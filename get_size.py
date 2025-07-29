import os
import zipfile
import yaml
import shutil
from PIL import Image
from dotenv import load_dotenv

# .envファイルから設定を読み込み
load_dotenv()

MAX_IMAGE_HEIGHT = int(os.getenv('MAX_IMAGE_HEIGHT', '2000'))
ADD_MINI_NAME = os.getenv('ADD_MINI_NAME', '_mini')
FOLDER_ORIGINAL = os.getenv('FOLDER_ORIGINAL', 'zip_original')
FOLDER_MINIFY = os.getenv('FOLDER_MINIFY', 'zip_minify')
FOLDER_UNZIP = os.getenv('FOLDER_UNZIP', 'unzip_files')
SIZE_FILE = os.getenv('SIZE_FILE', 'size_list.yaml')

# 処理対象の画像拡張子
SUPPORTED_EXTENSIONS = ('.jpeg', '.jpg', '.png', '.webp', '.bmp', '.tiff', '.gif')

def handle_no_large_images(zip_path, extract_folder):
    """MAX_IMAGE_HEIGHT以上の画像がない場合の処理"""
    print(f"  No images >= {MAX_IMAGE_HEIGHT}px found. Moving to minify folder...")
    
    # FOLDER_MINIFYフォルダを作成（存在しない場合）
    if not os.path.exists(FOLDER_MINIFY):
        os.makedirs(FOLDER_MINIFY)
    
    # ファイル名に_miniを追加
    zip_filename = os.path.basename(zip_path)
    name_without_ext = os.path.splitext(zip_filename)[0]
    new_zip_name = f"{name_without_ext}{ADD_MINI_NAME}.zip"
    new_zip_path = os.path.join(FOLDER_MINIFY, new_zip_name)
    
    # ZIPファイルをFOLDER_MINIFYに移動
    shutil.move(zip_path, new_zip_path)
    print(f"  Moved to: {new_zip_path}")
    
    # 展開したフォルダを削除
    if os.path.exists(extract_folder):
        shutil.rmtree(extract_folder)
        print(f"  Removed extracted folder: {extract_folder}")

def get_image_sizes_from_zip(zip_path):
    """ZIPファイル内の画像の高さを取得"""
    base_name = os.path.splitext(os.path.basename(zip_path))[0]
    extract_folder = os.path.join(FOLDER_UNZIP, base_name)
    
    print(f"Processing: {os.path.basename(zip_path)}")
    
    # ZIPファイルを展開
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)
        print(f"  Extracting to: {extract_folder}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
    else:
        print(f"  Already extracted: {extract_folder}")
    
    # 画像の高さを収集（サイズごとの枚数もカウント）
    height_counts = {}  # {height: count} の辞書
    has_large_image = False  # MAX_IMAGE_HEIGHT以上の画像があるかチェック
    
    for root, _, files in os.walk(extract_folder):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                image_path = os.path.join(root, file)
                try:
                    with Image.open(image_path) as img:
                        height = img.height
                        height_counts[height] = height_counts.get(height, 0) + 1
                        if height >= MAX_IMAGE_HEIGHT:
                            has_large_image = True
                        print(f"    {file}: {height}px")
                except Exception as e:
                    print(f"    Could not process {file}: {e}")
    
    # MAX_IMAGE_HEIGHT以上の画像がない場合の処理
    if not has_large_image:
        handle_no_large_images(zip_path, extract_folder)
        return height_counts, has_large_image
    
    return height_counts, has_large_image

def main():
    """メイン処理"""
    if not os.path.isdir(FOLDER_ORIGINAL):
        print(f"Error: Source directory '{FOLDER_ORIGINAL}' not found.")
        return
    
    # ZIPファイルを取得してファイル名順にソート
    zip_files = [f for f in os.listdir(FOLDER_ORIGINAL) if f.lower().endswith('.zip')]
    zip_files.sort()  # ファイル名順にソート
    
    if not zip_files:
        print(f"No ZIP files found in '{FOLDER_ORIGINAL}' directory.")
        return
    
    # サイズ情報を収集
    size_data = {}
    
    for zip_file in zip_files:
        zip_path = os.path.join(FOLDER_ORIGINAL, zip_file)
        heights, has_large_image = get_image_sizes_from_zip(zip_path)
        if has_large_image is True:
            size_data[zip_file] = heights
        else:
            # MAX_IMAGE_HEIGHT以上の画像がない場合は==付きで記録
            size_data[f"=={zip_file}"] = heights
    
    # YAMLファイルに出力
    with open(SIZE_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(size_data, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\nSize list saved to: {SIZE_FILE}")
    print("Completed!")

if __name__ == "__main__":
    main()
