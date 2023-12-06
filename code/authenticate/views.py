from django.shortcuts import render, redirect
from .forms import SignUpForm
from app.models import User
from app.utility import only_executeSQL, encoder_22_characters

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            
            email = form.cleaned_data['email']
            name = form.cleaned_data['username']
            age = form.cleaned_data['age']
            instance = form.save()
            id = instance.id
            # Insert into GCP table
            sql = f"INSERT INTO user (id, email, name, age) VALUES ('{id}', '{email}', '{name}', '{age}')"
            res = only_executeSQL(sql)
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

