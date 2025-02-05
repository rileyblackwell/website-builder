from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.landing_page, name='landing_page'),
    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_page, name='contact'),
    
    # Policy pages
    path('privacy/', views.privacy_page, name='privacy_page'),
    path('terms/', views.terms_page, name='terms_page'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
]

