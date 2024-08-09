from django.http import HttpResponse
from django.shortcuts import render


def heartbeat(request):
    return HttpResponse("alive")


def home(request):
    return render(request,'home.html')