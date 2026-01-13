# 🎺 LilyPond楽譜プレビューツール

金管編曲のためのLilyPond楽譜作成・変換・プレビューツール

## 機能

- **LilyPond楽譜プレビュー**: コードを入力して即座にPDFとMIDI生成
- **MusicXML変換**: MusicXMLファイルをLilyPondに変換
- **日本語UI**: 親しみやすい日本語インターフェース
- **テンプレート**: トロンボーン三重奏、金管五重奏などのテンプレート

## 技術スタック

- **バックエンド**: Python FastAPI
- **フロントエンド**: HTML/CSS/JavaScript
- **楽譜生成**: LilyPond 2.24
- **変換**: musicxml2ly

## ローカル開発

### 必要な環境

- Python 3.10+
- LilyPond 2.24+

### セットアップ

```bash
# 依存関係をインストール
pip install -r requirements.txt

# サーバーを起動
python main.py
```

ブラウザで `http://localhost:8000` を開く

## Railwayデプロイ手順

### 1. Railwayアカウント作成

1. https://railway.app にアクセス
2. GitHubアカウントでサインアップ

### 2. プロジェクトをGitHubにプッシュ

```bash
# Gitリポジトリを初期化
git init
git add .
git commit -m "Initial commit"

# GitHubに新しいリポジトリを作成してプッシュ
git remote add origin https://github.com/YOUR_USERNAME/lilypond-preview-tool.git
git push -u origin main
```

### 3. Railwayでデプロイ

1. Railwayダッシュボードで **"New Project"** をクリック
2. **"Deploy from GitHub repo"** を選択
3. リポジトリを選択
4. 自動的にDockerfileを検出してビルド開始
5. デプロイ完了後、**"Settings"** → **"Generate Domain"** でURLを取得

### 4. 環境変数（オプション）

必要に応じて環境変数を設定：

- `PORT`: ポート番号（デフォルト: 8000）

## 使い方

### LilyPond楽譜作成

1. 「LilyPond楽譜作成」タブを開く
2. テンプレートを選択、またはコードを入力
3. 「楽譜にする」ボタンをクリック
4. PDFプレビューとMIDI再生が表示される

### MusicXML変換

1. 「MusicXML変換」タブを開く
2. MusicXMLファイル（.xml, .musicxml, .mxl）をアップロード
3. 変換されたLilyPondコードが表示される
4. 「エディタにコピー」で編集可能
5. 「プレビュー」で楽譜を確認

## API エンドポイント

### `POST /render`

LilyPondコードをレンダリング

```json
{
  "code": "\\version \"2.24.0\"\n{ c' d' e' }",
  "format": "pdf"
}
```

### `POST /convert/xml2ly`

MusicXMLをLilyPondに変換

```bash
curl -X POST -F "file=@score.xml" http://localhost:8000/convert/xml2ly
```

### `GET /health`

ヘルスチェック

## トラブルシューティング

### LilyPondがインストールされていない

Dockerfileで自動的にインストールされます。

### Railwayでビルドが失敗する

- Dockerfileが正しいか確認
- ログを確認して依存関係エラーをチェック

### MIDIが再生されない

- ブラウザがMIDI再生に対応していない可能性
- PDFプレビューは正常に動作します

## 今後の追加予定機能

- [ ] LilyPond → MusicXML変換（実験的）
- [ ] 楽譜の保存・共有機能
- [ ] AI編曲アシスタント統合
- [ ] ファゴット編成対応
- [ ] テンプレートライブラリ拡充

## ライセンス

MIT License

## 作者

Fuki - 金管編曲スペシャリスト

---

**開発ステータス**: Phase 1 - 開発用プレビューツール ✅
