from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .seo import get_seo
import json

from .models import ImpactStory, Program, Partner, DonationLead, ContactMessage
#create view here
# ── Fallback data shown when DB is empty (dev / first run) ──────────────────

FALLBACK_STORIES = [
    {
        "name": "Amara Nkosi", "location": "Kampala, Uganda",
        "story": "Thanks to the vocational training programme, I now run my own tailoring business and employ three other women from my community.",
        "image": "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=400&q=80",
        "tag": "Empowerment",
    },
    {
        "name": "David Ochieng", "location": "Gulu, Uganda",
        "story": "The scholarship changed everything. I am now in my second year of engineering and plan to build clean-water infrastructure for my village.",
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80",
        "tag": "Education",
    },
    {
        "name": "Grace Mutesi", "location": "Mbarara, Uganda",
        "story": "Our mothers' group received micro-loans and business coaching. Today we supply fresh produce to five schools across the district.",
        "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=80",
        "tag": "Livelihoods",
    },
]

FALLBACK_PROGRAMS = [
    {"icon": "bi-book-half",    "title": "Education Access",  "description": "Scholarships, school supplies, and mentorship for 2,400+ learners annually.", "color": "#3BAD6E", "stat_label": "2,400+ Learners"},
    {"icon": "bi-heart-pulse",  "title": "Community Health",  "description": "Mobile clinics, maternal care, and nutrition programmes in underserved areas.",  "color": "#8E0005", "stat_label": "15,000+ Served"},
    {"icon": "bi-briefcase",    "title": "Livelihoods",        "description": "Vocational training, micro-finance, and market linkages for economic independence.", "color": "#3BAD6E", "stat_label": "800+ Entrepreneurs"},
    {"icon": "bi-droplet-half", "title": "Clean Water",        "description": "Borehole drilling, rainwater harvesting, and WASH education across rural communities.", "color": "#8E0005", "stat_label": "40+ Villages"},
]

FALLBACK_PARTNERS = [
    {"name": "UNICEF",     "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Logo_of_UNICEF.svg/200px-Logo_of_UNICEF.svg.png",    "website": ""},
    {"name": "USAID",      "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/USAID-Identity.svg/200px-USAID-Identity.svg.png",      "website": ""},
    {"name": "WHO",        "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/WHO-EM.svg/200px-WHO-EM.svg.png",                      "website": ""},
    {"name": "UN Women",   "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/UN_Women_Logo.svg/200px-UN_Women_Logo.svg.png",        "website": ""},
    {"name": "GIZ",        "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/GIZ_Logo.svg/200px-GIZ_Logo.svg.png",                  "website": ""},
    {"name": "World Bank", "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/The_World_Bank_logo.svg/200px-The_World_Bank_logo.svg.png", "website": ""},
]

STATS = [
    {"value": "875", "label": "Agriculture"},
    {"value": "342",       "label": "Sponsored students"},
 
 
]



def index(request):
    try:
        from .models import ImpactStory, Program, Partner
        stories  = list(ImpactStory.objects.filter(is_featured=True)[:3]) or FALLBACK_STORIES[:3]
        programs = list(Program.objects.all()) or FALLBACK_PROGRAMS
        partners = list(Partner.objects.all()) or FALLBACK_PARTNERS
    except Exception:
        stories, programs, partners = FALLBACK_STORIES[:3], FALLBACK_PROGRAMS, FALLBACK_PARTNERS
    ctx = {'stories': stories, 'programs': programs, 'partners': partners, 'stats': STATS}
    #ctx.update(get_seo('index'))
    return render(request, 'index.html', ctx)



def logo_view(request):
    return render(request, 'logo.html')

