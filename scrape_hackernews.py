import requests
from bs4 import BeautifulSoup
import json
import time

# --- 設定 ---
# 監視したいキーワード (小文字)
KEYWORDS = ["ai", "python", "llm", "gpt", "deep learning", "pytorch", "tensorflow"]
# Hacker News トップページ
URL = "https://news.ycombinator.com/"
# 保存ファイル名
OUTPUT_FILE = "ai_news.json"
# ----------------

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
        print("Failed to fetch HTML. Exiting.")
        return

    print("Parsing articles...")
    all_articles = parse_news(html)
    
    print(f"Found {len(all_articles)} articles. Filtering by keywords...")
    ai_articles = filter_articles(all_articles)
    
    # 実行時刻を追加
    result_data = {
        "last_updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "keywords_used": KEYWORDS,
        "articles": ai_articles
    }
    
    save_to_json(result_data)

if __name__ == "__main__":
    main()