import csv
import json

def csv_to_json(csv_file, json_file):
    data = []
    seen_texts = set()
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            text = row['komentar']
            if text not in seen_texts:
                seen_texts.add(text)
                data.append({
                    'text': text,
                    'label': bool(int(row['label']))
                })
    
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    
    print(f"Converted {len(data)} rows from {csv_file} to {json_file}")

if __name__ == "__main__":
    csv_to_json('komentar_youtube_1.csv', 'komentar_youtube_1.json')