from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from main.forms import SearchForm
from main.services import get_photos

# Create your views here.
def index(request):
    tmpl_vars = {
      'form': SearchForm()
    }
    return render(request, "main/index.html", tmpl_vars)

def about(request):
    return HttpResponse('Educ-8 is a cool site made by cool people.')

def coming_soon(request):
    return HttpResponse('Coming soon!')

def search(request):
    if request.method == 'GET':
        search_term = request.GET["search_term"]
        result = get_photos(search_term)
        return JsonResponse(result, safe=False)
