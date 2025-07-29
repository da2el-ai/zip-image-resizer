import os
import zipfile
from PIL import Image
from dotenv import load_dotenv

# .envファイルから設定を読み込み
load_dotenv()

# 設定値を.envから取得
MAX_IMAGE_HEIGHT = int(os.getenv('MAX_IMAGE_HEIGHT', '2500'))
RESIZE_IMAGE_HEIGHT = int(os.getenv('RESIZE_IMAGE_HEIGHT', '2250'))
JPEG_QUALITY = int(os.getenv('JPEG_QUALITY', '90'))
ADD_MINI_NAME = os.getenv('ADD_MINI_NAME', '_mini')

FOLDER_ORIGINAL = os.getenv('FOLDER_ORIGINAL', 'zip_original')
FOLDER_MINIFY = os.getenv('FOLDER_MINIFY', 'zip_minify')
FOLDER_UNZIP = os.getenv('FOLDER_UNZIP', 'unzip_files')

# 処理対象の画像拡張子
SUPPORTED_EXTENSIONS = ('.jpeg', '.jpg', '.png', '.webp', '.bmp', '.tiff', '.gif')

def process_images_in_folder(extract_folder, base_name):
    """指定されたフォルダ内の画像を処理する"""
    print(f"\nProcessing folder: {base_name}")
    
    # 展開したフォルダ内の画像を処理
    resized_count = 0
    for root, _, files in os.walk(extract_folder):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                image_path = os.path.join(root, file)
                try:
                    with Image.open(image_path) as img:
                        # 条件（高さがMAX_IMAGE_HEIGHT以上）をチェック
                        if img.height >= MAX_IMAGE_HEIGHT:
                            print(f"  Resizing: {file} ({img.height}px -> {RESIZE_IMAGE_HEIGHT}px)")
                            
                            # アスペクト比を維持してリサイズ
                            ratio = RESIZE_IMAGE_HEIGHT / float(img.height)
                            new_width = int(float(img.width) * float(ratio))
                            resized_img = img.resize((new_width, RESIZE_IMAGE_HEIGHT), Image.Resampling.LANCZOS)

                            # PNGの透過チャンネルなどを考慮してRGBに変換
                            if resized_img.mode in ('RGBA', 'P'):
                                resized_img = resized_img.convert('RGB')

                            # 新しいファイルパス (拡張子を.jpgに)
                            new_image_path = os.path.splitext(image_path)[0] + '.jpg'
                            
                            # JPEGとして保存
                            resized_img.save(new_image_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)

                            # 元のファイルが新しいファイルと違う場合（例：PNG→JPG）、元のファイルを削除
                            if image_path != new_image_path:
                                os.remove(image_path)
                            
                            resized_count += 1

                except Exception as e:
                    print(f"  Could not process image {file}: {e}")

    # 新しいZIPファイルを作成
    new_zip_name = f"{base_name}{ADD_MINI_NAME}.zip"
    new_zip_path = os.path.join(FOLDER_MINIFY, new_zip_name)

    print(f"  Creating new zip: {new_zip_path}")
    print(f"  Resized images: {resized_count}")
    
    with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
        for root, _, files in os.walk(extract_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # ZIP内のパスを相対パスにする
                arcname = os.path.relpath(file_path, start=extract_folder)
                new_zip.write(file_path, arcname)

def process_images_in_zip_target(target):
    """処理対象に基づいて画像を処理する"""
    zip_file = target['zip_file']
    zip_path = target['zip_path']
    extract_folder = target['extract_folder']
    has_zip = target['has_zip']
    has_folder = target['has_folder']
    
    base_name = os.path.splitext(zip_file)[0]
    
    print(f"\nProcessing: {zip_file}")
    
    # ZIPファイルが存在する場合は展開
    if has_zip and not has_folder:
        if not os.path.exists(extract_folder):
            os.makedirs(extract_folder)
            print(f"  Extracting to: {extract_folder}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
        else:
            print(f"  Already extracted: {extract_folder}")
    elif has_folder:
        print(f"  Using existing folder: {extract_folder}")
    else:
        print(f"  Error: Neither ZIP file nor folder exists for {zip_file}")
        return
    
    # フォルダ内の画像を処理
    process_images_in_folder(extract_folder, base_name)

def get_processing_targets():
    """処理対象となるzipファイルと解凍済みフォルダのリストを作成"""
    targets = []
    
    # FOLDER_ORIGINALに存在するzipファイルを取得
    original_zips = set()
    if os.path.isdir(FOLDER_ORIGINAL):
        original_zips = {f for f in os.listdir(FOLDER_ORIGINAL) if f.lower().endswith('.zip')}
    
    # FOLDER_UNZIPに存在する解凍済みフォルダを取得
    unzipped_folders = set()
    if os.path.isdir(FOLDER_UNZIP):
        unzipped_folders = {f for f in os.listdir(FOLDER_UNZIP) if os.path.isdir(os.path.join(FOLDER_UNZIP, f))}
    
    # 処理対象を決定
    for zip_file in original_zips:
        zip_path = os.path.join(FOLDER_ORIGINAL, zip_file)
        base_name = os.path.splitext(zip_file)[0]
        extract_folder = os.path.join(FOLDER_UNZIP, base_name)
        targets.append({
            'zip_file': zip_file,
            'zip_path': zip_path,
            'extract_folder': extract_folder,
            'has_zip': True,
            'has_folder': base_name in unzipped_folders
        })
    
    # zipファイルは存在しないが、解凍済みフォルダが存在するものを追加
    for folder_name in unzipped_folders:
        zip_file = f"{folder_name}.zip"
        if zip_file not in original_zips:
            zip_path = os.path.join(FOLDER_ORIGINAL, zip_file)
            extract_folder = os.path.join(FOLDER_UNZIP, folder_name)
            targets.append({
                'zip_file': zip_file,
                'zip_path': zip_path,
                'extract_folder': extract_folder,
                'has_zip': False,
                'has_folder': True
            })
    
    return targets

def main():
    """メイン処理"""
    # 出力フォルダを作成
    if not os.path.exists(FOLDER_MINIFY):
        os.makedirs(FOLDER_MINIFY)
        print(f"Created output directory: {FOLDER_MINIFY}")

    if not os.path.exists(FOLDER_UNZIP):
        os.makedirs(FOLDER_UNZIP)
        print(f"Created unzip directory: {FOLDER_UNZIP}")

    # 処理対象を取得
    targets = get_processing_targets()
    
    if not targets:
        print(f"No processing targets found.")
        print(f"  - No ZIP files in '{FOLDER_ORIGINAL}' directory.")
        print(f"  - No extracted folders in '{FOLDER_UNZIP}' directory.")
        return

    print(f"Found {len(targets)} targets to process.")
    print(f"Settings:")
    print(f"  MAX_IMAGE_HEIGHT: {MAX_IMAGE_HEIGHT}px")
    print(f"  RESIZE_IMAGE_HEIGHT: {RESIZE_IMAGE_HEIGHT}px")
    print(f"  JPEG_QUALITY: {JPEG_QUALITY}")
    
    # 処理対象の詳細を表示
    for target in targets:
        status = []
        if target['has_zip']:
            status.append("ZIP")
        if target['has_folder']:
            status.append("FOLDER")
        print(f"  - {target['zip_file']} ({', '.join(status)})")

    for target in targets:
        process_images_in_zip_target(target)
    
    print("\n\nAll tasks completed.")

if __name__ == "__main__":
    main()
