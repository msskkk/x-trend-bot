# X投資トレンド自動投稿Bot 🤖📈

日本の投資系トレンドを1時間ごとに自動取得・投稿するTwitter Botです。  
GitHub Actionsで完全自動化されており、サーバー不要で動作します。

## ✨ 機能

- 📊 日本のXトレンドをリアルタイム取得
- 💰 投資・金融関連キーワードで自動フィルタリング
- 📝 魅力的な投稿文を自動生成
- 🤖 1時間ごとに自動投稿（GitHub Actions）
- 📝 詳細なログ記録
- 🛡️ エラーハンドリング完備

## 🎯 投資系キーワード

以下のカテゴリーのトレンドを自動検出します：

- **株式・市場**: 日経、TOPIX、IPO、決算など
- **仮想通貨**: ビットコイン、イーサリアム、NFTなど
- **FX・為替**: ドル円、円安、FXなど
- **経済指標**: 金利、GDP、インフレなど
- **投資一般**: NISA、iDeCo、資産運用など

## 🚀 セットアップ手順

### 1. リポジトリの準備

#### ローカルで準備する場合
```bash
# リポジトリをクローン
git clone https://github.com/your-username/x-trend-bot.git
cd x-trend-bot

# 依存関係をインストール
pip install -r requirements.txt
```

#### GitHubに直接アップロードする場合
1. GitHubで新しいリポジトリを作成（例: `x-trend-bot`）
2. このフォルダの全ファイルをアップロード

### 2. X API認証情報の設定

#### GitHub Secretsに登録（本番環境）
1. GitHubリポジトリの **Settings** → **Secrets and variables** → **Actions** を開く
2. **New repository secret** をクリック
3. 以下の4つのシークレットを追加：

| Name | Value |
|------|-------|
| `API_KEY` | X Developer PortalのAPI Key |
| `API_SECRET` | X Developer PortalのAPI Secret |
| `ACCESS_TOKEN` | X Developer PortalのAccess Token |
| `ACCESS_SECRET` | X Developer PortalのAccess Token Secret |

#### ローカルテスト用（オプション）
```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集して認証情報を入力
nano .env
```

### 3. GitHub Actionsの有効化

1. GitHubリポジトリの **Actions** タブを開く
2. "I understand my workflows, go ahead and enable them" をクリック
3. ワークフロー `X投資トレンドBot自動実行` が表示されることを確認

### 4. 動作確認

#### 手動実行でテスト
1. **Actions** タブを開く
2. `X投資トレンドBot自動実行` をクリック
3. **Run workflow** → **Run workflow** をクリック
4. 実行結果を確認

#### 自動実行の確認
- 1時間ごとに自動実行されます
- **Actions** タブで実行履歴を確認できます

## 📁 ファイル構成

```
x-trend-bot/
├── .github/
│   └── workflows/
│       └── auto_post.yml       # GitHub Actions設定
├── src/
│   ├── config.py               # 設定ファイル
│   ├── fetch_trends.py         # トレンド取得
│   ├── generate_tweet.py       # 投稿文生成
│   ├── post_tweet.py           # 投稿実行
│   ├── logger.py               # ログ設定
│   └── main.py                 # メイン処理
├── logs/                       # ログファイル（自動生成）
├── .env.example                # 環境変数テンプレート
├── .gitignore                  # Git除外設定
├── requirements.txt            # Python依存関係
└── README.md                   # このファイル
```

## 🧪 ローカルでのテスト実行

### 環境変数を設定
```bash
export API_KEY="your_api_key"
export API_SECRET="your_api_secret"
export ACCESS_TOKEN="your_access_token"
export ACCESS_SECRET="your_access_secret"
export DRY_RUN=true  # trueの場合は実際には投稿しない
```

### トレンド取得のみテスト
```bash
python src/fetch_trends.py
```

### 投稿文生成のみテスト
```bash
python src/generate_tweet.py
```

### 完全フローのテスト（DRY RUN）
```bash
python src/main.py
```

### 実際に投稿する場合
```bash
export DRY_RUN=false
python src/main.py
```

## ⚙️ カスタマイズ

### 投稿頻度の変更
`.github/workflows/auto_post.yml` の cron 設定を変更：

```yaml
# 1時間ごと（デフォルト）
- cron: '0 * * * *'

# 2時間ごと
- cron: '0 */2 * * *'

# 30分ごと
- cron: '*/30 * * * *'

# 毎日9時（JST 18時）
- cron: '0 9 * * *'
```

### トレンド数の変更
`.env` または GitHub Secretsに追加：
```bash
MAX_TRENDS_TO_POST=5  # デフォルト: 5件
```

### キーワードの追加
`src/config.py` の `INVESTMENT_KEYWORDS` リストに追加：
```python
INVESTMENT_KEYWORDS = [
    '株', '投資', 'ビットコイン',
    # ここに新しいキーワードを追加
    'あなたのキーワード',
]
```

### 投稿テンプレートの変更
`src/generate_tweet.py` の `TEMPLATES` リストを編集：
```python
TEMPLATES = [
    "あなたのオリジナルテンプレート\n\n{trends}\n\n#投資",
]
```

## 📊 ログの確認

### GitHub Actionsでの確認
1. **Actions** タブを開く
2. 実行履歴をクリック
3. **post-trend** ジョブをクリック
4. ログを確認

### エラー時のログダウンロード
- エラーが発生した場合、ログファイルが自動的にアーティファクトとして保存されます
- **Artifacts** セクションからダウンロード可能

## ⚠️ 注意事項

### X API制限
- **Free Tier**: 月間500ツイートまで
- **Basic Tier ($100/月)**: 月間3,000ツイートまで
- 1時間1投稿 = 月720投稿 → **Basic以上のプランが必要**

### レート制限
- トレンド取得: 75リクエスト/15分
- ツイート投稿: 300ツイート/3時間

### コンプライアンス
- 投資助言にならないよう注意
- スパム判定されないよう適度な頻度と内容を
- 自動投稿であることを明示推奨

### セキュリティ
- APIキーは絶対に公開しない
- `.env` ファイルはGitにコミットしない
- GitHub Secretsを使用して認証情報を管理

## 🔧 トラブルシューティング

### 認証エラー
```
❌ 認証エラー: 401 Unauthorized
```
→ GitHub Secretsの認証情報が正しいか確認

### トレンドが取得できない
```
⚠️ 投資系トレンドが見つかりませんでした
```
→ 正常動作（現在投資系トレンドがない場合）

### ワークフローが実行されない
- **Actions** タブでワークフローが有効化されているか確認
- リポジトリの **Settings** → **Actions** → **General** で "Allow all actions" が選択されているか確認

### 投稿が重複する
- GitHub Actionsのスケジュールが複数設定されていないか確認
- 手動実行と自動実行が重なっていないか確認

## 📈 今後の拡張案

- [ ] 複数アカウント対応
- [ ] トレンド分析・グラフ生成
- [ ] 過去のトレンド履歴保存
- [ ] Slack/Discord通知連携
- [ ] AIによる投稿文生成
- [ ] 画像付き投稿
- [ ] リプライ自動応答

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエスト歓迎！

## 📧 お問い合わせ

Issue作成またはプルリクエストでご連絡ください。

---

**Happy Tweeting! 🚀📈**
