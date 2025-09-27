from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse,JsonResponse


def http_test(request):    
    return HttpResponse('<h1>http-test</h1>')

def json_test(request):
    return JsonResponse({'name':'AmirhoseinRamezani'})
