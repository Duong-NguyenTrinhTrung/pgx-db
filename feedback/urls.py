# urls.py
from django.urls import path
from .views import submit_contact_form

urlpatterns = [
    path('questions_to_pgx/', submit_contact_form, name='questions-pgx'),
    # Add other URL patterns as needed
]
