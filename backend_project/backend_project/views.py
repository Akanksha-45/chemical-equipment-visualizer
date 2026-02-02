# backend_project/views.py
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Backend is running"})
