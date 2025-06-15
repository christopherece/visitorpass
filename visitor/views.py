# visitor/views.py
from django.shortcuts import render, redirect
from .forms import VisitorLoginForm
from .models import Visitor
from django.core.mail import send_mail
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
import qrcode
from io import BytesIO
import base64
from django.conf import settings


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

def login(request):
    # Generate QR code with the current server URL
    try:
        # Always use the domain name for QR code URL
        domain = 'visitorpass.topitsolutions.co.nz'
        protocol = 'https'
        full_url = f'{protocol}://{domain}/'
        print(f"QR code generated with URL: {full_url}")
        
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
        
        # Get the static files directory
        static_dir = os.path.join(settings.STATIC_ROOT, 'img')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        # Save the QR code
        qr_image.save(os.path.join(static_dir, 'qr_code.png'))
        
        # Also save to the source directory for development
        qr_image.save('visitorpass/static/img/qr_code.png')
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
                # Try to send email, but don't let SSL errors prevent login
                try:
                    send_mail(
                        'You Have a Visitor',
                        f'{visitor.name} is waiting for you at the Reception.',
                        'balaydalakay@gmail.com',
                        [visitor.person_to_visit.email, 'christopheranchetaece@gmail.com'],
                        fail_silently=True
                    )
                except Exception as e:
                    print(f"Email sending failed: {e}")
                
                return render(request, 'visitor/welcome.html', {'name': visitor.name})
    else:
        form = VisitorLoginForm()
    
    return render(request, 'visitor/login.html', {
        'form': form,
        'success_message': success_message
    })

def login_visitor(request):
    if request.method == 'POST':
        form = VisitorLoginForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data['name']
            person_to_visit = form.cleaned_data['person_to_visit']
            staff_email = person_to_visit.email
            visitor, created = Visitor.objects.get_or_create(name=name, person_to_visit=person_to_visit)
            
            # Try to send email, but don't let SSL errors prevent login
            try:
                send_mail(
                    'You Have a Visitor',
                    name + ' is waiting for you at the Reception.',
                    'balaydalakay@gmail.com',
                    [staff_email, 'christopheranchetaece@gmail.com'],
                    fail_silently=True  # Changed to True to prevent errors from breaking the flow
                )
            except Exception as e:
                # Log the error but continue with the login process
                print(f"Email sending failed: {e}")
                
            return render(request, 'visitor/welcome.html', {'name': name})
    else:
        form = VisitorLoginForm()
    return render(request, 'visitor/login.html', {'form': form})

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
