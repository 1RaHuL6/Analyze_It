import json
import os

def split_json_file(filename, chunk_size=1000):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = len(data)
    for i in range(0, total, chunk_size):
        chunk = data[i:i+chunk_size]
        chunk_filename = f"{filename.split('.')[0]}_part_{i//chunk_size + 1}.json"
        with open(chunk_filename, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, indent=2)
        print(f"Created {chunk_filename} with {len(chunk)} records")

if __name__ == "__main__":
    split_json_file('attendance_clean.json', chunk_size=1000)