# visitor/views.py
from django.shortcuts import render, redirect
from .forms import VisitorLoginForm
from .models import Visitor
from django.core.mail import send_mail
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


def dashboard(request):
    return render(request, 'visitor/dashboard.html')

def logout(request, id):
    obj = get_object_or_404(Visitor, id=id)  # Use get_object_or_404 to handle not found cases
    
    if request.method == 'POST':
        
        obj.is_signin = False
        obj.signout_date = datetime.now()
        obj.save()
            
        messages.success(request, "You have successfully logged out.")
        return redirect('dashboard')
    
    return redirect('dashboard')
    

def signout_visitor(request):
    visitors = Visitor.objects.filter(is_signin=True).order_by('-login_date')
    context = {
        'visitors':visitors,
        'login_date':'login_date'
    }
    return render(request, 'visitor/signout.html', context)

def login_visitor(request):
    if request.method == 'POST':
        form = VisitorLoginForm(request.POST)
        
        if form.is_valid():
            # email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            person_to_visit = form.cleaned_data['person_to_visit']
            staff_email = person_to_visit.email
            visitor, created = Visitor.objects.get_or_create(name=name, person_to_visit=person_to_visit)
            send_mail(
                'You Have a Visitor',
                name + ' is waiting for you at the Reception.',
                'balaydalakay@gmail.com',
                [staff_email, 'christopheranchetaece@gmail.com'],
                fail_silently=False
            )
            return render(request, 'visitor/welcome.html', {'name': name})
    else:
        form = VisitorLoginForm()
    return render(request, 'visitor/login.html', {'form': form})

def welcome(request):
    return render(request, 'visitor/welcome.html')
