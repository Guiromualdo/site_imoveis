from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import io
from django.core.files.base import ContentFile


class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class WantedAd(models.Model):
       title = models.CharField(max_length=200, verbose_name="Título do Anúncio")
       description = models.TextField(verbose_name="Descrição")
       reward = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Recompensa", blank=True, null=True)
       category = models.CharField(max_length=100, verbose_name="Categoria", blank=True, null=True)  # Novo campo
       location = models.CharField(max_length=200, verbose_name="Localização", blank=True, null=True)  # Novo campo
       price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço", blank=True, null=True)  # Novo campo
       created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criado por")
       created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
       updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
       is_active = models.BooleanField(default=True, verbose_name="Ativo")

       class Meta:
           verbose_name = "Anúncio de Procurado"
           verbose_name_plural = "Anúncios de Procurados"

       def __str__(self):
           return self.title

class Offer(models.Model):
    wanted_ad = models.ForeignKey(WantedAd, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Oferta para {self.wanted_ad.title}'
    
class Anuncio(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class AdImage(models.Model):
       ad = models.ForeignKey(WantedAd, on_delete=models.CASCADE, related_name="images", verbose_name="Anúncio")
       image = models.ImageField(upload_to="wanted_ads/%Y/%m/%d/", verbose_name="Imagem")
       caption = models.CharField(max_length=200, blank=True, verbose_name="Legenda")
       uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")

       class Meta:
           verbose_name = "Imagem do Anúncio"
           verbose_name_plural = "Imagens dos Anúncios"

       def __str__(self):
           return f"Imagem de {self.ad.title}"

       def save(self, *args, **kwargs):
           super().save(*args, **kwargs)
           if self.image:
               img = Image.open(self.image.path)
               if img.height > 800 or img.width > 800:
                   output_size = (800, 800)
                   img.thumbnail(output_size, Image.Resampling.LANCZOS)
                   buffer = io.BytesIO()
                   img.save(buffer, format=img.format)
                   buffer.seek(0)
                   self.image.save(self.image.name, ContentFile(buffer.getvalue()), save=False)
                   super().save(*args, **kwargs)   