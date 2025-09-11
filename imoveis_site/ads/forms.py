from django import forms
from .models import WantedAd, Offer # Se Offer não existir, crie o modelo primeiro
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User 

class WantedAdForm(forms.ModelForm):
       class Meta:
           model = WantedAd
           fields = ['title', 'description', 'reward', 'category', 
                     'location', 'price', 'created_by', 'is_active']
           
class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Obrigatório. Digite um email válido.")
    first_name = forms.CharField(max_length=30, required=True, help_text="Nome")
    last_name = forms.CharField(max_length=30, required=True, help_text="Sobrenome")
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customizar labels e placeholders
        self.fields['username'].help_text = "Obrigatório. 150 caracteres ou menos. Apenas letras, dígitos e @/./+/-/_ ."
        self.fields['password1'].help_text = "Sua senha deve ter pelo menos 8 caracteres."
        
        # Adicionar classes CSS
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

