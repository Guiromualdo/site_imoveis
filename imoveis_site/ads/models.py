from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
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
       category = models.CharField(max_length=100, verbose_name="Categoria", blank=True, null=True)
       location = models.CharField(max_length=200, verbose_name="Localização", blank=True, null=True)
       price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço", blank=True, null=True)
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

# =============================================================================
# MODELOS DO SISTEMA DE CHAT
# =============================================================================

class ChatRoom(models.Model):
    """Sala de chat entre um anunciante e um interessado"""
    ad = models.ForeignKey(WantedAd, on_delete=models.CASCADE, related_name='chat_rooms', verbose_name="Anúncio")
    participant_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_p1', verbose_name="Participante 1")
    participant_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_p2', verbose_name="Participante 2")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        unique_together = ['ad', 'participant_1', 'participant_2']
        verbose_name = "Sala de Chat"
        verbose_name_plural = "Salas de Chat"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat: {self.ad.title} - {self.participant_1.username} & {self.participant_2.username}"
    
    @classmethod
    def get_or_create_room(cls, ad, user1, user2):
        """Busca uma sala existente ou cria uma nova"""
        try:
            # Tenta encontrar uma sala existente (em qualquer ordem dos participantes)
            room = cls.objects.get(
                Q(ad=ad, participant_1=user1, participant_2=user2) |
                Q(ad=ad, participant_1=user2, participant_2=user1)
            )
            return room, False
        except cls.DoesNotExist:
            # Cria uma nova sala
            room = cls.objects.create(
                ad=ad,
                participant_1=user1,
                participant_2=user2
            )
            return room, True
    
    def get_other_participant(self, user):
        """Retorna o outro participante do chat"""
        if user == self.participant_1:
            return self.participant_2
        return self.participant_1
    
    def get_last_message(self):
        """Retorna a última mensagem do chat"""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count_for_user(self, user):
        """Retorna o número de mensagens não lidas para um usuário"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

class ChatMessage(models.Model):
    """Mensagem individual do chat"""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name="Sala de Chat")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Remetente")
    message = models.TextField(verbose_name="Mensagem")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviado em")
    is_read = models.BooleanField(default=False, verbose_name="Lida")
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}..."
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualiza o timestamp da sala de chat quando uma nova mensagem é criada
        self.chat_room.updated_at = timezone.now()
        self.chat_room.save(update_fields=['updated_at'])