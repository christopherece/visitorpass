# visitor/views.py
from django.shortcuts import render, redirect
from .forms import VisitorLoginForm
from .models import Visitor, QRCode
from django.core.mail import send_mail
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
import requests
import json


def logout(request, id):
    obj = get_object_or_404(Visitor, id=id)  # Use get_object_or_404 to handle not found cases
    
    if request.method == 'POST':
        
        obj.is_signin = False
        obj.signout_date = datetime.now()
        obj.save()
            
        # Store success message in session
        request.session['success_message'] = "Successfully logged out!"
        return redirect('login', permanent=False)
    
    return redirect('dashboard')
    

def signout_visitor(request):
    visitors = Visitor.objects.filter(is_signin=True).order_by('-login_date')
    context = {
        'visitors':visitors,
        'login_date':'login_date'
    }
    return render(request, 'visitor/signout.html', context)

def login_visitor(request):
    try:
        # Get or create QR code
        qr = QRCode.get_or_create_qr()
        if not qr:
            print("Failed to get or create QR code")
            return render(request, 'visitor/login.html', {
                'error': 'Failed to generate QR code'
            })
            
        print(f"QR code URL: {qr.url}")
        print(f"QR code image path: {qr.image.url if qr.image else 'No image'}")
        
        # Pass QR code to template
        context = {'qr': qr}
        
        # Rest of your login logic...
        if request.method == 'POST':
            form = VisitorLoginForm(request.POST)
            if form.is_valid():
                visitor = form.save()
                if visitor:
                    try:
                        send_mail(
                            'You Have a Visitor',
                            f'{visitor.name} is waiting for you at the Reception.',
                            settings.EMAIL_HOST_USER,
                            [visitor.person_to_visit.email, 'christopheranchetaece@gmail.com'],
                            fail_silently=False
                        )
                        print("Email sent successfully!")
                    except Exception as e:
                        print(f"Email sending failed: {str(e)}")
                        messages.error(request, f"Failed to send email notification: {str(e)}")
                    
                    # === Send Print Request to Ubuntu Server ===
                    try:
                        # First test if print service is running
                        print("\n=== Testing Print Service ===")
                        test_url = "http://192.168.10.57:8001/printers"
                        test_response = requests.get(test_url)
                        print(f"Printers endpoint response: {test_response.text}")
                        
                        # Prepare print data
                        print_data = {
                            "printer_port": "/dev/usb/lp0",  # Default USB port for Brother QL-700
                            "content": f"Visitor: {visitor.name}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                        
                        def print_visitor_label(visitor_name):
                            """Print a label for the visitor using the print service"""
                            try:
                                # Print service URL - Ubuntu server
                                print_service_url = 'http://192.168.10.57:8001'
                                
                                # Prepare the print data with text
                                print_data = {
                                    'printer_port': '/dev/usb/lp0',
                                    'content': f"Visitor: {visitor_name}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                }
                                
                                # Send request to print service
                                response = requests.post(
                                    f"{print_service_url}/print",
                                    json=print_data,
                                    timeout=10
                                )
                                
                                if response.status_code == 200:
                                    return True
                                else:
                                    print(f"Print service error: {response.text}")
                                    return False
                            except Exception as e:
                                print(f"Error printing label: {str(e)}")
                                return False

                        if print_visitor_label(visitor.name):
                            print(f"🖨️ Label sent to Brother QL-700 printer successfully.")
                        else:
                            print(f"❌ Print server error")
                            messages.error(request, f"Failed to print visitor label")
                            # Log the error to a file as well
                            with open('print_errors.log', 'a') as f:
                                f.write(f"\n=== Print Error ===\n")
                                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                f.write(f"Error: {print_response.text}\n")
                                f.write("==================\n")
                        
                        # Log the print attempt
                        print(f"\n=== Print Details ===")
                        print(f"Printer Port: /dev/usb/lp0")
                        print(f"Content: {print_data['content']}")
                        print("-" * 40)
                        
                    except Exception as e:
                        print(f"❌ Could not print: {str(e)}")
                        import traceback
                        print("Full traceback:")
                        print(traceback.format_exc())
                        messages.error(request, f"Failed to print visitor label: {str(e)}")
                        # Log the error to a file as well
                        with open('print_errors.log', 'a') as f:
                            f.write(f"\n=== Print Error ===\n")
                            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"Error: {str(e)}\n")
                            f.write(f"Full traceback:\n{traceback.format_exc()}\n")
                            f.write("==================\n")
                    
                    return render(request, 'visitor/welcome.html', {'name': visitor.name})
        else:
            form = VisitorLoginForm()
            
        context['form'] = form
        return render(request, 'visitor/login.html', context)
    except Exception as e:
        print(f"Error in login_visitor: {str(e)}")
        return render(request, 'visitor/login.html', {'error': str(e)})
        
        # Log request details for debugging
        print("\n=== Request Details ===")
        print(f"Host: {request.get_host()}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Meta: {dict(request.META)}")
        print(f"Scheme: {request.scheme}")
        print(f"Is secure: {request.is_secure()}")
        print(f"Path: {request.path}")
        print("=======================")
        
        # Delete existing QR code if it exists
        import os
        
        # Get the correct static files directory
        static_dir = os.path.join(BASE_DIR, 'static', 'img')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            
        # Delete existing QR code if it exists
        qr_path = os.path.join(static_dir, 'qr_code.png')
        if os.path.exists(qr_path):
            os.remove(qr_path)
            print("Deleted existing QR code")
            
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)
        
        # Create image and save to file
        qr_image = qr.make_image(fill_color='black', back_color='white')
        
        # Save the QR code
        qr_image.save(os.path.join(static_dir, 'qr_code.png'))
        
        # Also save to the static root directory for production
        if not DEBUG:
            static_root_dir = os.path.join(BASE_DIR, 'staticfiles', 'img')
            if not os.path.exists(static_root_dir):
                os.makedirs(static_root_dir)
            qr_image.save(os.path.join(static_root_dir, 'qr_code.png'))
            
        print(f"QR code saved to: {os.path.join(static_dir, 'qr_code.png')}")
        print(f"QR code saved to: {os.path.join(static_root_dir, 'qr_code.png') if not DEBUG else 'Development mode'}")
        
        # Save the QR code to both locations
        qr_image.save(os.path.join(static_dir, 'qr_code.png'))
        
        # Also save to the source directory
        source_dir = os.path.join(BASE_DIR, 'visitorpass', 'static', 'img')
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)
        qr_image.save(os.path.join(source_dir, 'qr_code.png'))
        
        # Log the file paths
        print(f"QR code saved to: {os.path.join(static_dir, 'qr_code.png')}")
        print(f"QR code saved to: {os.path.join(source_dir, 'qr_code.png')}")
        print(f"QR code generated with URL: {full_url}")
    except Exception as e:
        print(f"Error generating QR code: {e}")
    
    # Check if there's a success message in the session
    success_message = request.session.pop('success_message', None)
    
    if request.method == 'POST':
        form = VisitorLoginForm(request.POST)
        if form.is_valid():
            visitor = form.save()
            if visitor:
                # Try to send email with detailed logging
                try:
                    print("\n=== Email Sending Attempt ===")
                    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"From: {settings.EMAIL_HOST_USER}")
                    print(f"To: {visitor.person_to_visit.email}, christopheranchetaece@gmail.com")
                    print(f"Subject: You Have a Visitor")
                    print(f"Body: {visitor.name} is waiting for you at the Reception.")
                    print(f"SMTP Server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
                    print(f"Use TLS: {settings.EMAIL_USE_TLS}")
                    print("============================")
                    
                    # Create email message
                    from django.core.mail import EmailMessage
                    email = EmailMessage(
                        'You Have a Visitor',
                        f'{visitor.name} is waiting for you at the Reception.',
                        settings.EMAIL_HOST_USER,
                        [visitor.person_to_visit.email, 'christopheranchetaece@gmail.com']
                    )
                    
                    # Send email
                    email.send()
                    print("\n=== Email Sent Successfully ===")
                    print(f"Email sent to: {visitor.person_to_visit.email}, christopheranchetaece@gmail.com")
                    print("============================")
                    
                except Exception as e:
                    print("\n=== Email Sending Failed ===")
                    print(f"Error: {str(e)}")
                    import traceback
                    print("Full traceback:")
                    print(traceback.format_exc())
                    print("============================")
                    messages.error(request, f"Failed to send email notification: {str(e)}")
                    # Log the error to a file as well
                    with open('email_errors.log', 'a') as f:
                        f.write(f"\n=== Email Error ===\n")
                        f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Error: {str(e)}\n")
                        f.write(f"Full traceback:\n{traceback.format_exc()}\n")
                        f.write("==================\n")
                    
                    # Try sending email with fail_silently=True as a fallback
                    try:
                        print("\n=== Attempting fallback email send ===")
                        send_mail(
                            'You Have a Visitor',
                            f'{visitor.name} is waiting for you at the Reception.',
                            settings.EMAIL_HOST_USER,
                            [visitor.person_to_visit.email, 'christopheranchetaece@gmail.com'],
                            fail_silently=True
                        )
                        print("Fallback email sent successfully")
                    except Exception as e:
                        print(f"Fallback email failed: {str(e)}")
                        print("All email attempts failed")
                       
                
                return render(request, 'visitor/welcome.html', {'name': visitor.name})
    else:
        form = VisitorLoginForm()
    
    return render(request, 'visitor/login.html', {
        'form': form,
        'success_message': success_message
    })

def welcome(request):
    return render(request, 'visitor/welcome.html')

def search_staff(request):
    """
    AJAX view to search for staff members based on a query string
    """
    from django.http import JsonResponse
    from .models import PersonToVisit
    
    query = request.GET.get('query', '')
    if query:
        staff_members = PersonToVisit.objects.filter(name__icontains=query).values('id', 'name')
        return JsonResponse(list(staff_members), safe=False)
    return JsonResponse([], safe=False)
