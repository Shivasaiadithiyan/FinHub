
# from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt
# import requests
# import json  # Import json for formatting the JSON response
# import finny_pete.env_var as env_var

# # Setup API details for Finny_Pete (NVIDIA API)
# API_KEY = env_var.key
# BASE_URL = "https://integrate.api.nvidia.com/v1"

# @csrf_exempt
# def finny_pete_view(request):
#     """
#     Finny_Pete chat view. Handles the chat conversation by storing user messages and generating
#     responses using the NVIDIA model.
#     """
#     # Initialize chat history in the session if it doesn't exist
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
#         return render(request, 'finny_pete.html', {'messages': request.session.get('messages', [])})

#     return render(request, 'finny_pete.html', {'messages': request.session.get('messages', [])})


# def get_chat_response(user_message):
#     """
#     Sends a request to NVIDIA API for generating a chat response based on the user's message
#     and converts the JSON response to a readable string format.
#     """
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
#             # Parse the JSON response into a string format for display
#             response_data = response.json()
#             response_content = response_data['choices'][0]['message']['content']
            
#             # Convert response JSON to a nicely formatted string (if necessary)
#             formatted_response = json.dumps(response_content, indent=2)  # Optional: format JSON
            
#             return formatted_response  # Return the formatted string for display in the chat
#         except Exception as e:
#             return "Error in response processing."
#     else:
#         return "Failed to get a response from the model."


# def clear_chat_history(request):
#     """
#     Clears the chat history in the session and redirects to the home page or menu.
#     """
#     request.session['messages'] = []  # Clear the session history
#     return redirect('home')  # Redirect to the home page or menu

#ver 2

# from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt
# import requests
# from sentence_transformers import SentenceTransformer
# from pinecone import Pinecone, Index
# import finny_pete.env_var as env_var
# import logging

# # Setup logging
# logging.basicConfig(level=logging.DEBUG)

# # API Details
# API_KEY = env_var.key  # NVIDIA API key
# BASE_URL = "https://integrate.api.nvidia.com/v1"
# PINECONE_API_KEY = env_var.pinecone_key
# INDEX_NAME = "indian-market-data"

# # Initialize Pinecone Client and Embedding Model
# pc = Pinecone(api_key=PINECONE_API_KEY)
# host = pc.describe_index(INDEX_NAME).host
# index = Index(name=INDEX_NAME, host=host, api_key=PINECONE_API_KEY)
# embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")


# @csrf_exempt
# def finny_pete_view(request):
#     """
#     Handles chat with the user, augmenting responses with relevant documents.
#     """
#     # Initialize messages session if not present
#     if 'messages' not in request.session:
#         request.session['messages'] = []

#     if request.method == "POST":
#         # Log and retrieve the user message
#         user_message = request.POST.get('message-bar')
#         logging.debug(f"POST data: {request.POST}")
#         logging.debug(f"User message extracted: {user_message}")

#         if not user_message:
#             logging.error("User message is empty!")
#             return render(request, 'finny_pete.html', {
#                 'messages': request.session.get('messages', []),
#                 'error': "Message cannot be empty."
#             })

#         # Retrieve relevant documents from Pinecone
#         context = retrieve_documents(user_message)
#         logging.debug(f"Retrieved context: {context}")

#         # Handle empty context
#         if not context:
#             context = ["No relevant documents were found."]
#         context_str = "\n".join(context)  # Convert context list to string

#         # Augment user message with context
#         augmented_message = f"User query: {user_message}\n\nRelevant context:\n{context_str}"

#         # Get bot response from NVIDIA API
#         bot_response = get_chat_response(augmented_message)
#         logging.debug(f"Bot response: {bot_response}")

#         # Save messages in session
#         request.session['messages'].append({"role": "user", "content": user_message})
#         request.session['messages'].append({"role": "assistant", "content": bot_response})
#         request.session.modified = True

#         return render(request, 'finny_pete.html', {'messages': request.session.get('messages', [])})

#     return render(request, 'finny_pete.html', {'messages': request.session.get('messages', [])})


# def get_chat_response(augmented_message):
#     """
#     Sends a request to NVIDIA API, augmented with document context.
#     """
#     headers = {
#         'Authorization': f'Bearer {API_KEY}',
#         'Content-Type': 'application/json',
#     }

#     payload = {
#         "model": "writer/palmyra-fin-70b-32k",
#         "messages": [{"role": "user", "content": augmented_message}],
#         "temperature": 0.2,
#         "top_p": 0.7,
#         "max_tokens": 3073,
#         "stream": False
#     }

#     try:
#         response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
#         if response.status_code == 200:
#             response_data = response.json()
#             return response_data['choices'][0]['message']['content']
#         else:
#             logging.error(f"NVIDIA API Error: {response.status_code} - {response.text}")
#             return "Sorry, there was an issue processing your request. Please try again later."
#     except Exception as e:
#         logging.error(f"Error in get_chat_response: {e}")
#         return "An error occurred while contacting the AI model. Please try again."


