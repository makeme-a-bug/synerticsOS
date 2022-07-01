from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email,EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import SetPasswordForm,PasswordChangeForm
from django.contrib.auth import password_validation

from .models import User
class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254,widget=forms.EmailInput(
            attrs={
                'class':'form-control',
            }
        ))
    password = forms.CharField(widget=forms.PasswordInput(attrs = {'class':'form-control'}))
    
    def clean(self):
 
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if len(email) < 1:
            raise forms.ValidationError('Enter correct email')
        if not password and not email :
            raise forms.ValidationError('You have to write something!')
        user =  authenticate(email = email , password = password)

        if user == None: 
            raise forms.ValidationError('Email or Password is incorrect')

        return self.cleaned_data




class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ["password",'groups' , 'user_permissions','is_active','is_staff','is_superuser','last_login','date_joined','email']

