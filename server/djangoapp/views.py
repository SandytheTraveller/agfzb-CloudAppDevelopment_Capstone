from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarDealer, CarModel, DealerReview
# from .restapis import related methods
from .restapis import get_dealer_reviews_from_cf, get_dealers_from_cf

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required  # For authentication checks
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

def index(request):
    return render(request, 'djangoapp/index.html')

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully.")
                return redirect('djangoapp:index')  # Redirect to the home page after successful login
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'djangoapp/login.html', {'form': form})

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return render(request, 'djangoapp/logout.html')
# Create a `registration_request` view to handle sign up request
# def registration_request(request):

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}. You can now log in.")
            return redirect('djangoapp:login_view')
        else:
            # Debugging output
            print(form.errors)  # You can also log this information
    else:
        form = UserCreationForm()
    return render(request, 'djangoapp/registration.html', {'form': form})

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/b81143fb-ebf7-455a-b7a0-fe558100017e/default/getDealerships"
        # Get dealers from the URL
        dealerships = CarDealer.objects.all()
        # Concat all dealer's short name
        context = {
            "dealerships": dealerships  # Updated context variable name
        }

        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...



def get_dealer_details(request, dealer_id):
    api_key = 'NgRnMOGD9aZZbFEGJI9B_6EoOc4lYsHbjHXRPEOcKAyx'
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/b81143fb-ebf7-455a-b7a0-fe558100017e/default/getReviewsForDealership?dealerId=13"
    
    if request.method == "GET":
        # Get reviews for the dealer with the specified ID
        reviews = get_dealer_reviews_from_cf(url, dealer_id, api_key)
        
        context = {
            "reviews": reviews
        }
        
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

def add_review(request, dealer_id):
    if request.method == 'GET':
        # Query cars with the dealer id to be reviewed
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        
        # Append the queried cars into context
        context = {
            'cars': cars,
            'dealer_id': dealer_id,
        }
        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == 'POST':
        dealer_id = request.POST.get('dealer_id')  # You may need to retrieve dealer_id from the form or URL
        review_content = request.POST.get('content')
        purchased = request.POST.get('purchasecheck')
        car_id = request.POST.get('car')
        purchasedate = request.POST.get('purchasedate')

        # Use datetime.utcnow().isoformat() to format the review time
        review_time = datetime.utcnow().isoformat()

        # Use car.year.strftime("%Y") to get the year from the date field
        car = CarModel.objects.get(id=car_id)
        purchase_year = car.year.strftime("%Y")

        # Create a DealerReview object and save it to the database
        review = DealerReview(
            dealership=dealer_id,
            name="Your User Name",  # Replace with user authentication if available
            purchase=(purchased == 'on'),  # Convert checkbox input to a boolean
            review=review_content,
            purchase_date=purchasedate,
            car_make=car.make.name,
            car_model=car.name,
            car_year=purchase_year,
            sentiment="Unknown",
        )
        review.save()

        # Redirect to the dealer details page for the dealer_id
        return redirect('djangoapp:dealer_details', dealer_id=dealer_id)

    return HttpResponse("Invalid request method")