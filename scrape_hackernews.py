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
# 処理する記事の上限（無料API枠のため）
MAX_ARTICLES_TO_PROCESS = 3
# ----------------

# GitHub SecretsからAPIキーを取得
try:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    print("エラー: 環境変数 'GEMINI_API_KEY' が設定されていません。")
    exit(1)


def get_gemini_summary(article_title, article_url):
    """Gemini APIを使って記事を翻訳・要約する"""
    print(f"Gemini処理中: {article_title}")
    model = genai.GenerativeModel('gemini-1.5-flash')  # 無料枠で高速なモデル

    prompt = f"""
    以下の技術ニュースを日本語で要約してください。

    タイトル: {article_title}
    URL: {article_url}

    出力形式は以下のJSON形式のみでお願いします。
    {{
      "japanese_title": "日本語のタイトル",
      "summary": "3行程度の簡潔な日本語の要約"
    }}
    """

    try:
        response = model.generate_content(prompt)
        # レスポンスがJSON形式であることを期待
        json_response = json.loads(
            response.text.strip("```json\n").strip("\n```"))
        return json_response
    except Exception as e:
        print(f"Gemini APIエラー: {e}")
        return {
            "japanese_title": f"（翻訳エラー: {article_title}）",
            "summary": "記事の要約に失敗しました。"
        }


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
        print(f"Successfully saved {len(data)} articles to {OUTPUT_FILE}")
    except IOError as e:
        print(f"Error writing to file: {e}")


def main():
    print("Fetching Hacker News...")
    html = fetch_hackernews()
    if not html:
        return

    print("Parsing articles...")
    all_articles = parse_news(html)

    print(f"Filtering by keywords...")
    ai_articles = filter_articles(all_articles)

    print(
        f"Found {len(ai_articles)} relevant articles. Processing top {MAX_ARTICLES_TO_PROCESS}...")

    processed_articles = []
    # 上位の記事だけを処理 (API節約)
    for article in ai_articles[:MAX_ARTICLES_TO_PROCESS]:
        summary_data = get_gemini_summary(article["title"], article["url"])

        # 元の記事情報とAIの処理結果をマージ
        article.update(summary_data)
        processed_articles.append(article)
        time.sleep(1)  # APIのレート制限を避けるため

    result_data = {
        "last_updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "articles": processed_articles
    }

    # save_to_json(result_data) を呼び出す
    # (※前回のコードをそのまま使ってください)


if __name__ == "__main__":
    main()
