#!/usr/bin/env python3
"""
HackerNews AI Scraper
Scrapes AI-related stories from HackerNews and saves them to a JSON file.
"""

import json
import requests
from datetime import datetime

def fetch_hackernews_stories():
    """Fetch top stories from HackerNews API."""
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_story_details(story_id):
    """Fetch details of a specific story."""
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def is_ai_related(title, text=""):
    """Check if a story is AI-related."""
    ai_keywords = [
        'ai', 'artificial intelligence', 'machine learning', 'ml',
        'deep learning', 'neural network', 'gpt', 'llm',
        'large language model', 'chatgpt', 'openai', 'anthropic',
        'transformer', 'nlp', 'computer vision', 'reinforcement learning'
    ]
    
    combined_text = f"{title} {text}".lower()
    return any(keyword in combined_text for keyword in ai_keywords)

def scrape_ai_news(max_stories=100):
    """Scrape AI-related news from HackerNews."""
    print("Fetching HackerNews stories...")
    story_ids = fetch_hackernews_stories()[:max_stories]
    
    ai_stories = []
    
    for i, story_id in enumerate(story_ids):
        try:
            story = fetch_story_details(story_id)
            
            if story and story.get('type') == 'story':
                title = story.get('title', '')
                text = story.get('text', '')
                
                if is_ai_related(title, text):
                    ai_story = {
                        'id': story.get('id'),
                        'title': title,
                        'url': story.get('url', ''),
                        'score': story.get('score', 0),
                        'by': story.get('by', ''),
                        'time': story.get('time', 0),
                        'descendants': story.get('descendants', 0)
                    }
                    ai_stories.append(ai_story)
                    print(f"Found AI story: {title}")
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(story_ids)} stories...")
                
        except Exception as e:
            print(f"Error fetching story {story_id}: {e}")
            continue
    
    return ai_stories

def save_to_json(stories, filename='ai_news.json'):
    """Save stories to a JSON file."""
    data = {
        'last_updated': datetime.utcnow().isoformat(),
        'story_count': len(stories),
        'stories': stories
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(stories)} AI stories to {filename}")

def main():
    """Main function."""
    print("Starting HackerNews AI Scraper...")
    ai_stories = scrape_ai_news(max_stories=100)
    save_to_json(ai_stories)
    print("Done!")

if __name__ == '__main__':
    main()
