# visitor/forms.py
from django import forms
from .models import PersonToVisit, Visitor
from datetime import date


class VisitorLoginForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Hidden field to store the selected person_to_visit ID
    person_to_visit_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    # Text input for searching staff
    person_to_visit_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type to search for staff...',
            'autocomplete': 'off'
        })
    )
    # The actual ModelChoiceField (hidden from the user)
    person_to_visit = forms.ModelChoiceField(
        queryset=PersonToVisit.objects.all(),
        required=True,
        widget=forms.HiddenInput()
    )
    # Updated submit method to handle form submission and save data
    def submit(self):
        if self.is_valid():
            # email = self.cleaned_data['email']
            name = self.cleaned_data['name']
            person_to_visit = self.cleaned_data['person_to_visit']

             # Check if a visitor with the same email exists for today
            today = date.today()
            existing_visitor = Visitor.objects.filter(name=name, created_at__date=today).first()

            # if existing_visitor:
            #     # If a visitor with the same email exists for today, you can handle this case as needed.
            #     # For example, return a message or prevent the submission.
            #     return None
            
            # Create a new Visitor instance and save it to the database
            visitor, created = Visitor.objects.get_or_create(name=name, person_to_visit=person_to_visit)
            return visitor  # Return the visitor instance if needed
        return None  # Return None if form is not valid
        
