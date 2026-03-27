@echo off
rem venvディレクトリの存在をチェック
if not exist venv (
  echo venvディレクトリを作成します。
  python -m venv venv
  
  rem venvを有効化
  call venv\Scripts\activate
  
  rem 必要なモジュールをインストール（初回のみ）
  echo 必要なモジュールをインストールします...
  pip install -r requirements.txt
) else (
  rem venvを有効化
  call venv\Scripts\activate
)

rem Pythonスクリプトを実行
echo archive_images.py を実行します...
python archive_images.py

echo 完了しました。
