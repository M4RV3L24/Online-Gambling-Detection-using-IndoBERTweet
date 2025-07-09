# read json file and count the number of entries

import json
def count_entries(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return len(data)

# only unique entries
def count_unique_entries(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        unique_entries = set(tuple(entry.items()) for entry in data)
        return len(unique_entries)  
    
if __name__ == "__main__":
    file_path = 'combine.json'  # replace with your file path
    total_count = count_entries(file_path)
    unique_count = count_unique_entries(file_path)
    
    print(f"Total entries: {total_count}")
    print(f"Unique entries: {unique_count}")