def about_us(request):
    from django.urls import reverse
    about_cards = [
        {"title": "Mission & Vision",    "desc": "The north star guiding everything we do.",   "icon": "bi-eye",         "color": "#8E0005", "bg": "rgba(142,0,5,.1)",    "url": reverse('cosma_development:mission_vision')},
        {"title": "Core Values & Goals", "desc": "The principles that shape our culture.",     "icon": "bi-stars",       "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)", "url": reverse('cosma_development:core_values')},
        {"title": "Our Team",            "desc": "Meet the people behind the programmes.",     "icon": "bi-people-fill", "color": "#8E0005", "bg": "rgba(142,0,5,.1)",    "url": reverse('cosma_development:our_team')},
        {"title": "Our Partners",        "desc": "Global allies who stand with us.",           "icon": "bi-handshake",   "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)", "url": reverse('cosma_development:our_partners')},
    ]
    ctx = {'about_cards': about_cards, 'stats': STATS}
    ctx.update(get_seo('about_us'))
    return render(request, 'about-us/about-us.html', ctx)


def mission_vision(request):
    pillars = [
        {"icon": "bi-book-half",    "title": "Education",   "desc": "Quality learning for every child.",          "color": "#3BAD6E"},
        {"icon": "bi-heart-pulse",  "title": "Health",      "desc": "Accessible healthcare for every family.",    "color": "#8E0005"},
        {"icon": "bi-briefcase",    "title": "Livelihoods", "desc": "Sustainable income for every household.",    "color": "#3BAD6E"},
        {"icon": "bi-droplet-half", "title": "Clean Water", "desc": "Safe water for every community.",            "color": "#8E0005"},
    ]
    ctx = {'pillars': pillars}
    ctx.update(get_seo('mission_vision'))
    return render(request, 'about-us/mission_vision.html', ctx)


def core_values(request):
    values = [
        {"title": "Integrity",       "desc": "Transparent, honest, and accountable in all we do. 98% of funds reach beneficiaries.",            "icon": "bi-shield-check",   "color": "#8E0005", "bg": "rgba(142,0,5,.1)"},
        {"title": "Community First", "desc": "We design with communities, not for them. Local voices lead every programme.",                     "icon": "bi-people-fill",    "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)"},
        {"title": "Sustainability",  "desc": "We build capacity so communities thrive long after our programmes end.",                           "icon": "bi-arrow-repeat",   "color": "#8E0005", "bg": "rgba(142,0,5,.1)"},
        {"title": "Inclusion",       "desc": "We leave no one behind — women, children, persons with disabilities, and the most marginalised.",  "icon": "bi-heart-fill",     "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)"},
        {"title": "Innovation",      "desc": "We embrace evidence-based approaches and continuously learn and adapt.",                           "icon": "bi-lightbulb-fill", "color": "#8E0005", "bg": "rgba(142,0,5,.1)"},
        {"title": "Collaboration",   "desc": "We believe in the power of partnerships — local, national, and global.",                          "icon": "bi-handshake",      "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)"},
    ]
    goals = [
        {"title": "Reach 250,000 Beneficiaries",     "desc": "Double our current reach by 2030 through expanded programming.",    "color": "#8E0005", "bg": "rgba(142,0,5,.1)",    "progress": 50},
        {"title": "100% School Retention",           "desc": "Ensure every sponsored child completes their educational cycle.",    "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)", "progress": 72},
        {"title": "1,000 New Farmer Cooperatives",   "desc": "Establish farmer cooperatives in all 12 districts.",                "color": "#8E0005", "bg": "rgba(142,0,5,.1)",    "progress": 38},
        {"title": "Clean Water for 100 Communities", "desc": "Install boreholes and rainwater systems in 100 communities.",       "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)", "progress": 42},
    ]
    ctx = {'values': values, 'goals': goals}
    ctx.update(get_seo('core_values'))
    return render(request, 'about-us/core_values.html', ctx)


