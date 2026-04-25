from django import forms
from FlowziApp.models import Post


class NewPostform(forms.ModelForm):

    picture = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'flowzi-file'}),
        required=True
    )
    caption = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'flowzi-textarea',
            'placeholder': 'Write a caption...',
            'rows': 3
        }),
        required=True
    )
    tags = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'flowzi-input',
            'placeholder': 'e.g. travel, food, design'
        }),
        required=True
    )

    class Meta:
        model = Post
        fields = ['picture', 'caption', 'tags']
