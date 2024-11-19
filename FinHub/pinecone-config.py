import os
import requests
import hashlib
from pinecone import Pinecone, Index, ServerlessSpec
from sentence_transformers import SentenceTransformer
import finny_pete.env_var as env_var
from datetime import datetime

# API Keys
PINECONE_API_KEY = env_var.pinecone_key
NEWS_API_KEY = env_var.news_api_key  # Your NewsAPI key

# Initialize Pinecone Client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define Index Name and Dimension
index_name = "indian-market-data"
dimension = 768  # Dimension of the embedding model

# Create or Connect to the Pinecone Index
try:
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    host = pc.describe_index(index_name).host
    index = Index(name=index_name, host=host, api_key=PINECONE_API_KEY)
except Exception as e:
    print(f"Error initializing Pinecone: {e}")
    exit()

# Initialize Embedding Model
try:
    embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
except Exception as e:
    print(f"Error loading embedding model: {e}")
    exit()

# Helper Function to Upload Documents
def upload_documents_to_pinecone(documents, doc_type):
    try:
        for doc in documents:
            vector_id = hashlib.md5(doc["text"].encode("utf-8")).hexdigest()
            embedding = embedding_model.encode(doc["text"]).tolist()
            metadata = {
                "text": doc["text"],
                "type": doc_type,
                "category": doc.get("category"),
                "date": doc.get("date"),
                "source": doc.get("source"),
            }
            index.upsert([(vector_id, embedding, metadata)])
        print(f"{doc_type.capitalize()} documents uploaded successfully.")
    except Exception as e:
        print(f"Error uploading {doc_type} documents: {e}")

# Fetch News Articles
def fetch_news():
    NEWS_API_URL = "https://newsapi.org/v2/everything"
    queries = [
        "stock market news India",
        "Indian market analysis",
        "sector performance India",
        "stock recommendations India",
        "trading strategies India",
        "earnings reports India",
        "financial analysis India",
        "Nifty index analysis",
        "Sensex performance today",
        "Indian mutual funds news",
        "dividend stocks India",
        "stock market trends in India",
        "market volatility India",
        "market outlook India",
        "investment opportunities India",
        "cryptocurrency market India",
        "commodity prices India",
        "global stock market performance",
        "BSE stock news",
        "Nifty options trading news",
        "sectoral performance Nifty",
        "company financials India",
        "corporate earnings India",
        "stock market regulations India",
        "stock trading news",
        "tech stocks India",
        "banking stocks India",
        "FII (Foreign Institutional Investors) flows India",
        "foreign exchange rates India"
        "Indian stock market",
        "recent IPOs in India",
        "Nifty 50 performance",
        "Sensex",
        "gold prices in India",
        "Indian economy updates",
        "government bonds India",
        "Indian stock market news",
        "financial news India",
        "inflation in India",
        "GDP growth India",
        "Indian fiscal policy",
        "monetary policy India",
        "Indian debt market",
        "commodity market India",
        "banking news India",
        "interest rates India",
        "ipo prices recent India",
        "indian government investment sectors",

        # Additional Queries for Finance and Stock Market
        
    ]
    
    all_articles = []
    for query in queries:
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": NEWS_API_KEY,
        }
        response = requests.get(NEWS_API_URL, params=params)
        if response.status_code == 200:
            news_data = response.json().get("articles", [])
            articles = [
                {
                    "text": f"{article['title']} {article.get('description', '')}",
                    "category": "news",
                    "date": article["publishedAt"],
                    "source": article["source"]["name"],
                }
                for article in news_data
            ]
            all_articles.extend(articles)
        else:
            print(f"Error fetching news for query '{query}': {response.status_code}")
    return all_articles

# Fetch Recent IPO Data (Dynamic)
def fetch_recent_ipos():
    IPO_API_URL = "https://newsapi.org/v2/everything"
    queries = [
        "newly listed stocks India",
        "IPO pricing in India",
        "IPOs in Indian stock market",
        "IPO performance India"
        "recent IPOs in India",
        "Indian IPO market news",
        "upcoming IPOs India",
        "IPO listings India",
    ]
    all_articles = []
    for query in queries:
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": NEWS_API_KEY,
        }
        response = requests.get(IPO_API_URL, params=params)
        if response.status_code == 200:
            ipo_data = response.json().get("articles", [])
            articles = [
                {
                    "text": f"{article['title']} {article.get('description', '')}",
                    "category": "IPO",
                    "date": article["publishedAt"],
                    "source": article["source"]["name"],
                }
                for article in ipo_data
            ]
            all_articles.extend(articles)
        else:
            print(f"Error fetching IPO data: {response.status_code}")
    return all_articles

# Fetch Macroeconomic Data (Dynamic)
def fetch_macro_data():
    MACRO_API_URL = "https://newsapi.org/v2/everything"
    queries = [
         "Indian fiscal policy OR budget news",
        "India trade balance news",
        "Indian government spending",
        "India economic growth outlook",
        "macroeconomic news India",
        "Indian unemployment rate",
        "India GDP projections",
        "inflation trends India",
        "Indian economic policy",
        "India central bank news",
        "monetary policy India",
        "Indian tax policy",
        "India interest rates news"
        "Indian economy updates OR GDP growth OR inflation",
       
    ]
    
    all_articles = []
    for query in queries:
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": NEWS_API_KEY,
        }
        response = requests.get(MACRO_API_URL, params=params)
        if response.status_code == 200:
            macro_data = response.json().get("articles", [])
            articles = [
                {
                    "text": f"{article['title']} {article.get('description', '')}",
                    "category": "economy",
                    "date": article["publishedAt"],
                    "source": article["source"]["name"],
                }
                for article in macro_data
            ]
            all_articles.extend(articles)
        else:
            print(f"Error fetching macroeconomic data: {response.status_code}")
    return all_articles

# Main Workflow
def main():
    # Fetch and Upload News
    news_articles = fetch_news()
    upload_documents_to_pinecone(news_articles, doc_type="news")

    # Fetch and Upload Macroeconomic Data
    macro_data = fetch_macro_data()
    upload_documents_to_pinecone(macro_data, doc_type="macro")

    # Fetch and Upload IPO Data
    ipo_data = fetch_recent_ipos()
    upload_documents_to_pinecone(ipo_data, doc_type="ipo")

    print("Dynamic data ingestion completed.")

if __name__ == "__main__":
    main()
