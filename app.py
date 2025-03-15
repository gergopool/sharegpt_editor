from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# Ensure data directory exists
DATA_DIR = 'conversations'
os.makedirs(DATA_DIR, exist_ok=True)


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get list of saved conversations"""
    conversations = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                conversations.append({
                    'id': data.get('id', filename.replace('.json', '')),
                    'timestamp': data.get('timestamp', ''),
                    'messageCount': len(data.get('messages', []))
                })

    # Sort by timestamp (newest first)
    conversations.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(conversations)


@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation"""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'Conversation not found'}), 404


@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation"""
    conversation_id = str(uuid.uuid4())
    conversation = {'id': conversation_id, 'timestamp': datetime.now().isoformat(), 'messages': []}

    # Save to file
    with open(os.path.join(DATA_DIR, f"{conversation_id}.json"), 'w') as f:
        json.dump(conversation, f, indent=2)

    return jsonify(conversation)


@app.route('/api/conversations/<conversation_id>', methods=['PUT'])
def update_conversation(conversation_id):
    """Update an existing conversation"""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Conversation not found'}), 404

    data = request.json
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    return jsonify(data)


@app.route('/api/conversations/<conversation_id>/message', methods=['POST'])
def add_message(conversation_id):
    """Add a message to a conversation"""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Conversation not found'}), 404

    with open(filepath, 'r') as f:
        conversation = json.load(f)

    data = request.json
    role = data.get('role', 'user')  # default to user if not specified
    content = data.get('content', '')

    # Automatically detect and format JSON if content starts with '{'
    is_json = False
    if isinstance(content, str) and content.strip().startswith('{'):
        try:
            content_obj = json.loads(content)
            content = json.dumps(content_obj, indent=2)
            is_json = True
        except json.JSONDecodeError:
            # If invalid JSON, keep as is
            pass

    message = {'role': role, 'content': content}

    conversation['messages'].append(message)
    conversation['timestamp'] = datetime.now().isoformat()

    with open(filepath, 'w') as f:
        json.dump(conversation, f, indent=2)

    return jsonify(conversation)


@app.route('/api/conversations/<conversation_id>/message/<int:message_index>', methods=['PUT'])
def update_message(conversation_id, message_index):
    """Update a specific message in a conversation"""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Conversation not found'}), 404

    with open(filepath, 'r') as f:
        conversation = json.load(f)
    
    messages = conversation.get('messages', [])
    
    if message_index < 0 or message_index >= len(messages):
        return jsonify({'error': 'Message index out of range'}), 400
    
    data = request.json
    role = data.get('role')
    content = data.get('content')
    
    if role:
        messages[message_index]['role'] = role
    
    if content is not None:
        messages[message_index]['content'] = content
    
    conversation['timestamp'] = datetime.now().isoformat()
    
    with open(filepath, 'w') as f:
        json.dump(conversation, f, indent=2)
    
    return jsonify(conversation)


@app.route('/api/conversations/<conversation_id>/message/<int:message_index>', methods=['DELETE'])
def delete_message(conversation_id, message_index):
    """Delete a specific message from a conversation"""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Conversation not found'}), 404

    with open(filepath, 'r') as f:
        conversation = json.load(f)
    
    messages = conversation.get('messages', [])
    
    if message_index < 0 or message_index >= len(messages):
        return jsonify({'error': 'Message index out of range'}), 400
    
    # Remove the message at the specified index
    del messages[message_index]
    conversation['timestamp'] = datetime.now().isoformat()
    
    with open(filepath, 'w') as f:
        json.dump(conversation, f, indent=2)
    
    return jsonify(conversation)


@app.route('/api/conversations/<conversation_id>/message/<int:message_index>/after', methods=['POST'])
def add_message_after(conversation_id, message_index):
    """Add a message after a specific message in a conversation"""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Conversation not found'}), 404

    with open(filepath, 'r') as f:
        conversation = json.load(f)
    
    messages = conversation.get('messages', [])
    
    if message_index < 0 or message_index >= len(messages):
        return jsonify({'error': 'Message index out of range'}), 400
    
    data = request.json
    role = data.get('role', 'user')  # default to user if not specified
    content = data.get('content', '')
    
    message = {'role': role, 'content': content}
    
    # Insert the new message after the specified index
    messages.insert(message_index + 1, message)
    conversation['timestamp'] = datetime.now().isoformat()
    
    with open(filepath, 'w') as f:
        json.dump(conversation, f, indent=2)
    
    return jsonify(conversation)


@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'success': True})
    return jsonify({'error': 'Conversation not found'}), 404


@app.route('/api/export/<conversation_id>', methods=['GET'])
def export_conversation(conversation_id):
    """Export a conversation in ShareGPT format"""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Conversation not found'}), 404

    return send_file(filepath, as_attachment=True, download_name=f"sharegpt_{conversation_id}.json")


@app.route('/api/export-all', methods=['GET'])
def export_all_conversations():
    """Export all conversations as a single file"""
    all_messages = []

    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                all_messages.append({'messages': data['messages']})

    export_data = {'conversations': all_messages}

    # Save to a temporary file
    export_path = 'export_all.json'
    with open(export_path, 'w') as f:
        json.dump(export_data, f, indent=2)

    return send_file(export_path,
                     as_attachment=True,
                     download_name=f"sharegpt_all_{datetime.now().strftime('%Y%m%d')}.json")


if __name__ == '__main__':
    app.run(debug=True)
