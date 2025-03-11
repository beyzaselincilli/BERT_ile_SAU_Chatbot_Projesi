import json
import os

def load_chunks(chatbot_folder):
    jsonl_path = os.path.join(chatbot_folder, "chatbot_dataset.jsonl")
    with open(jsonl_path, "r", encoding="utf-8") as f:
        chunks = [json.loads(line.strip()) for line in f]
    return chunks
