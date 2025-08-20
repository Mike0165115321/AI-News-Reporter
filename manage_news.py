# manage_news.py (ฉบับปลูกถ่ายความสามารถ)

import feedparser
import requests
import faiss
import json
import os
import time
import torch
import datetime
import traceback
from urllib.parse import urlparse
from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

# ปลูกถ่าย 1: เพิ่ม import ที่จำเป็น
from tqdm import tqdm
from newspaper import Article, Config, ArticleException
from sentence_transformers import SentenceTransformer
from core.config import settings

NEWS_INDEX_DIR = "data/news_index"
NEWS_FAISS_PATH = os.path.join(NEWS_INDEX_DIR, "news_faiss.index")
NEWS_MAPPING_PATH = os.path.join(NEWS_INDEX_DIR, "news_mapping.json")

NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
RSS_FEEDS = {
    "Reuters Tech": "https://www.reuters.com/pf/api/v2/content/corp/rss/US/technology-news-idUSKBN0P204J20150622",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Wired Top Stories": "https://www.wired.com/feed/rss",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
    "Hacker News": "https://news.ycombinator.com/rss",
    "Scientific American": "http://rss.sciam.com/sciam/news",
    "ScienceDaily": "https://www.sciencedaily.com/rss/top.xml",
    
    "Reuters Business": "https://www.reuters.com/pf/api/v2/content/corp/rss/US/business-news-idUSKBN0P002020150615",
    "Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss",
    "The Economist": "https://www.economist.com/finance-and-economics/rss.xml",
    "Harvard Business Review": "https://hbr.org/rss/topic/latest",
    "Financial Times": "https://www.ft.com/world?format=rss",
    "Wall Street Journal": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",

    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Associated Press (AP)": "https://apnews.com/hub/ap-top-news/rss.xml",
    "The New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.xml",
    
    "Google News (TH)": "https://news.google.com/rss?hl=th&gl=TH&ceid=TH:th", 
    "Thai PBS": "https://www.thaipbs.or.th/rss/news.xml",
    "Thairath": "https://www.thairath.co.th/rss/news.xml",
    "The Standard": "https://thestandard.co/feed/",
    "Blognone": "https://www.blognone.com/rss.xml",
    "Brand Buffet": "https://www.brandbuffet.in.th/feed/"
}

def fetch_from_newsapi() -> List[Dict]:
    """ดึงข่าวจาก NewsAPI.org"""
    print("📰 Fetching news from NewsAPI.org...")
    if not settings.NEWS_KEY:
        print("  - ⚠️ NewsAPI key not found in .env file.")
        return []
    
    params = {'country': 'us', 'pageSize': 20, 'apiKey': settings.NEWS_KEY}
    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=15)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        print(f"  - Fetched {len(articles)} articles from NewsAPI.")
        return [{
            "published_at": a.get("publishedAt"),
            "source_name": a.get("source", {}).get("name"),
            "title": a.get("title"),
            "description": a.get("description"),
            "url": a.get("url")
        } for a in articles]
    except Exception as e:
        print(f"  - ❌ NewsAPI Error: {e}")
        return []

def fetch_from_rss(url: str, source: str) -> List[Dict]:
    """ดึงข่าวจากแหล่ง RSS Feed"""
    try:
        feed = feedparser.parse(url)
        return [{
            "published_at": entry.get("published", datetime.datetime.now().isoformat()),
            "source_name": source,
            "title": entry.get("title"),
            "description": entry.get("summary"),
            "url": entry.get("link")
        } for entry in feed.entries]
    except Exception as e:
        print(f"  - ❌ RSS Error ({source}): {e}")
        return []

def sanitize_text(text: str) -> str:
    """ลบอักขระควบคุมที่อาจทำให้เกิดปัญหา"""
    if not text:
        return ""
    return text.replace("\u2028", " ").replace("\u2029", " ")

def scrape_article_content(url: str) -> str:
    """ขูดเนื้อหาข่าวจาก URL พร้อมตั้งค่า Config เพื่อความเสถียร"""
    try:
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        config.request_timeout = 15

        article = Article(url, config=config)
        article.download()
        article.parse()
        return sanitize_text(article.text)
    except ArticleException:
        return ""
    except Exception:
        return ""

