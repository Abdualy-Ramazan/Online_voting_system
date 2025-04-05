from django.shortcuts import render

def index(request):
    return render(request, 'Online_voting_system/index.html')