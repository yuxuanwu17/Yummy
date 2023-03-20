from django.shortcuts import render

# Create your views here.
def global_action(request):
    return render(request, 'Yummy/base.html', {})