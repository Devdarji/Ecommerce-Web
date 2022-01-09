from django import forms
from django.contrib.auth import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, fields
from shop.models import Profile, ShippingAddress

class CreateUserForm(UserCreationForm):

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(
                "The given email is already registered")
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']

    # first_name = forms.CharField(max_length=50)
    # last_name = forms.CharField(max_length=50)
    # mobile_no = forms.CharField(max_length=14)
    # alternate_mobile_no = forms.CharField(max_length=14, required=False)
    address_line1 = forms.CharField(max_length=100)
    address_line2 = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=30)
    state = forms.CharField(max_length=30)
    city = forms.CharField(max_length=30)
    zipcode = forms.CharField(max_length=10)

