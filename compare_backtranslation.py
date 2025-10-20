import json
import pandas as pd

def compare_backtranslation():
    # Load original data
    with open('Preprocessing/fetched_data.json', 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # Load back translation data
    with open('Preprocessing/result/fetched_data_final_checkpoint_500.json', 'r', encoding='utf-8') as f:
        backtranslated_data = json.load(f)
    
    # Create comparison dataframe
    comparison_df = pd.DataFrame({
        # only first 500 data
        'Original': [item['text'] for item in original_data[:500]],
        'Result': [item['text'] for item in backtranslated_data]
        # 'Result': backtranslated_data
    })
    
    # # Display the table
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', None)
    # pd.set_option('display.max_colwidth', 80)
    
    # print("=== ORIGINAL vs BACK TRANSLATION COMPARISON ===\n")
    
    # # Clean text for display (remove problematic characters)
    # display_df = comparison_df.copy()
    # display_df['Original'] = display_df['Original'].str.encode('ascii', errors='ignore').str.decode('ascii')
    # display_df['Back_Translation'] = display_df['Back_Translation'].str.encode('ascii', errors='ignore').str.decode('ascii')
    
    # print(display_df.head(20))  # Show first 20 rows
    
    # Save to Excel
    comparison_df.to_excel('rf_comparison.xlsx', index=False, engine='openpyxl')
    print(f"\nExcel file saved as 'backtranslation_comparison.xlsx' with {len(comparison_df)} rows")

    return comparison_df

if __name__ == "__main__":
    df = compare_backtranslation()