# def retrieve_documents(query, top_k=5):
#     """
#     Retrieves top-k relevant documents for a given query from Pinecone.
#     """
#     try:
#         query_embedding = embedding_model.encode(query).tolist()
#         logging.debug(f"Query embedding generated: {query_embedding[:5]}...")  # Log first 5 values of embedding

#         results = index.query(query_embedding, top_k=top_k, include_metadata=True)
#         logging.debug(f"Pinecone results: {results}")

#         # Return list of document texts
#         return [result['metadata'].get('text', 'No metadata found') for result in results['matches']]
#     except Exception as e:
#         logging.error(f"Error during document retrieval: {e}")
#         return []


# def clear_chat_history(request):
#     """
#     Clears chat history and redirects to home.
#     """
#     request.session['messages'] = []
#     return redirect('home')

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import requests
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, Index
import finny_pete.env_var as env_var
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# API Details
API_KEY = env_var.key  # NVIDIA API key
BASE_URL = "https://integrate.api.nvidia.com/v1"
PINECONE_API_KEY = env_var.pinecone_key
INDEX_NAME = "indian-market-data"

# Initialize Pinecone Client and Embedding Model
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    host = pc.describe_index(INDEX_NAME).host
    index = Index(name=INDEX_NAME, host=host, api_key=PINECONE_API_KEY)
    embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
except Exception as e:
    logging.error(f"Initialization error: {e}")
    raise RuntimeError("Failed to initialize Pinecone or embedding model.") from e


@csrf_exempt
def finny_pete_view(request):
    """
    Handles chat with the user, augmenting responses with relevant documents.
    """
    # Initialize or retrieve chat history
    if 'messages' not in request.session:
        request.session['messages'] = []

    if request.method == "POST":
        # Extract user message
        user_message = request.POST.get('message-bar', "").strip()
        if not user_message:
            logging.error("User message is empty.")
            return render(request, 'finny_pete.html', {
                'messages': request.session.get('messages', []),
                'error': "Message cannot be empty.",
            })

        # Retrieve relevant documents
        try:
            context = retrieve_documents(user_message)
            logging.debug(f"Context retrieved: {context}")
        except Exception as e:
            logging.error(f"Error during document retrieval: {e}")
            context = ["An error occurred while fetching relevant documents."]

        # Format context
        context_str = "\n".join(context) if context else "No relevant documents found."

        # Augment user query with context
        augmented_message = f"User query: {user_message}\n\nRelevant context:\n{context_str}"

        # Fetch response from NVIDIA API
        bot_response = get_chat_response(augmented_message)

        # Update session chat history
        request.session['messages'].append({"role": "user", "content": user_message})
        request.session['messages'].append({"role": "assistant", "content": bot_response})
        request.session.modified = True

        # Render updated chat
        return render(request, 'finny_pete.html', {
            'messages': request.session.get('messages', []),
        })

    # Render chat page for GET requests
    return render(request, 'finny_pete.html', {'messages': request.session.get('messages', [])})

def format_response_content(response_content):
    """
    Formats the response content to:
    1. Truncate to the nearest full stop if it ends mid-sentence.
    2. Replace **text** with bolded text.
    3. Add newline characters after bold text for readability.
    """
    try:
        # Truncate to the nearest full stop
        if "." in response_content:
            last_full_stop = response_content.rfind(".")
            response_content = response_content[: last_full_stop + 1]

        # Replace **text** with bold text
        response_content = response_content.replace("**", "**\n")

        return response_content
    except Exception as e:
        logging.error(f"Error formatting response content: {e}")
        return "An error occurred. "

def get_chat_response(augmented_message):
    """
    Sends a request to the NVIDIA API for a response.
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        "model": "writer/palmyra-fin-70b-32k",
        "messages": [{"role": "user", "content": augmented_message}],
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 2048,
        "stream": False,
    }

    try:
        response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            return format_response_content(response_data['choices'][0]['message']['content'])
        else:
            logging.error(f"NVIDIA API error: {response.status_code} - {response.text}")
            return "I'm sorry, I couldn't process your request. Please try again later."
    except Exception as e:
        logging.error(f"Error in get_chat_response: {e}")
        return "An error occurred while generating a response. Please try again."




def retrieve_documents(query, top_k=5):
    """
    Retrieves the top-k relevant documents for a query from Pinecone.
    """
    try:
        # Encode the query into an embedding
        query_embedding = embedding_model.encode(query).tolist()

        # Perform the query using keyword arguments
        results = index.query(
            vector=query_embedding,  # The embedding of the query
            top_k=top_k,             # Number of top matches to retrieve
            include_metadata=True    # Include metadata in the results
        )

        # Extract and return document text from results
        return [result['metadata'].get('text', 'No metadata available') for result in results.get('matches', [])]

    except Exception as e:
        logging.error(f"Error retrieving documents from Pinecone: {e}")
        return []



def clear_chat_history(request):
    """
    Clears the chat history.
    """
    request.session['messages'] = []
    return redirect('home')
