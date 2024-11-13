from django.shortcuts import render
from transformers import pipeline
import requests
from bs4 import BeautifulSoup

# Load sentiment analysis and summarization models
sentiment_model = pipeline("text-classification", model="ProsusAI/finbert")
summarizer = pipeline("summarization", model="Falconsai/text_summarization")

def sentiment_view(request):
    if request.method == "POST":
        url = request.POST.get("url")
        title, content = fetch_article(url)
        
        if title and content:
            sentiment, score = analyze_sentiment(title)
            summary = summarize_content(content)
            return render(request, 'fintiment.html', {
                "title": title,
                "sentiment": sentiment,
                "score": score,
                "summary": summary
            })

    return render(request, 'fintiment.html')

def fetch_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
    content = " ".join(paragraph.get_text(strip=True) for paragraph in soup.find_all('p'))
    return title, content

def analyze_sentiment(title):
    result = sentiment_model(title[:512])  # Truncate to 512 tokens if necessary
    sentiment = result[0]["label"]
    score = result[0]["score"]
    return sentiment, score

def summarize_content(content):
    summary = summarizer(content, max_length=1024, min_length=150, do_sample=False)
    return summary[0]['summary_text']
