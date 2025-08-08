from django import forms
from .models import Newsletter

class NewsletterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': True
        })
    )
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name (Optional)'
        })
    )
    language_preference = forms.ChoiceField(
        choices=[('en', 'English'), ('sw', 'Swahili')],
        initial='en',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if Newsletter.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError('This email is already subscribed.')
        return email