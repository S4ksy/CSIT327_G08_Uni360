from django.shortcuts import render
from django.http import HttpResponse   # 👈 add this line

def home(request):
    return HttpResponse("Welcome to Uni360 POS System 🚀")