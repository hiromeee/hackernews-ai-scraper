import json
from jinja2 import Environment, FileSystemLoader
import os

JSON_FILE = "ai_news.json"
TEMPLATE_FILE = "template.html"
OUTPUT_DIR = "dist"  # デプロイするファイル置き場
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")


def build_html():
    print(f"Loading data from {JSON_FILE}...")
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"エラー: {JSON_FILE} が見つかりません。")
        return
    except json.JSONDecodeError:
        print(f"エラー: {JSON_FILE} のJSON形式が正しくありません。")
        return

    print(f"Loading template {TEMPLATE_FILE}...")
    # テンプレートエンジンを設定 (カレントディレクトリの 'template.html' を探す)
    env = Environment(loader=FileSystemLoader("."), autoescape=True)
    template = env.get_template(TEMPLATE_FILE)

    # テンプレートにデータを渡してHTMLを生成
    html_content = template.render(
        last_updated_utc=data.get("last_updated_utc", "N/A"),
        articles=data.get("articles", [])
    )

    # 出力ディレクトリを作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 最終的なHTMLファイルとして保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Successfully generated {OUTPUT_FILE}")


if __name__ == "__main__":
    build_html()
