from django.shortcuts import render


def home_view(request):
    context = {
        'name': request.user or None
    }
    return render(request, 'home.html', context)
