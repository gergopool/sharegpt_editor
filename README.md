# ShareGPT Editor: LLM Training Data Generator

A web application for easily creating, editing, and exporting conversation data in ShareGPT format for LLM fine-tuning.

## Features

- **Interactive Web UI**: Create and manage conversations with user, assistant, and system messages
- **Message Management**: Edit, delete, reorder, and change roles of messages
- **Drag & Drop Interface**: Easily reorder messages in conversations
- **Data Processing**: Generate training examples that end with assistant responses
- **Export Options**: Export individual conversations or all data at once

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/gergopool/sharegpt_editor.git
   cd sharegpt_editor
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Web Application

1. Start the web application:
   ```
   python app.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:5000`

### Chunking Data for Training

Generate training examples from your conversations:

```
python chunk_conversations.py
```

Parameters:
- `--input-dir`: Directory containing JSON conversation files (default: "conversations")
- `--output-dir`: Directory to save training chunks (default: "training_examples")
- `--system-prompt`: File containing system prompt to add to all conversations (default: "system_prompt.txt")

## Data Format

ShareGPT Editor works with conversation data in this format:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello, how are you?"
    },
    {
      "role": "assistant",
      "content": "I'm doing well, thank you for asking. How can I help you today?"
    }
  ]
}
```

When chunking for training data, each chunk will:
1. Include a system prompt (if provided)
2. Contain conversation context up to an assistant response
3. Always end with an assistant message

## License

MIT