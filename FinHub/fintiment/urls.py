from django.urls import path
from . import views

app_name = 'fintiment'

urlpatterns = [
    path('', views.sentiment_view, name='sentiment_view'),
]
