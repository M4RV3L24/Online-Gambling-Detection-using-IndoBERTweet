import pandas as pd
import json
import os

def xlsx_to_json(xlsx_file_path, json_file_path=None, include_columns=None):
    """
    Convert Excel (XLSX) file back to JSON format
    
    Args:
        xlsx_file_path (str): Path to the input XLSX file
        json_file_path (str): Path to the output JSON file (optional)
        include_columns (list): List of column names to include (optional, includes all if None)
    """
    
    # Generate output filename if not provided
    if json_file_path is None:
        base_name = os.path.splitext(xlsx_file_path)[0]
        json_file_path = f"{base_name}_converted.json"
    
    try:
        # Read Excel file
        df = pd.read_excel(xlsx_file_path, engine='openpyxl')
        
        # Filter columns if specified
        if include_columns:
            available_columns = [col for col in include_columns if col in df.columns]
            missing_columns = [col for col in include_columns if col not in df.columns]
            
            if missing_columns:
                print(f"Warning: Columns not found: {missing_columns}")
            
            if available_columns:
                df = df[available_columns]
                print(f"Including columns: {available_columns}")
            else:
                print("Error: None of the specified columns found in the file")
                return None
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        
        # Write to JSON file
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully converted {xlsx_file_path} to {json_file_path}")
        print(f"Total records: {len(data)}")
        print(f"Columns: {list(df.columns)}")
        
        return json_file_path
        
    except FileNotFoundError:
        print(f"Error: File {xlsx_file_path} not found")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Convert the Excel file back to JSON
    input_file = "./data excel/justified_data.xlsx"
    output_file = "fetched_data_from_excel.json"
    
    # Specify which columns to include (set to None to include all columns)
    columns_to_include = ['votes']  # Adjust this list as needed
    # columns_to_include = None  # Uncomment this to include all columns
    
    # Check if input file exists
    if os.path.exists(input_file):
        result = xlsx_to_json(input_file, output_file, columns_to_include)
        if result:
            print(f"\nConversion completed successfully!")
            print(f"Output file: {result}")
    else:
        print(f"Input file not found: {input_file}")
        print("Please make sure the fetched_data.xlsx file exists in the Preprocessing folder.")