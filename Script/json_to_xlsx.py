import json
import pandas as pd
import os
import xlsxwriter

def json_to_xlsx(json_file_path, xlsx_file_path=None):
    """
    Convert JSON file to Excel (XLSX) format while preserving text formatting
    
    Args:
        json_file_path (str): Path to the input JSON file
        xlsx_file_path (str): Path to the output XLSX file (optional)
    """
    
    # Generate output filename if not provided
    if xlsx_file_path is None:
        base_name = os.path.splitext(json_file_path)[0]
        xlsx_file_path = f"{base_name}.xlsx"
    
    try:
        # Read JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Clean data to prevent corruption
        # Replace problematic characters that might cause Excel issues
        df_clean = df.copy()
        
        # Clean text column if it exists
        # if 'text' in df_clean.columns:
        #     df_clean['text'] = df_clean['text'].astype(str)
        #     # Remove null bytes and other problematic characters
        #     df_clean['text'] = df_clean['text'].str.replace('\x00', '', regex=False)
        #     df_clean['text'] = df_clean['text'].str.replace('\ufeff', '', regex=False)
        
        # Write to Excel using xlsxwriter engine (better Unicode support)
        df.to_excel(xlsx_file_path, index=False, engine='xlsxwriter')
        
        print(f"Successfully converted {json_file_path} to {xlsx_file_path}")
        print(f"Total records: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        return xlsx_file_path
        
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Convert the fetched_data.json file
    input_file = "../Preprocessing/fetched_data.json"
    output_file = "../Preprocessing/fetched_data3.xlsx"
    
    # Check if input file exists
    if os.path.exists(input_file):
        result = json_to_xlsx(input_file, output_file)
        if result:
            print(f"\nConversion completed successfully!")
            print(f"Output file: {result}")
    else:
        print(f"Input file not found: {input_file}")
        print("Please make sure the fetched_data.json file exists in the Preprocessing folder.")