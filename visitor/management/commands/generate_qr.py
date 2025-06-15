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
            
            # Save to static directory
            static_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)
                
            # Delete existing QR code if it exists
            qr_path = os.path.join(static_dir, 'qr_code.png')
            if os.path.exists(qr_path):
                os.remove(qr_path)
                print("Deleted existing QR code")
                
            # Create image and save
            qr_image = qr.make_image(fill_color='black', back_color='white')
            qr_image.save(os.path.join(static_dir, 'qr_code.png'))
            
            # Also save to the static root directory for production
            if not settings.DEBUG:
                static_root_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'img')
                if not os.path.exists(static_root_dir):
                    os.makedirs(static_root_dir)
                qr_image.save(os.path.join(static_root_dir, 'qr_code.png'))
                
            print(f"QR code saved to: {os.path.join(static_dir, 'qr_code.png')}")
            print(f"QR code saved to: {os.path.join(static_root_dir, 'qr_code.png') if not settings.DEBUG else 'Development mode'}")
            
            self.stdout.write(self.style.SUCCESS('Successfully generated QR code'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating QR code: {e}'))
