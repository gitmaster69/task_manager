from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect


def index(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return render(request, 'home/index.html')


def about(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return render(request, 'home/about.html')


def view_404(request):
    # make a redirect to homepage
    # you can use the name of url or just the plain link
    # TODO create 404 page and redirect all error page to 404
    return redirect('/dashboard/')
