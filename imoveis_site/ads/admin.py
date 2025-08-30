from django.contrib import admin # type: ignore
from .models import Category, WantedAd

admin.site.register(Category)
admin.site.register(WantedAd)