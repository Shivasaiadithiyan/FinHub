from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

# Home view for the landing page
def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Home page at root URL
    path('finny_pete/', include('finny_pete.urls')),
    path('fintiment/', include('fintiment.urls')),
]
