# -*- coding: utf-8 -*-
"""
SmartAgri Project Packaging Script
Creates a clean, portable .ZIP archive ready for submission and evaluation.
"""
import os
import zipfile
import time

def create_project_zip(include_raw_datasets=False):
    zip_name = 'SmartAgri_Major_Project.zip'
    
    # Remove existing zip if any
    if os.path.exists(zip_name):
        try:
            os.remove(zip_name)
        except Exception:
            pass

    exclude_dirs = {
        '.venv', 'venv', 'env', '__pycache__', '.git', '.idea', 
        '.vscode', '.gemini', 'flask_sessions', 'scratch', 'node_modules'
    }
    
    if not include_raw_datasets:
        exclude_dirs.add('Datasets')
        exclude_dirs.add('smartagri-react')

    exclude_exts = {'.pyc', '.pyo', '.pyd', '.zip', '.log'}

    print("=" * 60)
    print(f"[+] Starting packaging for: {zip_name}")
    print(f"[*] Excluding temporary/heavy folders: {', '.join(exclude_dirs)}")
    print("=" * 60)

    start_time = time.time()
    file_count = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk('.'):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            for file in files:
                if any(file.endswith(ext) for ext in exclude_exts):
                    continue
                if file == zip_name or file.startswith('.'):
                    # allow .env.example
                    if file not in ['.env.example', '.gitignore']:
                        continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                
                try:
                    fsize = os.path.getsize(file_path)
                    zipf.write(file_path, arcname)
                    file_count += 1
                    total_uncompressed_bytes += fsize
                    if file_count % 25 == 0:
                        print(f"  -> Added {file_count} files ({arcname})...")
                except Exception as e:
                    print(f"  [-] Skipping {file_path}: {e}")

    zip_size_mb = os.path.getsize(zip_name) / (1024 * 1024)
    elapsed = time.time() - start_time

    print("=" * 60)
    print(f"[OK] SUCCESS! Created '{zip_name}'")
    print(f"[*] Total Files Included : {file_count}")
    print(f"[*] Final Archive Size   : {zip_size_mb:.2f} MB")
    print(f"[*] Time Taken           : {elapsed:.1f} seconds")
    print(f"[*] Location             : {os.path.abspath(zip_name)}")
    print("=" * 60)

if __name__ == '__main__':
    create_project_zip(include_raw_datasets=False)
