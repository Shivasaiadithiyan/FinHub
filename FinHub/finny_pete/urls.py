from django.urls import path
from . import views

app_name = 'finny_pete'

urlpatterns = [
    path('', views.finny_pete_view, name='chat_view'),
    path('clear-chat/', views.clear_chat_history, name='clear_chat_history'),  # Clear chat history
]
