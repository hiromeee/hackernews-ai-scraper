import requests
from bs4 import BeautifulSoup
import json
import time
import os
import google.generativeai as genai

# --- 設定 ---
# 監視したいキーワード (小文字)
KEYWORDS = ["ai", "python", "llm", "gpt",
            "deep learning", "pytorch", "tensorflow"]
# Hacker News トップページ
URL = "https://news.ycombinator.com/"
# 保存ファイル名
OUTPUT_FILE = "ai_news.json"
# 処理する記事の上限（無料API枠と実行時間のため）
MAX_ARTICLES_TO_PROCESS = 5
# ----------------

# --- Gemini API設定 ---
try:
    # GitHub ActionsのSecretsからAPIキーを取得
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    print("エラー: 環境変数 'GEMINI_API_KEY' が設定されていません。")
    if "GEMINI_API_KEY" not in os.environ:
        exit("GitHub Secrets (GEMINI_API_KEY) が設定されていないため終了します。")


def get_gemini_summary(article_title, article_url):
    """Gemini APIを使って記事を翻訳・要約する"""
    print(f"Gemini処理中: {article_title}")
    # gemini-1.5-flash は高速で無料枠があります
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    以下の技術ニュースを日本語で要約してください。

    タイトル: {article_title}
    URL: {article_url}

    出力は、必ず以下のJSON形式のみでお願いします。説明や前置きは一切不要です。
    {{
      "japanese_title": "日本語に翻訳したタイトル",
      "summary": "3行程度の簡潔な日本語の要約"
    }}
    """

    try:
        # API呼び出し (タイムアウトを30秒に設定)
        response = model.generate_content(
            prompt, request_options={"timeout": 30})

        # レスポンスがJSON形式であることを期待してパース
        # Geminiは時々 ```json ... ``` で囲むことがあるため、それを取り除く
        cleaned_text = response.text.strip().lstrip("```json").rstrip("```").strip()

        json_response = json.loads(cleaned_text)

        # 必須キーのチェック
        if "japanese_title" in json_response and "summary" in json_response:
            return json_response
        else:
            raise ValueError("必要なキー (japanese_title, summary) がありません")

    except Exception as e:
        print(f"Gemini APIエラー (タイトル: {article_title}): {e}")
        # エラーが発生した場合も、サイト表示が壊れないよう空の情報を返す
        return {
            "japanese_title": f"（AI処理エラー: {article_title}）",
            "summary": "記事の要約・翻訳に失敗しました。"
        }

# --- ここから下は、以前のスクリプトにあった関数です ---


def fetch_hackernews():
    """Hacker Newsのトップページを取得して解析する"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None


def parse_news(html_content):
    """HTMLから記事のタイトルとURLを抽出する"""
    soup = BeautifulSoup(html_content, "html.parser")
    articles = []
    # Hacker Newsのタイトル行は 'titleline' クラスが使われている
    for item in soup.find_all("span", class_="titleline"):
        tag = item.find("a")
        if tag:
            title = tag.get_text()
            url = tag.get("href")
            # 相対URL (例: "item?id=...") の場合は完全なURLに変換
            if url.startswith("item?"):
                url = f"https://news.ycombinator.com/{url}"

            articles.append({"title": title, "url": url})
    return articles


def filter_articles(articles):
    """キーワードで記事をフィルタリングする"""
    filtered = []
    for article in articles:
        title_lower = article["title"].lower()
        if any(keyword in title_lower for keyword in KEYWORDS):
            filtered.append(article)
    return filtered


def save_to_json(data):
    """収集結果をJSONファイルに保存する"""
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # 保存された記事の件数を表示（data["articles"] の件数）
        print(
            f"Successfully saved {len(data.get('articles', []))} articles to {OUTPUT_FILE}")
    except IOError as e:
        print(f"Error writing to file: {e}")

# --- main関数 (AI処理を呼び出すように更新) ---


def main():
    print("Fetching Hacker News...")
    html = fetch_hackernews()
    if not html:
        print("Failed to fetch HTML. Exiting.")
        return

    print("Parsing articles...")
    all_articles = parse_news(html)

    print(
        f"Found {len(all_articles)} articles. Filtering by keywords: {KEYWORDS}")
    ai_articles = filter_articles(all_articles)

    if not ai_articles:
        print("キーワードにマッチする記事が見つかりませんでした。")
        processed_articles = []
    else:
        print(
            f"Found {len(ai_articles)} relevant articles. Processing top {MAX_ARTICLES_TO_PROCESS}...")
        processed_articles = []
        # 上位の記事だけを処理 (API節約)
        for article in ai_articles[:MAX_ARTICLES_TO_PROCESS]:
            # Gemini APIを呼び出し
            summary_data = get_gemini_summary(article["title"], article["url"])

            # 元の記事情報とAIの処理結果をマージ
            article.update(summary_data)
            processed_articles.append(article)
            # APIのレート制限を避けるため、1秒待機
            time.sleep(1)

    # 最終的な結果データ (build_site.py が読み込む形式)
    result_data = {
        "last_updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "articles": processed_articles  # ここが重要！
    }

    save_to_json(result_data)
    print("Script finished.")


if __name__ == "__main__":
    main()
