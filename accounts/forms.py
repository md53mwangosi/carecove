
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Address

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = [
            'phone', 'birth_date', 'default_billing_address_1', 'default_billing_address_2',
            'default_billing_city', 'default_billing_state', 'default_billing_postal_code',
            'default_billing_country', 'default_shipping_address_1', 'default_shipping_address_2',
            'default_shipping_city', 'default_shipping_state', 'default_shipping_postal_code',
            'default_shipping_country', 'preferred_language', 'receive_newsletter',
            'receive_order_updates'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'default_billing_address_1': forms.TextInput(attrs={'class': 'form-control'}),
            'default_billing_address_2': forms.TextInput(attrs={'class': 'form-control'}),
            'default_billing_city': forms.TextInput(attrs={'class': 'form-control'}),
            'default_billing_state': forms.TextInput(attrs={'class': 'form-control'}),
            'default_billing_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'default_billing_country': forms.TextInput(attrs={'class': 'form-control'}),
            'default_shipping_address_1': forms.TextInput(attrs={'class': 'form-control'}),
            'default_shipping_address_2': forms.TextInput(attrs={'class': 'form-control'}),
            'default_shipping_city': forms.TextInput(attrs={'class': 'form-control'}),
            'default_shipping_state': forms.TextInput(attrs={'class': 'form-control'}),
            'default_shipping_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'default_shipping_country': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_language': forms.Select(attrs={'class': 'form-control'}),
            'receive_newsletter': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_order_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'type', 'first_name', 'last_name', 'company', 'address_1', 'address_2',
            'city', 'state', 'postal_code', 'country', 'phone', 'is_default'
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'address_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
