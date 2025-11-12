# AI Tech News Summary (from Hacker News)

Hacker NewsからAI・Python関連のニュースを自動収集し、Gemini API（`gemini-1.5-flash`）で日本語に翻訳・要約して、GitHub Pagesに静的サイトとして自動公開するプロジェクトです。

**[公開サイトのデモURL](https://hiromeee.github.io/hackernews-ai-scraper/)**（※ご自身のURLに置き換えてください）

![サイトのスクリーンショット](https://hiromeee.github.io/hackernews-ai-scraper/demo.png) 
## 🤖 主な機能

このプロジェクトは、GitHub ActionsのCI/CDパイプラインによって完全に自動化されています。

1.  **自動収集 (Scrape)**: 6時間ごと にHacker Newsのトップページを巡回し、指定したキーワード（"ai", "python", "llm"など）に一致する記事を取得します。
2.  **AI要約 (Summarize)**: 取得した記事をGemini APIに渡し、「日本語タイトルへの翻訳」と「3行の日本語要約」を生成させます。
3.  **サイト構築 (Build)**: AIの生成結果を `ai_news.json` に保存し、それを `template.html` と組み合わせて静的なWebサイト（`index.html`）を構築します。
4.  **自動デプロイ (Deploy)**: 構築したWebサイトをGitHub Pagesに自動でデプロイ（公開）します。
5.  **CI/CD**: `main` ブランチにコード（UIの修正など）をプッシュすると、自動でCIが走り、サイトが即座に更新されます。

## 🛠️ 使用技術

### バックエンド (Python)
* **`requests`**: Webスクレイピング（Hacker Newsへのアクセス）
* **`beautifulsoup4`**: HTMLの解析
* **`google-generativeai`**: Gemini API（翻訳・要約）
* **`Jinja2`**: HTMLテンプレートエンジン（静的サイト生成）

### フロントエンド
* **HTML5**
* **Tailwind CSS (CDN)**: モダンなUIデザイン

### CI/CD & インフラ
* **GitHub Actions**: 自動化パイプライン
* **GitHub Pages**: 静的サイトホスティング

## 🚀 セットアップ手順

このリポジトリをフォーク（Fork）またはクローンして、ご自身のアカウントで動かすための手順です。

### 1. Gemini APIキーの取得

1.  [Google AI Studio](https://aistudio.google.com/app) にアクセスします。
2.  「Get API key」から新しいAPIキーを作成し、コピーします。

### 2. GitHubリポジトリの設定

1.  **シークレットの登録**
    * リポジトリの `Settings` > `Secrets and variables` > `Actions` を開きます。
    * `New repository secret` をクリックします。
    * **Name**: `GEMINI_API_KEY`
    * **Secret**: ステップ1でコピーしたAPIキーを貼り付けます。

2.  **GitHub Pagesの設定**
    * リポジトリの `Settings` > `Pages` を開きます。
    * `Build and deployment` > `Source` で、「**GitHub Actions**」を選択します。

### 3. プロジェクトの実行

上記の設定が完了したら、`main` ブランチにプッシュするか、[Actions] タブで `Build and Deploy AI News Site` ワークフローを [Run workflow] ボタンから手動実行します。

ワークフローが成功すると、`Settings` > `Pages` に表示されるURL（例: `https://[YOUR_USERNAME].github.io/[REPOSITORY_NAME]/`）でサイトが公開されます。



---