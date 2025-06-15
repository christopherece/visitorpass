from django.contrib import admin
from .models import PersonToVisit, Visitor, QRCode

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'person_to_visit', 'login_date','signout_date', 'is_signin')
    list_filter = ('person_to_visit',)
    search_fields = ('name', 'email')

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('url', 'created_at', 'updated_at')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')
        return "No image"
    image_preview.short_description = 'QR Code Preview'

admin.site.register(PersonToVisit)
