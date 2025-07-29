# ZIP画像リサイズツール

このツールは、ZIPファイルに含まれる画像を特定の高さにリサイズし、新しいZIPファイルとして保存するPythonスクリプトです。

## 概要

このツールは2つのスクリプトで構成されています。

1.  `get_size.py`: ZIP内の画像サイズを調査し、リサイズが必要かどうかを判断します。
2.  `archive_images.py`: 画像を実際にリサイズし、新しいZIPファイルを作成します。

## インストール方法

### 1. 仮想環境の作成

このスクリプトは仮想環境(venv)での実行を推奨します。

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windowsの場合
# venv\Scripts\activate
# macOS/Linuxの場合
source venv/bin/activate
```

### 2. 必要なライブラリのインストール

`requirements.txt` を使って、必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

## 設定

スクリプトの動作は `.env` ファイルで設定します。プロジェクトのルートに `.env` ファイルを作成し、以下の内容を参考に設定してください。

```dotenv
# 縮小対象とする画像の高さ（これ以上の高さの画像がリサイズ対象）
MAX_IMAGE_HEIGHT=2500

# 縮小後の画像の高さ
RESIZE_IMAGE_HEIGHT=2250

# JPEG画像の品質 (1-100)
JPEG_QUALITY=90

# 縮小版のファイル名に付ける接尾辞
ADD_MINI_NAME=_mini

# オリジナルのZIPファイルを置くフォルダ
FOLDER_ORIGINAL=data/zip_original

# 処理後のZIPファイルを保存するフォルダ
FOLDER_MINIFY=data/zip_minify

# ZIPファイルを展開する作業用フォルダ
FOLDER_UNZIP=data/unzip_files

# 画像サイズの一覧を保存するYAMLファイル
SIZE_FILE=data/size_list.yaml
```

## 使い方

### ステップ1: 画像サイズ一覧の作成 (`get_size.py`)

1.  リサイズしたいZIPファイルを `data/zip_original/` フォルダに置きます。
2.  以下のコマンドを実行します。

    ```bash
    python get_size.py
    ```

3.  実行後、以下の処理が行われます。
    *   ZIPファイルが `data/unzip_files/` に展開されます。
    *   画像の高さと枚数の一覧が `data/size_list.yaml` に出力されます。
    *   もし、ZIP内の全ての画像の高さが `MAX_IMAGE_HEIGHT` 未満だった場合、そのZIPファイルはリサイズ不要と判断され、`_mini` という接尾辞が付いて `data/zip_minify/` に直接移動されます。

### ステップ2: 画像のリサイズと再圧縮 (`archive_images.py`)

1.  以下のコマンドを実行します。

    ```bash
    python archive_images.py
    ```

2.  実行後、以下の処理が行われます。
    *   `data/zip_original/` にあるZIPファイル、または `data/unzip_files/` にある展開済みフォルダが処理対象となります。
    *   `MAX_IMAGE_HEIGHT` 以上の高さの画像が `RESIZE_IMAGE_HEIGHT` の高さにリサイズされます。
    *   リサイズされた画像を含む新しいZIPファイルが、`_mini` という接尾辞付きで `data/zip_minify/` に作成されます。
