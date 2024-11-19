
from django.shortcuts import render
import requests
from transformers import pipeline
from bs4 import BeautifulSoup
import fintiment.env_var as env_var  # Import API key for NVIDIA Finance Bot

# Load sentiment analysis model for Fintiment
sentiment_model = pipeline("text-classification", model="ProsusAI/finbert")

# Setup NVIDIA API details
API_KEY = env_var.key
BASE_URL = "https://integrate.api.nvidia.com/v1"

def sentiment_view(request):
    """
    Fintiment view for sentiment analysis and summarization.
    Allows users to input a URL for sentiment and summary generation.
    """
    if request.method == "POST":
        url = request.POST.get("url")
        title, content = fetch_article(url)
        
        if title and content:
            sentiment, score = analyze_sentiment(title)
            summary = get_summary_from_nvidia(content)  # Use NVIDIA model for summary generation
            return render(request, 'fintiment.html', {
                "title": title,
                "sentiment": sentiment,
                "score": score,
                "summary": summary
            })

    return render(request, 'fintiment.html')


def fetch_article(url):
    """
    Fetches the article title and content from a given URL.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
    content = " ".join(paragraph.get_text(strip=True) for paragraph in soup.find_all('p'))
    return title, content


def analyze_sentiment(title):
    """
    Analyzes the sentiment of the article title using the FinBERT model.
    """
    result = sentiment_model(title[:512])  # Truncate to 512 tokens if necessary
    sentiment = result[0]["label"]
    score = result[0]["score"]
    return sentiment, score


def get_summary_from_nvidia(content):
    """
    Generates a summary of the article content using NVIDIA Finance Bot API.
    """
    prompt = f"Summarize the following financial article: {content[:1000]}"  # Truncate content to fit within model limits

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        "model": "writer/palmyra-fin-70b-32k",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 1024,  # Adjusted for a summary response
        "stream": False
    }

    # Send request to NVIDIA's API
    response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
    
    if response.status_code == 200:
        try:
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        except Exception as e:
            return "Error in processing response."
    else:
        return "Failed to get a summary from the model."
