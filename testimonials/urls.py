
from django.urls import path
from . import views

app_name = 'testimonials'

urlpatterns = [
    path('', views.testimonials_list, name='testimonials_list'),
    path('submit/', views.submit_testimonial, name='submit_testimonial'),
    path('thank-you/', views.testimonial_thank_you, name='testimonial_thank_you'),
]
