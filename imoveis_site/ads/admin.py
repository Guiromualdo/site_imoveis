from django.contrib import admin  # type: ignore
from .models import Category, WantedAd, AdImage

class AdImageInline(admin.TabularInline):
    model = AdImage
    extra = 1
    fields = ('image', 'caption')

class WantedAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    inlines = [AdImageInline]

admin.site.register(Category)
admin.site.register(WantedAd, WantedAdAdmin)
admin.site.register(AdImage)