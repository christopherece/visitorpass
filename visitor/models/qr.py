from django.db import models
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import base64

class QRCode(models.Model):
    url = models.URLField(default='https://visitorpass.topitsolutions.co.nz/')
    image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_qr(self):
        """Generate and save QR code image"""
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.url)
            qr.make(fit=True)
            
            # Create image
            qr_image = qr.make_image(fill_color='black', back_color='white')
            
            # Save to BytesIO
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            
            # Save to model
            self.image.save(
                'qr_code.png',
                ContentFile(buffer.getvalue()),
                save=False
            )
            self.save()
            
            print(f"QR code generated and saved to database")
            
        except Exception as e:
            print(f"Error generating QR code: {e}")

    @classmethod
    def get_or_create_qr(cls):
        """Get existing QR code or create a new one"""
        try:
            # Try to get existing QR code
            qr = cls.objects.first()
            if not qr:
                # Create new QR code if none exists
                qr = cls.objects.create()
                qr.generate_qr()
            elif not qr.image:
                # Regenerate if image is missing
                qr.generate_qr()
            return qr
        except Exception as e:
            print(f"Error getting or creating QR code: {e}")
            return None
