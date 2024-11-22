from django.shortcuts import render
from visitor.models import Visitor
from django.db.models import Count
import json

def index(request):
    labels = []  # This will hold the names of the people being visited (x-axis)
    data = []    # This will hold the count of visits for each person (y-axis)

    # Query to count the number of visits for each 'person_to_visit'
    queryset = Visitor.objects.values('person_to_visit__name') \
                               .annotate(visit_count=Count('person_to_visit')) \
                               .order_by('-visit_count')

    # Prepare labels and data for the chart
    for entry in queryset:
        labels.append(entry['person_to_visit__name'])  # The name of the person being visited (x-axis label)
        data.append(entry['visit_count'])  # Count of visits for this person (y-axis value)

    return render(request, 'report/index.html', {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    })
