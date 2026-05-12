from django.urls import path
from . import views

app_name = 'cosma_development'

urlpatterns = [
    path('', views.index, name='index'),

    # ── About ──────────────────────────────────────────────────────────────
    path('about/',                    views.about_us,       name='about-us'),
    path('about/our-approach/',       views.our_approach,   name='our_approach'),   # NEW
    path('about/our-story/',          views.our_story,      name='our_story'),
    path('about/team-partners/',      views.team_partners,  name='team_partners'),
    path('about/resources/',          views.resources,      name='resources'),

    # Legacy redirects (keep for SEO)
    path('about/mission-vision/',     views.mission_vision, name='mission_vision'),
    path('about/core-values/',        views.core_values,    name='core_values'),
    path('about/our-team/',           views.our_team,       name='our_team'),
    path('about/our-partners/',       views.our_partners,   name='our_partners'),

    # ── Programs ───────────────────────────────────────────────────────────
    path('programs/agriculture/',                views.agri_why,           name='agri_why'),
    path('programs/agriculture/approach/',       views.agri_approach,      name='agri_approach'),
    path('programs/agriculture/support-farmer/', views.agri_support,       name='agri_support'),
    path('programs/agriculture/impact-stories/', views.agri_impact,        name='agri_impact'),
    path('programs/agriculture/faqs/',           views.agri_faqs,          name='agri_faqs'),
    path('programs/sponsorship/',                views.sponsor_why,        name='sponsor_why'),
    path('programs/sponsorship/impact-stories/', views.sponsorship_impact, name='sponsorship_impact'),
    path('programs/sponsorship/sponsor-child/',  views.sponsor_child,      name='sponsor_child'),
    path('programs/sponsorship/vocational/',     views.vocational,         name='vocational'),
    path('programs/sponsorship/faqs/',           views.sponsorship_faqs,   name='sponsorship_faqs'),

    # ── Impact ─────────────────────────────────────────────────────────────
    path('impact/numbers/', views.impact_numbers, name='impact_numbers'),
    path('impact/stories/', views.impact_stories, name='impact_stories'),
    path('impact/stories/<slug:slug>/', views.story_detail, name='story_detail'),
    path('impact/gallery/', views.gallery,         name='gallery'),

    # ── Get Involved ───────────────────────────────────────────────────────
    path('get-involved/partner-with-us/', views.partner_with_us, name='partner_with_us'),
    path('get-involved/volunteer/',       views.volunteer,        name='volunteer'),
    path('get-involved/fund-a-project/',  views.fund_project,     name='fund_project'),   # NEW
    path('get-involved/sponsor-a-child/', views.sponsor_child,    name='sponsor_child_gi'), # alias
    path('get-involved/share-our-story/', views.share_story,      name='share_story'),
    path('get-involved/signup-updates/',  views.signup_updates,   name='signup_updates'),

    # ── News & Testimonials ────────────────────────────────────────────────
    path('news/',                     views.news_list,          name='news'),
    path('news/<slug:slug>/',         views.news_detail,        name='news_detail'),
    path('share-your-experience/',    views.submit_testimonial, name='submit_testimonial'),

    # ── Contact & Donate ──────────────────────────────────────────────────
    path('contact/', views.contact_page, name='contact'),
    path('donate/',  views.donate_page,  name='donate_page'),
    path('faqs/',    views.faqs,         name='faqs'),

    # ── API ────────────────────────────────────────────────────────────────
    path('api/donate/',  views.donate,  name='donate'),
    path('api/contact/', views.contact, name='contact_submit'),
]