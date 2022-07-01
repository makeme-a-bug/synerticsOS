from django.shortcuts import render,redirect
from django.contrib.auth import authenticate , login , logout

from .forms import LoginForm , UserForm

def loginView(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user:
                login(request,user)
                return redirect("delivery:deliveries")
        else:
            return render(request,'account/login.html',{'form':form})  

    return render(request,"account/login.html",{'form':form})



def account(request):
    form = UserForm(initial={'email':request.user.email,'first_name':request.user.first_name,'last_name':request.user.last_name})
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
    return render(request,"account/account.html",{'form':form})
