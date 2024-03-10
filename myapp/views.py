from django.shortcuts import render, redirect
from .models import destination  # Update the import
from .forms import RatingForm  # Create a form for rating (see next step)
from django.shortcuts import render, get_object_or_404, redirect
from .models import destination, Rating
from django.db import models
from django.db.models import Q
from django.db.models import Value, FloatField
from django.db.models import Count
import numpy as np
import re
import math
from collections import Counter


# Create your views here.

def create_places(request):
    if request.method == "POST":
        data = request.POST
        name = data.get('name')
        location = data.get('location')
        description = data.get('description')
        keywords = data.get('keywords')
        image = data.get('image')
        homeImage = request.FILES.get('homeImage')
        destination.objects.create(  # Update the model name
            name=name,
            location=location,
            description=description,
            keywords=keywords,
            image=image,
            homeImage = homeImage
        )
    return render(request, 'places.html', )
from django.shortcuts import render
from .models import destination
from django.db.models import Avg

from django.shortcuts import render
from django.db.models import Q
from .models import destination
def get_all_places(request):
    queryset = destination.objects.all()
    sorted_queryset = quicksort(queryset)
    context = {'destinations': sorted_queryset}
    return render(request, 'list.html', context=context)


def places(request):
    queryset = destination.objects.all()

    # Sorting logic (default sorting order)
    sorted = quicksort(queryset)
    sorted_queryset = sorted[:8]

    user = request.user if request.user.is_authenticated else None

    if request.GET.get('search'):
        search_term = request.GET.get('search')
        search_terms = search_term.split()

        # Create a Q object for each term and combine them with the | (OR) operator
        query = Q()
        for term in search_terms:
            query |= Q(keywords__icontains=term)

        # Apply the filter to the queryset
        queryset = queryset.filter(query)
        sorted_queryset = quicksort(queryset)

        context = {'destinations': sorted_queryset, 'user': user, 'terms':search_term}
        return render(request, 'home.html', context=context)

    context = {'destinations': sorted_queryset, 'user': user}
    return render(request, 'index.html', context=context)

def quicksort(arr):
    if len(arr) <= 1:
        return arr  # Already sorted

    # Call the method to get the average rating
    pivot = arr[len(arr) // 2].average_rating()
    left = [x for x in arr if x.average_rating() > pivot]
    middle = [x for x in arr if x.average_rating() == pivot]
    right = [x for x in arr if x.average_rating() < pivot]

    return quicksort(left) + middle + quicksort(right)

def delete_destination(request,id):
    queryset = destination.objects.get(id=id)
    queryset.delete()
    return redirect('/create-destination')


def update_destination(request, id):
    queryset = destination.objects.get(id=id)

    if request.method == "POST":
        data = request.POST
        name = data.get('name')
        location = data.get('location')
        description = data.get('description')
        keywords = data.get('keywords')
        image = data.get('image')
        queryset.name = name
        queryset.location = location
        queryset.description = description
        queryset.keywords = keywords
        queryset.image = image
        print(data)
        queryset.save()
        return redirect('/')

    context = {'destinations': queryset, 'user': request.user}
    print(queryset.description)
    return render(request, 'update_place.html', context=context)






'''def rate_destination(request, destination_id):
    destination_instance = get_object_or_404(destination, id=destination_id)
    user = request.user

    # Check if the user has already rated the destination
    existing_rating = Rating.objects.filter(user=user, location=destination_instance).first()

    if existing_rating:
        # If the user has already rated, you might want to handle this case
        # For now, let's redirect them back to the destination page
        already_rated = True
        return render(request, 'rate_destination.html', {'destination': destination_instance, 'already_rated': already_rated})

    if request.method == 'POST':
        form = request.get('name')
        rating = form.cleaned_data['rating']
        print('rating:',rating)
        Rating.objects.create(user=user, location=destination_instance, rating=rating)

    context = {'destination': destination_instance, 'rating': rating}
    return render(request, 'details.html', context)
'''



def rate_destination(request, destination_id):
    destination_instance = get_object_or_404(destination, id=destination_id)
    user = request.user
    rating = None  # Initialize rating

    if request.method == 'POST':
        # Assuming your form field is named 'rating' in the HTML form
        rating_value = request.POST.get('rating')

        if rating_value is not None:
            # You may want to perform additional validation on the rating_value
            rating = int(rating_value)
            print('rating:',rating)
            Rating.objects.create(user=user, location=destination_instance, rating=rating)

    context = {'destination': destination_instance, 'rating': rating}
    return render(request, 'details.html', context)


def get_cosine_similarity(vector1, vector2):
    counter1 = text_to_vector(vector1)
    counter2 = text_to_vector(vector2)

    intersection = set(counter1.keys()) & set(counter2.keys())
    numerator = sum([counter1[x] * counter2[x] for x in intersection])

    sum1 = sum([counter1[x] ** 2 for x in counter1.keys()])
    sum2 = sum([counter2[x] ** 2 for x in counter2.keys()])

    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator
def get_details(request, destination_id):
    current_destination = destination.objects.get(id=destination_id)
    current_keywords = current_destination.keywords.split(', ')

    all_destinations = destination.objects.exclude(id=destination_id)

    similar_destinations = []
    for i, sim_destination in enumerate(all_destinations):
        similar_keywords = sim_destination.keywords.split(', ')
        sim_score = get_cosine_similarity(current_keywords, similar_keywords)
        print(sim_score)
        similar_destinations.append({'destination': sim_destination, 'similarity': sim_score})
    print(similar_destinations)
    # Sort destinations by similarity in descending order
    similar_destinations = sorted(similar_destinations, key=lambda x: x['similarity'], reverse=True)
    print(similar_destinations)
    destination_objects = [item['destination'] for item in similar_destinations[:4]]
    print(destination_objects)
    context = {'destination': current_destination, 'similar_destinations': destination_objects}
    return render(request, 'details.html', context)

def text_to_vector(text):
    keywords = re.split(r'\s*,\s*', text[0])  # Access the first element of the list
    return Counter(keywords)












