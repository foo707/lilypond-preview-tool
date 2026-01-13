FROM ubuntu:24.04

# 環境変数設定
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    lilypond \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ作成
WORKDIR /app

# Python依存関係をインストール
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# アプリケーションファイルをコピー
COPY main.py .
COPY index.html .

# ポート公開
EXPOSE 8000

# アプリケーション起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
