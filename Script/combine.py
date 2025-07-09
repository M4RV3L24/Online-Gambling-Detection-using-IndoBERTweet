import os
import json

input_folder = '../Dataset/Filterred Data'
output_folder = '../Dataset/Combined Data'
output_file = os.path.join(output_folder, 'combined3.json')

os.makedirs(output_folder, exist_ok=True)

combined_data = []
seen_texts = set()

for filename in os.listdir(input_folder):
    if filename.endswith('.json'):
        file_path = os.path.join(input_folder, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        text = item.get('text')
                        if text and text not in seen_texts:
                            combined_data.append(item)
                            seen_texts.add(text)
                else:
                    text = data.get('text')
                    if text and text not in seen_texts:
                        combined_data.append(data)
                        seen_texts.add(text)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, ensure_ascii=False, indent=2)

print(f"Combined {len(combined_data)} unique items into {output_file}")