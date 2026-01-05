import json
import os

def compare_and_merge_json(original_json_path, new_json_path, output_json_path, label_key='votes', original_label_key='label'):
    """
    Compare two JSON files and merge labels from new JSON into original JSON
    
    Args:
        original_json_path (str): Path to original JSON file
        new_json_path (str): Path to new JSON file with updated labels
        output_json_path (str): Path to output merged JSON file
        label_key (str): Key name for labels in new JSON (default: 'votes')
        original_label_key (str): Key name for labels in original JSON (default: 'label')
    """
    
    try:
        # Load original JSON
        with open(original_json_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # Load new JSON with updated labels
        with open(new_json_path, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
        
        print(f"Original data: {len(original_data)} records")
        print(f"New data: {len(new_data)} records")
        
        # Check if lengths match
        min_length = min(len(original_data), len(new_data))
        if len(original_data) != len(new_data):
            print(f"Warning: Different lengths. Using first {min_length} records.")
        
        # Compare and count differences
        differences = 0
        merged_data = []
        
        for i in range(min_length):
            # Copy original record
            merged_record = original_data[i].copy()
            
            # Get labels for comparison
            original_label = original_data[i].get(original_label_key)
            new_label = new_data[i].get(label_key)
            
            # Convert boolean to int if needed
            if isinstance(new_label, bool):
                new_label = int(new_label)
            if isinstance(original_label, bool):
                original_label = int(original_label)
            
            # Count differences
            if original_label != new_label:
                differences += 1
            
            # Update label in merged record
            merged_record[original_label_key] = new_label
            merged_data.append(merged_record)
        
        # Save merged data
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        # Print results
        print(f"\nComparison Results:")
        print(f"Total records processed: {min_length}")
        print(f"Different labels: {differences}")
        print(f"Same labels: {min_length - differences}")
        print(f"Difference percentage: {(differences/min_length)*100:.2f}%")
        print(f"\nMerged data saved to: {output_json_path}")
        
        return output_json_path, differences
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return None, 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, 0

if __name__ == "__main__":
    # File paths
    original_file = "../Preprocessing/result_BERT_BT/fetched_data_final.json"  # Change this to your original JSON file path
    new_file = "./fetched_data_from_excel.json"  # Your new JSON with updated labels
    output_file = "./final_data/final_BT_BERT.json"
    
    # Check if files exist
    if not os.path.exists(original_file):
        print(f"Original file not found: {original_file}")
        print("Please update the 'original_file' path in the script")
    elif not os.path.exists(new_file):
        print(f"New file not found: {new_file}")
    else:
        # Compare and merge
        result, diff_count = compare_and_merge_json(
            original_file, 
            new_file, 
            output_file,
            label_key='votes',  # Key in your new JSON
            original_label_key='label'  # Key in your original JSON
        )
        
        if result:
            print(f"\nProcess completed successfully!")
            print(f"Output file: {result}")