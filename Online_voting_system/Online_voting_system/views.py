from django.shortcuts import render

def index(request):
    # Use relative path, not absolute filesystem path
    return render(request, 'Online_voting_system/index.html')