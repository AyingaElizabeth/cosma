from django.urls import path
from . import views

app_name = 'cosma_development'

urlpatterns = [
    # Home
    path('', views.index, name='index'),

    # About Us
    path('about/',                   views.about_us,       name='about-us'),
    path('about/mission-vision/',    views.mission_vision, name='mission_vision'),
    path('about/core-values/',       views.core_values,    name='core_values'),
    path('about/our-team/',          views.our_team,       name='our_team'),
    path('about/our-partners/',      views.our_partners,   name='our_partners'),

    # # Programs — Agriculture
    path('programs/agriculture/',                views.agri_why,      name='agri_why'),
    path('programs/agriculture/approach/',       views.agri_approach, name='agri_approach'),
    path('programs/agriculture/support-farmer/', views.agri_support,  name='agri_support'),
    path('programs/agriculture/impact-stories/', views.agri_impact,   name='agri_impact'),

    # # Programs — Sponsorship
    path('programs/sponsorship/',                views.sponsor_why,   name='sponsor_why'),
    path('programs/sponsorship/sponsor-child/',  views.sponsor_child, name='sponsor_child'),
    path('programs/sponsorship/vocational/',     views.vocational,    name='vocational'),

    # # Impact
    path('impact/numbers/', views.impact_numbers, name='impact_numbers'),
    path('impact/stories/', views.impact_stories, name='impact_stories'),
     # Contact
     path('contact/', views.contact_page, name='contact'),

 # API endpoints (POST only)
     path('api/donate/',  views.donate,   name='donate'),
    path('api/contact/', views.contact,  name='contact_submit'),
]
