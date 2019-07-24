from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import SignupForm


def signup(request):
    if request.user.is_authenticated:
        return redirect(reverse('dashboard'))

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect(reverse('login'))
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {'form': form})
