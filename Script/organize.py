import os
import shutil

# Get the absolute path of the raw data directory
project_root = os.path.dirname(os.path.abspath(__file__))  # current: Script/
raw_data_dir = os.path.abspath(os.path.join(project_root, '..', 'Dataset', 'Raw Data'))

# Map file extensions to their destination folders
extension_to_folder = {
    '.csv': 'CSV',
    '.json': 'JSON',
    '.xlsx': 'XLSX'
}

# Create folders if they don't exist
for folder in extension_to_folder.values():
    target_dir = os.path.join(raw_data_dir, folder)
    os.makedirs(target_dir, exist_ok=True)

# Loop through all files in Raw Data (non-recursive)
for file in os.listdir(raw_data_dir):
    file_path = os.path.join(raw_data_dir, file)

    # Skip directories (like CSV/, JSON/, etc.)
    if os.path.isdir(file_path):
        continue

    # Check file extension
    ext = os.path.splitext(file)[1].lower()
    if ext in extension_to_folder:
        target_folder = os.path.join(raw_data_dir, extension_to_folder[ext])
        dest_path = os.path.join(target_folder, file)

        # Avoid overwriting
        if not os.path.exists(dest_path):
            shutil.move(file_path, dest_path)
            print(f"Moved: {file} → {extension_to_folder[ext]}")
        else:
            print(f"Skipped (exists): {file}")