def load_existing_urls(mapping_path: str) -> Set[str]:
    """โหลด URL ของข่าวที่มีอยู่แล้วใน Index เพื่อป้องกันการทำงานซ้ำซ้อน"""
    if not os.path.exists(mapping_path):
        return set()
    
    existing_urls = set()
    try:
        with open(mapping_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.values():
                if url := item.get("url"):
                    existing_urls.add(url)
    except (json.JSONDecodeError, IOError):
        print("  - ⚠️ Could not parse existing mapping file. Starting fresh.")
    
    print(f"🔍 Found {len(existing_urls)} existing articles in the index.")
    return existing_urls

def collect_and_scrape_articles(existing_urls: Set[str]) -> List[Dict]:
    """รวบรวมข่าวจากทุกแหล่งพร้อมกัน และขูดเนื้อหาเฉพาะข่าวใหม่แบบ Polite"""
    print("\n--- 📰 Starting Concurrent News Collection ---")
    
    initial_articles = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(fetch_from_newsapi)]
        for name, url in RSS_FEEDS.items():
            futures.append(executor.submit(fetch_from_rss, url, name))
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching feeds"):
            try:
                initial_articles.extend(future.result())
            except Exception as e:
                print(f"  - ❌ A fetch task failed: {e}")

    new_articles_to_process = [
        article for article in initial_articles 
        if article.get("url") and article.get("title") and article.get("url") not in existing_urls
    ]
    
    unique_new_articles = {article['url']: article for article in new_articles_to_process}.values()
    
    print(f"\n🔬 Found {len(unique_new_articles)} new unique articles to scrape.")
    if not unique_new_articles:
        return []

    articles_by_domain = {}
    for article in unique_new_articles:
        try:
            domain = urlparse(article['url']).netloc.replace('www.', '')
            if domain not in articles_by_domain:
                articles_by_domain[domain] = []
            articles_by_domain[domain].append(article)
        except Exception:
            continue
    
    full_articles = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_article = {
            executor.submit(scrape_article_content, articles[0]['url']): articles[0]
            for domain, articles in articles_by_domain.items() if articles
        }
        
        with tqdm(total=len(unique_new_articles), desc="Scraping new articles") as progress_bar:
            while future_to_article:
                for future in as_completed(future_to_article):
                    article_data = future_to_article.pop(future)
                    domain = urlparse(article_data['url']).netloc.replace('www.', '')
                    
                    try:
                        content = future.result()
                        if content:
                            article_data['full_content'] = content
                            full_articles.append(article_data)
                    except Exception as e:
                        print(f"  - ❌ Scrape failed for {article_data['url']}: {e}")
                    
                    progress_bar.update(1)
                    
                    articles_by_domain[domain].pop(0)
                    if articles_by_domain[domain]:
                        next_article = articles_by_domain[domain][0]
                        new_future = executor.submit(scrape_article_content, next_article['url'])
                        future_to_article[new_future] = next_article
                    
                    time.sleep(0.1) 

    print(f"\n💾 Collected {len(full_articles)} new articles with full content.")
    return full_articles

def build_news_index(articles: List[Dict], batch_size: int = 32):
    """สร้างหรืออัปเดต FAISS Index และ Mapping file จากข่าวใหม่"""
    if not articles:
        print("🟡 No new articles to add to the index.")
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n⚙️  Using embedder on device: {device.upper()}")
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device=device)
    
    index = None
    mapping = {}
    
    if os.path.exists(NEWS_FAISS_PATH) and os.path.exists(NEWS_MAPPING_PATH):
        try:
            print("  - Loading existing index to append data...")
            index = faiss.read_index(NEWS_FAISS_PATH)
            with open(NEWS_MAPPING_PATH, "r", encoding="utf-8") as f:
                mapping = json.load(f)
        except Exception as e:
            print(f"  - ⚠️ Error loading existing index/mapping: {e}. Creating new ones.")

    print(f"🧠 Generating embeddings for {len(articles)} new articles...")
    
    for i in tqdm(range(0, len(articles), batch_size), desc="Encoding batches"):
        batch_articles = articles[i:i+batch_size]
        
        texts_to_embed = [
            f"หัวข้อ: {sanitize_text(a.get('title', ''))}\nเนื้อหา: {sanitize_text(a.get('full_content', ''))}" 
            for a in batch_articles
        ]
        
        new_embeddings = model.encode(
            texts_to_embed,
            show_progress_bar=False, 
            convert_to_numpy=True
        ).astype("float32")
        
        if index is None:
            index = faiss.IndexFlatL2(new_embeddings.shape[1])
        
        index.add(new_embeddings)

        start_id = len(mapping)
        for j, article in enumerate(batch_articles):
            article['embedding_text'] = texts_to_embed[j]
            mapping[str(start_id + j)] = article

    os.makedirs(NEWS_INDEX_DIR, exist_ok=True)
    print(f"💾 Saving News Index to '{NEWS_FAISS_PATH}'...")
    faiss.write_index(index, NEWS_FAISS_PATH)
    
    print(f"💾 Saving News Mapping to '{NEWS_MAPPING_PATH}'...")
    with open(NEWS_MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)

    print(f"\n✅ News RAG Index updated successfully! Total articles in index: {index.ntotal}")

if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("--- 📰 Starting News Intelligence Gathering & Indexing 📰 ---")
        print("="*60)
        
        existing_urls = load_existing_urls(NEWS_MAPPING_PATH)
        
        new_articles_with_content = collect_and_scrape_articles(existing_urls)
        
        build_news_index(new_articles_with_content)

    except KeyboardInterrupt:
        print("\n\n🛑 Process interrupted by user (Ctrl+C).")
    except Exception as e:
        print(f"\n❌ A critical error occurred in the main process: {e}")
        traceback.print_exc()
    finally:
        print("\n" + "="*60)
        print("✅ News RAG Index build process finished.")
        print("="*60)