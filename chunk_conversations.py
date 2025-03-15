import json
import os
import argparse
from pathlib import Path
import glob


def chunk_conversations(input_dir, output_dir, system_prompt_file=None):
    """
    Process all JSON files in the input directory, 
    add system prompt to each conversation, and
    split conversations into smaller chunks for training examples.
    Each chunk ends with a user message.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load system prompt if provided
    system_prompt = None
    if system_prompt_file and os.path.exists(system_prompt_file):
        with open(system_prompt_file, 'r') as f:
            system_prompt = f.read().strip()

    # Find all JSON files in the input directory
    json_files = glob.glob(os.path.join(input_dir, "*.json"))

    # Process each file
    all_chunks = []
    file_count = 0

    for input_file in json_files:
        file_count += 1
        print(f"Processing file {file_count}/{len(json_files)}: {os.path.basename(input_file)}")

        # Load the data
        with open(input_file, 'r') as f:
            data = json.load(f)

        # Handle both single conversation format and exported format with "conversations" key
        if "messages" in data:
            # Single conversation format
            messages = data.get("messages", [])
            process_messages(messages, system_prompt, all_chunks)
        elif "conversations" in data:
            # Exported format with multiple conversations
            conversations = data.get("conversations", [])
            for conversation in conversations:
                messages = conversation.get("messages", [])
                process_messages(messages, system_prompt, all_chunks)

    # Save all chunks to separate files
    for chunk_idx, chunk in enumerate(all_chunks):
        chunk_data = {"messages": chunk}

        output_file = Path(output_dir) / f"chunk_{chunk_idx}.json"
        with open(output_file, 'w') as f:
            json.dump(chunk_data, f, indent=2)

    print(f"Processed {file_count} files")
    print(f"Created {len(all_chunks)} training examples")


def process_messages(messages, system_prompt, all_chunks):
    """Process a single message list into chunks"""
    # Skip empty conversations
    if not messages:
        return

    # Find all assistant messages
    assistant_indices = [i for i, msg in enumerate(messages) if msg['role'] == 'assistant']

    # For each assistant message, create a chunk ending with that assistant message
    for assistant_idx in assistant_indices:
        # Create a new chunk
        chunk = []

        # Add system prompt if provided
        if system_prompt:
            chunk.append({"role": "system", "content": system_prompt})

        # Find all messages that precede this assistant message
        # This includes any preceding user messages and other context
        for j in range(assistant_idx + 1):
            chunk.append(messages[j])

        # Only include chunks that contain at least a user message and an assistant response
        # (or system prompt + user message + response)
        min_length = 3 if system_prompt else 2

        # Also ensure the chunk ends with an assistant message
        if len(chunk) >= min_length and chunk[-1]['role'] == 'assistant':
            all_chunks.append(chunk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process conversations and split into training chunks")
    parser.add_argument("--input-dir",
                        default="conversations",
                        help="Input directory containing JSON files")
    parser.add_argument("--output-dir",
                        default="training_examples",
                        help="Output directory for chunks")
    parser.add_argument("--system-prompt",
                        help="File containing the system prompt to add to all conversations",
                        default="system_prompt.txt")

    args = parser.parse_args()
    chunk_conversations(args.input_dir, args.output_dir, args.system_prompt)
