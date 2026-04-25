from userauths.models import Profile
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class EditProfileForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'flowzi-input', 'placeholder': 'First name'}), required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'flowzi-input', 'placeholder': 'Last name'}), required=False)
    location = forms.CharField(widget=forms.TextInput(attrs={'class': 'flowzi-input', 'placeholder': 'Location'}), required=False)
    url = forms.CharField(widget=forms.TextInput(attrs={'class': 'flowzi-input', 'placeholder': 'Portfolio or website'}), required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'flowzi-textarea', 'placeholder': 'Tell people what you create on Flowzi', 'rows': 4}), required=False)

    class Meta:
        model = Profile
        fields = ['image', 'first_name', 'last_name', 'location', 'url', 'bio']

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'flowzi-input'}), max_length=50, required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'flowzi-input'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Create password', 'class': 'flowzi-input'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'flowzi-input'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