def our_team(request):
    team = [
        {"name": "Dr. Sarah Nakamya",  "role": "Executive Director",        "bio": "20 years in community development across East Africa.",      "image": "https://images.unsplash.com/photo-1589156280159-27698a70f29e?w=400&q=80"},
        {"name": "James Okiror",       "role": "Director of Programs",      "bio": "Agricultural economist and former UNDP programme officer.",  "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80"},
        {"name": "Grace Atim",         "role": "Head of Education",         "bio": "Former headteacher driving literacy and scholarship access.", "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=80"},
        {"name": "Peter Ssemwogerere", "role": "Finance Director",          "bio": "CPA with 15 years in NGO financial management.",             "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80"},
        {"name": "Annet Nantume",      "role": "Community Engagement Lead", "bio": "Grassroots organiser working directly with village councils.","image": "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=400&q=80"},
        {"name": "Moses Tumuhairwe",   "role": "M&E Manager",               "bio": "Data-driven impact measurement specialist.",                 "image": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&q=80"},
    ]
    ctx = {'team': team}
    ctx.update(get_seo('our_team'))
    return render(request, 'about-us/our_team.html', ctx)


def our_partners(request):
    ctx = {'partners': FALLBACK_PARTNERS}
    ctx.update(get_seo('our_partners'))
    return render(request, 'about-us/our_partners.html', ctx)
# ─── PROGRAMS ─────────────────────────────────────────────────────────────────

def agri_why(request):
    ctx = get_seo('agri_why')
    return render(request, 'programs/agri_why.html', ctx)


def agri_approach(request):
    steps = [
        {"title": "Farmer Assessment",         "desc": "Detailed assessment of each farmer's land, resources, and challenges."},
        {"title": "Training & Capacity",       "desc": "Hands-on training in modern techniques, soil management, and climate-smart agriculture."},
        {"title": "Input Support",             "desc": "Quality seeds, fertilisers, and tools at subsidised rates through partner cooperatives."},
        {"title": "Market Linkages",           "desc": "Connecting farmers to buyers, cooperatives, and digital marketplaces for fair prices."},
        {"title": "Monitoring & Follow-up",    "desc": "Regular field visits and data collection to track progress and adapt support."},
        {"title": "Cooperative Formation",     "desc": "Supporting farmers to form cooperatives for collective bargaining and resource sharing."},
    ]
    ctx = {'approach_steps': steps}
    ctx.update(get_seo('agri_approach'))
    return render(request, 'programs/agri_approach.html', ctx)


def agri_support(request):
    ctx = get_seo('agri_support')
    return render(request, 'programs/agri_support.html', ctx)


def agri_impact(request):
    stories = [s for s in FALLBACK_STORIES if s['tag'] in ('Agriculture', 'Livelihoods')] or FALLBACK_STORIES[:4]
    ctx = {'agri_stories': stories}
    ctx.update(get_seo('agri_impact'))
    return render(request, 'programs/agri_impact.html', ctx)


def sponsor_why(request):
    ctx = get_seo('sponsor_why')
    return render(request, 'programs/sponsor_why.html', ctx)


def sponsor_child(request):
    steps = [
        {"title": "Choose a Giving Level", "desc": "Select a monthly or annual amount that works for you."},
        {"title": "Complete Your Details",  "desc": "Fill in your contact information and payment details securely."},
        {"title": "Get Matched",            "desc": "We match you with a child and send you their profile."},
        {"title": "Receive Updates",        "desc": "Get regular updates, photos, and progress reports."},
    ]
    ctx = {'sponsor_steps': steps}
    ctx.update(get_seo('sponsor_child'))
    return render(request, 'programs/sponsor_child.html', ctx)


def vocational(request):
    courses = [
        {"title": "Tailoring & Fashion Design", "desc": "Garment construction, pattern making, and business skills.",          "icon": "bi-scissors",      "duration": "3 Months"},
        {"title": "Carpentry & Joinery",         "desc": "Practical wood-working skills for furniture and construction.",       "icon": "bi-tools",         "duration": "4 Months"},
        {"title": "Catering & Hospitality",      "desc": "Professional cooking, food safety, and hospitality management.",     "icon": "bi-cup-hot",       "duration": "3 Months"},
        {"title": "Solar & Electrical",          "desc": "Installation and maintenance of solar systems and electrical wiring.","icon": "bi-lightning-fill","duration": "4 Months"},
        {"title": "Hair & Beauty",               "desc": "Hairdressing, salon management, and cosmetology skills.",             "icon": "bi-stars",         "duration": "3 Months"},
        {"title": "Financial Literacy",          "desc": "Budgeting, saving, and small business financial management.",         "icon": "bi-cash-stack",    "duration": "6 Weeks"},
    ]
    ctx = {'courses': courses}
    ctx.update(get_seo('vocational'))
    return render(request, 'programs/vocational.html', ctx)

# ─── IMPACT ───────────────────────────────────────────────────────────────────

def impact_numbers(request):
    big_stats = [
        {"value": "125,000+", "label": "Lives Impacted",        "icon": "bi-people-fill",    "color": "#8E0005"},
        {"value": "2,400+",   "label": "Students in School",    "icon": "bi-book-half",      "color": "#3BAD6E"},
        {"value": "4,200+",   "label": "Farmers Supported",     "icon": "bi-flower1",        "color": "#8E0005"},
        {"value": "40+",      "label": "Clean Water Sites",     "icon": "bi-droplet-half",   "color": "#3BAD6E"},
        {"value": "800+",     "label": "Entrepreneurs Trained", "icon": "bi-briefcase",      "color": "#8E0005"},
        {"value": "12",       "label": "Districts Reached",     "icon": "bi-geo-alt-fill",   "color": "#3BAD6E"},
        {"value": "15,000+",  "label": "Health Consultations",  "icon": "bi-heart-pulse",    "color": "#8E0005"},
        {"value": "98%",      "label": "Fund Efficiency",       "icon": "bi-graph-up-arrow", "color": "#3BAD6E"},
    ]
    programme_stats = [
        {"label": "Education — Students retained in school",     "value": "2,400+", "pct": 85, "color": "#3BAD6E"},
        {"label": "Agriculture — Farmers with increased yields", "value": "4,200+", "pct": 72, "color": "#8E0005"},
        {"label": "Health — Communities with clinic access",     "value": "68%",    "pct": 68, "color": "#3BAD6E"},
        {"label": "Water — Villages with clean water access",    "value": "40+",    "pct": 55, "color": "#8E0005"},
        {"label": "Vocational — Graduates now self-employed",    "value": "78%",    "pct": 78, "color": "#3BAD6E"},
        {"label": "Sponsorship — Children completing P7",        "value": "94%",    "pct": 94, "color": "#8E0005"},
    ]
    ctx = {'big_stats': big_stats, 'programme_stats': programme_stats}
    ctx.update(get_seo('impact_numbers'))
    return render(request, 'impact/impact_numbers.html', ctx)


def impact_stories(request):
    ctx = {'stories': FALLBACK_STORIES}
    ctx.update(get_seo('impact_stories'))
    return render(request, 'impact/impact_stories.html', ctx)

def donate(request):
    try:
        data = json.loads(request.body)
        try:
            from .models import DonationLead
            DonationLead.objects.create(
                name=data.get('name', ''), email=data.get('email', ''),
                amount=data.get('amount', 0), message=data.get('message', ''),
            )
        except Exception:
            pass
        return JsonResponse({'status': 'success', 'message': 'Thank you for your generous donation!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def contact_page(request):
    ctx = get_seo('contact')
    return render(request, 'contact.html', ctx)

@require_POST
def contact(request):
    try:
        data = json.loads(request.body)
        ContactMessage.objects.create(
            name=data.get('name', ''),
            email=data.get('email', ''),
            subject=data.get('subject', 'Website Enquiry'),
            message=data.get('message', ''),
        )
        return JsonResponse({'status': 'success', 'message': 'Message received. We will be in touch shortly.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

