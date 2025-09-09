from django import forms
from .models import WantedAd, Offer  # Se Offer não existir, crie o modelo primeiro

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


