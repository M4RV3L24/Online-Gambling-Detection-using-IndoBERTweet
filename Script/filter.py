import json

# Path to the specific JSON file
json_file = r'D:\laragon\www\Skripsi\Dataset\Raw Data\JSON\dataset_facebook-post-comments-scraper_2025-06-22_14-24-12-580.json'
output_file = r'D:\laragon\www\Skripsi\Dataset\Filterred Data\filterred_2025-06-22_14-24-12-580.json'

def extract_comment_text(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [{"text":item['commentText']} for item in data if 'commentText' in item]

def move_comment_text_to_new_json(json_file, output_file):
    comments = extract_comment_text(json_file)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    move_comment_text_to_new_json(json_file, output_file)
