import json
import os

def convert_back_translation():
    """
    Convert fetched_data_back_translation.json to match the format of fetched_data.json
    with text and votes attributes
    """
    
    # File paths
    back_translation_file = "../Preprocessing/result_RF2/fetched_data_back_translation.json"
    original_file = "../Preprocessing/fetched_data.json"
    output_file = "../Preprocessing/result_RF2/fetched_data_back_translation_formatted.json"
    
    try:
        # Read back translation data (array of strings)
        with open(back_translation_file, 'r', encoding='utf-8') as f:
            back_translation_data = json.load(f)
        
        # Read original data to get votes
        with open(original_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # Check if both files have same number of records
        if len(back_translation_data) != len(original_data):
            print(f"Warning: Different number of records!")
            print(f"Back translation: {len(back_translation_data)}")
            print(f"Original: {len(original_data)}")
            return None
        
        # Convert to same format as original
        formatted_data = []
        for i, text in enumerate(back_translation_data):
            formatted_record = {
                "text": text,
                "votes": original_data[i]["votes"]
            }
            formatted_data.append(formatted_record)
        
        # Write formatted data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully converted {len(formatted_data)} records")
        print(f"Output saved to: {output_file}")
        
        return output_file
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = convert_back_translation()
    if result:
        print(f"\nConversion completed successfully!")
        print(f"Output file: {result}")