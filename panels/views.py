from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'panels.html', {'is_panels': True})

def apply(request):
    return render(request, 'panels-apply.html', {'is_panels': True})
