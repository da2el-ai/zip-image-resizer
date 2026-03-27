#!/bin/bash

# venvディレクトリの存在をチェック
if [ ! -d "venv" ]; then
  echo "venvディレクトリを作成します。"
  python3 -m venv venv
  
  # venvを有効化
  source venv/bin/activate
  
  # 必要なモジュールをインストール（初回のみ）
  echo "必要なモジュールをインストールします..."
  pip install -r requirements.txt
else
  # venvを有効化
  source venv/bin/activate
fi

# Pythonスクリプトを実行
echo "get_size.py を実行します..."
python get_size.py

echo "完了しました。"
