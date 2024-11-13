# from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings
# import requests
# import finny_pete.env_var as env_var


# API_KEY = env_var.key

# BASE_URL = "https://integrate.api.nvidia.com/v1"

# @csrf_exempt
# def finny_pete_view(request):
#     # Initialize chat history
#     if 'messages' not in request.session:
#         request.session['messages'] = []

#     if request.method == "POST":
#         user_message = request.POST.get('message')
        
#         # Append user message to session history
#         request.session['messages'].append({"role": "user", "content": user_message})
        
#         # Get bot response from NVIDIA's API
#         response_content = get_chat_response(user_message)
        
#         # Append bot response to session history
#         request.session['messages'].append({"role": "assistant", "content": response_content})
        
#         # Update session to make messages persistent across requests
#         request.session.modified = True
#         return redirect('finny_pete:chat_view')

#     return render(request, 'finny_pete.html', {'messages': request.session.get('messages', [])})

# def get_chat_response(user_message):
#     headers = {
#         'Authorization': f'Bearer {API_KEY}',
#         'Content-Type': 'application/json',
#     }

#     payload = {
#         "model": "writer/palmyra-fin-70b-32k",
#         "messages": [{"role": "user", "content": user_message}],
#         "temperature": 0.2,
#         "top_p": 0.7,
#         "max_tokens": 3073,
#         "stream": False  
#     }

#     response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
    
#     if response.status_code == 200:
#         try:
#             response_data = response.json()
#             return response_data['choices'][0]['message']['content']
#         except Exception as e:
#             return "Error in response processing."
#     else:
#         return "Failed to get a response from the model."

# # Add a new view to handle clearing the session when going back to the menu
# def clear_chat_history(request):
#     request.session['messages'] = []  # Clear the session history
#     return redirect('home')  # Redirect to the home page or menu

from django.shortcuts import render
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import finny_pete.env_var as env_var

# Load sentiment analysis model
sentiment_model = pipeline("text-classification", model="ProsusAI/finbert")

# Setup API details
API_KEY = env_var.key
BASE_URL = "https://integrate.api.nvidia.com/v1"

def sentiment_view(request):
    if request.method == "POST":
        url = request.POST.get("url")
        title, content = fetch_article(url)
        
        if title and content:
            sentiment, score = analyze_sentiment(title)
            summary = get_summary_from_nvidia(url)  # Use NVIDIA model for summary generation
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

def get_summary_from_nvidia(url):
    # Prepare the prompt for the NVIDIA model
    prompt = f"give detailed summary {url}"

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        "model": "writer/palmyra-fin-70b-32k",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 1024,  # Adjusted for a detailed summary response
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

# Back button functionality
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def finny_pete_view(request):
    # Initialize chat history
    if 'messages' not in request.session:
        request.session['messages'] = []

    if request.method == "POST":
        user_message = request.POST.get('message')
        
        # Append user message to session history
        request.session['messages'].append({"role": "user", "content": user_message})
        
        # Get bot response from NVIDIA's API
        response_content = get_chat_response(user_message)
        
        # Append the full bot response as a single message to the session history
        request.session['messages'].append({"role": "assistant", "content": response_content})
        
        # Update session to make messages persistent across requests
        request.session.modified = True
        return render(request, 'finny_pete.html', {'messages': request.session.get('messages', [])})

    return render(request, 'finny_pete.html', {'messages': request.session.get('messages', [])})

def get_chat_response(user_message):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        "model": "writer/palmyra-fin-70b-32k",
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 3073,
        "stream": False  
    }

    response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
    
    if response.status_code == 200:
        try:
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        except Exception as e:
            return "Error in response processing."
    else:
        return "Failed to get a response from the model."

# Add a new view to handle clearing the session when going back to the menu
def clear_chat_history(request):
    request.session['messages'] = []  # Clear the session history
    return redirect('home')  # Redirect to the home page or menu
