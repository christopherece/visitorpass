from django.core.management.base import BaseCommand
from django.conf import settings
import os
import qrcode


class Command(BaseCommand):
    help = 'Generate QR code for the login page'

    def handle(self, *args, **options):
        try:
            # Create static directory if it doesn't exist
            static_dir = os.path.join(settings.STATIC_ROOT, 'img')
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)

            # Always use the domain name for QR code URL
            domain = 'visitorpass.topitsolutions.co.nz'
            protocol = 'https'
            full_url = f'{protocol}://{domain}/'
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(full_url)
            qr.make(fit=True)
            
            # Create image and save
            qr_image = qr.make_image(fill_color='black', back_color='white')
            qr_image.save(os.path.join(static_dir, 'qr_code.png'))
            
            # Also save to development directory
            dev_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
            if not os.path.exists(dev_dir):
                os.makedirs(dev_dir)
            qr_image.save(os.path.join(dev_dir, 'qr_code.png'))
            
            self.stdout.write(self.style.SUCCESS('Successfully generated QR code'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating QR code: {e}'))
