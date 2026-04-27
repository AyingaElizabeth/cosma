from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse
from .seo import get_seo
import json
from .models import ImpactStory, Program, TeamMember, Partner, GalleryImage, FAQ, DonationLead, ContactMessage, Resource, Testimonial, NewsPost

FALLBACK_STORIES = [
    {
        "name": "Grace Mutesi",
        "location": "Mbarara, Uganda",
        "headline": "Grace turned one acre into a reliable family income",
        "programme": "agriculture",
        "story": "Grace joined a COSMA-supported farmer group after two failed planting seasons. With climate-smart training, improved seed, and cooperative market access, her harvest grew enough to feed her household and sell surplus to nearby schools.",
        "challenge": "Unpredictable rainfall, poor seed, and no buyer relationships kept Grace's farm income unstable.",
        "intervention": "COSMA provided farmer-field training, starter inputs, and linked her group to a produce buyer.",
        "outcome": "Grace now earns regular seasonal income and keeps all three children in school.",
        "quote": "The training helped me plan before planting and sell together with other farmers.",
        "author": "Webadmin",
        "image": "imgs/hero2.jpg",
        "tag": "Agriculture",
    },
    {
        "name": "David Ochieng",
        "location": "Gulu, Uganda",
        "headline": "Sponsorship kept David learning after his family lost income",
        "programme": "child_sponsorship",
        "story": "When David's family could no longer afford school requirements, COSMA child sponsorship covered fees, books, uniform, and mentorship. His attendance stabilized and his teachers report steady progress in science and reading.",
        "challenge": "School costs and household hardship were pushing David toward dropout.",
        "intervention": "Sponsorship paid essential school costs and connected David with a mentor.",
        "outcome": "David returned to consistent attendance and is preparing for secondary school.",
        "quote": "I want to become an engineer and help my community build better homes.",
        "author": "Webadmin",
        "image": "imgs/kids.png",
        "tag": "Child Sponsorship",
    },
    {
        "name": "Amara Nkosi",
        "location": "Kampala, Uganda",
        "headline": "Skills training helped Amara create work for other young women",
        "programme": "vocational",
        "story": "After completing tailoring and business-skills training, Amara began taking school-uniform orders from her community. She now runs a small workshop and trains three young women as apprentices.",
        "challenge": "Amara had practical talent but no certified skills or startup pathway.",
        "intervention": "COSMA supported vocational training, coaching, and starter business guidance.",
        "outcome": "Her tailoring work now supports her household and creates local apprenticeship opportunities.",
        "quote": "I learned how to sew, price my work, and keep records.",
        "author": "Webadmin",
        "image": "imgs/about-us.jpeg",
        "tag": "Vocational",
    },
]
FALLBACK_PROGRAMS = [
    {"icon": "bi-book-half",    "title": "Education Access", "description": "Scholarships, school supplies, and mentorship for 2,400+ learners annually.", "color": "#3BAD6E", "stat_label": "2,400+ Learners"},
    {"icon": "bi-heart-pulse",  "title": "Community Health", "description": "Mobile clinics, maternal care, and nutrition programmes in underserved areas.",  "color": "#8E0005", "stat_label": "15,000+ Served"},
    {"icon": "bi-briefcase",    "title": "Livelihoods",      "description": "Vocational training, micro-finance, and market linkages for independence.",       "color": "#3BAD6E", "stat_label": "800+ Entrepreneurs"},
    {"icon": "bi-droplet-half", "title": "Clean Water",      "description": "Borehole drilling, rainwater harvesting, and WASH education.",                   "color": "#8E0005", "stat_label": "40+ Villages"},
]
FALLBACK_PARTNERS = [
    {"name": "UNICEF",     "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Logo_of_UNICEF.svg/200px-Logo_of_UNICEF.svg.png",        "website": ""},
    {"name": "USAID",      "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/USAID-Identity.svg/200px-USAID-Identity.svg.png",          "website": ""},
    {"name": "WHO",        "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/WHO-EM.svg/200px-WHO-EM.svg.png",                          "website": ""},
    {"name": "World Bank", "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/The_World_Bank_logo.svg/200px-The_World_Bank_logo.svg.png","website": ""},
]
STATS = [{"value": "875", "label": "Agriculture"}, {"value": "342", "label": "Sponsored students"}]
FALLBACK_GALLERY = [
    {"image": "imgs/kids.png",       "caption": "Children supported through learning and mentorship", "category": "education"},
    {"image": "imgs/hero2.jpg",      "caption": "Farmers building practical skills for stronger harvests", "category": "agriculture"},
    {"image": "imgs/about-us.jpeg",  "caption": "COSMA staff working alongside community members", "category": "community"},
    {"image": "imgs/hero3.jpg",      "caption": "Families gathering for programme outreach", "category": "community"},
    {"image": "imgs/hero5.png",      "caption": "Young people taking part in skills development", "category": "vocational"},
]
IMPACT_FILTERS = {
    'agriculture': {
        'label': 'Agriculture',
        'hero': 'Agriculture Impact Stories',
        'description': 'Stories of smallholder farmers, cooperatives, and families building resilient livelihoods through agriculture.',
        'tags': ['Agriculture', 'Livelihoods'],
        'programme': 'agriculture',
        'icon': 'bi-flower1',
    },
    'child-sponsorship': {
        'label': 'Child Sponsorship',
        'hero': 'Child Sponsorship Impact Stories',
        'description': 'Stories of children and families whose education journey is strengthened through sponsorship.',
        'tags': ['Child Sponsorship', 'Sponsorship', 'Education'],
        'programme': 'child_sponsorship',
        'icon': 'bi-mortarboard',
    },
}


def _filter_fallback_stories(program_key=''):
    if not program_key:
        return FALLBACK_STORIES
    config = IMPACT_FILTERS.get(program_key)
    if not config:
        return FALLBACK_STORIES
    return [
        story for story in FALLBACK_STORIES
        if story.get('programme') == config['programme'] or story.get('tag') in config['tags']
    ] or FALLBACK_STORIES


def _impact_story_queryset(program_key='', featured_only=False):
    qs = ImpactStory.objects.all()
    if featured_only:
        qs = qs.filter(is_featured=True)
    config = IMPACT_FILTERS.get(program_key)
    if config:
        qs = qs.filter(Q(programme=config['programme']) | Q(tag__in=config['tags']))
    return qs


def _fallback_faqs(category=None):
    items = FALLBACK_FAQS
    if category:
        items = [item for item in items if item['category'] == category]
    return items


def _published_faqs(category=None):
    qs = FAQ.objects.filter(is_published=True)
    if category:
        qs = qs.filter(category=category)
    return qs.order_by('category','order','-created_at')


def _faq_groups(items):
    category_labels = dict(FAQ.CATEGORY_CHOICES)
    groups = []
    for key, label in FAQ.CATEGORY_CHOICES:
        group_items = [item for item in items if item.category == key] if items and hasattr(items[0], 'category') else [item for item in items if item.get('category') == key]
        if group_items:
            groups.append({'key': key, 'label': label, 'items': group_items})
    return groups


def _team_members():
    try:
        members = list(TeamMember.objects.filter(is_active=True))
        return members or TEAM
    except Exception:
        return TEAM


def _team_groups(members):
    groups = []
    for key, title, intro in [
        ('board', 'Board Members', 'Our board provides governance, oversight, and strategic guidance for COSMA development.'),
        ('staff', 'Staff', 'Our staff lead the day-to-day programme delivery, partnerships, and community engagement.'),
    ]:
        if members and hasattr(members[0], 'group'):
            group_members = [member for member in members if member.group == key]
        else:
            group_members = [member for member in members if member.get('group', 'staff') == key]
        if group_members:
            groups.append({'key': key, 'title': title, 'intro': intro, 'members': group_members})
    return groups
DONATE_FAQS = [
    {"q": "How is my donation processed?",           "a": "Donations are processed securely through our third-party payment provider. You receive an email confirmation and official receipt immediately."},
    {"q": "Can I donate in other currencies?",       "a": "Yes. Our platform accepts USD, GBP, EUR, and other major currencies."},
    {"q": "Is my donation tax-deductible?",          "a": "We issue official receipts for all donations. Tax eligibility depends on your country."},
    {"q": "Can I set up a recurring donation?",      "a": "Yes — select Monthly during the donation process."},
    {"q": "How do I know funds reach beneficiaries?","a": "We publish audited annual reports. 98% of all donations go directly to programmes."},
    {"q": "Can I donate to a specific programme?",   "a": "Yes. Select your programme during checkout or contact us for a restricted gift."},
]
FALLBACK_FAQS = [
    {"category": "agriculture", "q": "Who can join the agriculture programme?", "a": "Smallholder farmers and farmer groups in COSMA-supported communities can be assessed for training, input support, and cooperative participation."},
    {"category": "agriculture", "q": "What support does a farmer receive?", "a": "Support may include climate-smart agriculture training, improved seed, tools, coaching, savings group support, and links to reliable buyers."},
    {"category": "agriculture", "q": "How does COSMA measure agriculture impact?", "a": "Field teams track attendance, acreage, yield change, household income, cooperative sales, and practical household outcomes such as school retention and food security."},
    {"category": "agriculture", "q": "Can I support a specific farmer?", "a": "You can give toward the farmer support fund. COSMA allocates gifts based on verified need and reports back with programme-level outcomes."},
    {"category": "child_sponsorship", "q": "What does child sponsorship cover?", "a": "Sponsorship supports school fees, uniforms, learning materials, mentorship, wellbeing follow-up, and family engagement where needed."},
    {"category": "child_sponsorship", "q": "Will I receive updates?", "a": "Yes. Sponsors receive progress updates that protect the child's dignity and privacy while showing how support is helping."},
    {"category": "child_sponsorship", "q": "How are children selected?", "a": "COSMA works with local schools and community leaders to identify children facing the highest risk of dropout or interrupted learning."},
    {"category": "vocational", "q": "Is vocational and life skills training part of sponsorship?", "a": "Older children and youth can be linked to vocational and life skills pathways when that is the best route to continued learning and independence."},
    {"category": "donations", "q": "How is my donation processed?", "a": "Donations are processed securely through our giving platform. You receive confirmation and COSMA records your gift for follow-up and reporting."},
    {"category": "partnerships", "q": "Can organisations partner with COSMA?", "a": "Yes. COSMA works with community groups, schools, companies, foundations, and institutions on programme delivery and resource mobilisation."},
]
TIMELINE_EVENTS = [
    {"year": "2006", "icon": "bi-house-heart",   "title": "The Beginning",               "desc": "cosma development was founded by Ugandan educators in Kampala. The first after-school programme launched in a single classroom, serving 42 children.", "stat": "42 children in Year 1", "image": "https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=600&q=80"},
    {"year": "2008", "icon": "bi-heart-pulse",   "title": "Community Health Begins",     "desc": "Responding to high maternal mortality, we launched mobile health clinics across two districts. Over 800 health consultations were delivered in the first year.", "stat": "800+ health visits", "image": None},
    {"year": "2010", "icon": "bi-flower1",       "title": "Agriculture Programme",       "desc": "We launched our first cooperative model — connecting 120 smallholder farmers with inputs, training, and market access.", "stat": "120 farmers in first cohort", "image": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600&q=80"},
    {"year": "2012", "icon": "bi-droplet-half",  "title": "Clean Water Initiative",      "desc": "Partnering with UNICEF, we drilled our first 10 boreholes in Luwero district, bringing safe water to over 4,000 people.", "stat": "4,000+ gained clean water", "image": None},
    {"year": "2014", "icon": "bi-award",         "title": "National Recognition",        "desc": "cosma development received the Uganda NGO Excellence Award. Our model was adopted as a best-practice case study by the Ministry of Agriculture.", "stat": "Best-practice designation", "image": None},
    {"year": "2016", "icon": "bi-briefcase",     "title": "Vocational Centres Open",    "desc": "Two vocational training centres opened in Kampala and Jinja, offering tailoring, carpentry, solar, and catering to youth aged 16-35.", "stat": "600+ graduates in 2 years", "image": "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=600&q=80"},
    {"year": "2018", "icon": "bi-globe-africa",  "title": "Expanding to 12 Districts",  "desc": "With USAID and GIZ support, we expanded to all 12 target districts. The 100,000th beneficiary was served.", "stat": "100,000th beneficiary reached", "image": None},
    {"year": "2021", "icon": "bi-shield-check",  "title": "COVID-19 Response",           "desc": "When the pandemic struck, cosma development distributed food to 8,000 households and kept 1,200 children in remote schooling.", "stat": "8,000 households supported", "image": None},
    {"year": "2023", "icon": "bi-graph-up-arrow","title": "125,000 Lives Impacted",     "desc": "Our annual impact count crossed 125,000 — 17 years of consistent, community-led work. The cooperative model now includes 4,200+ farmers.", "stat": "125,000+ lives annually", "image": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=600&q=80"},
    {"year": "Today","icon": "bi-stars",         "title": "Looking Forward",             "desc": "With a plan to reach 250,000 beneficiaries by 2030, cosma development builds on 18 years of trust and partnership — one community at a time.", "stat": "Target: 250,000 by 2030", "image": None},
]
HERO_STATS = [
    {"label": "Years of service",  "raw": 18,     "suffix": "+"},
    {"label": "Lives impacted",    "raw": 125000, "suffix": "+"},
    {"label": "Districts reached", "raw": 12,     "suffix": ""},
    {"label": "Fund efficiency",   "raw": 98,     "suffix": "%"},
]
VALUES = [
    {"title": "Accountability",       "desc": "Transparency and integrity are at the heart of everything we do. We hold ourselves responsible to our beneficiaries, partners, and stakeholders, ensuring that our work is measurable, ethical, and results-driven. We openly communicate our progress and impact to build trust and credibi", "color": "#8E0005", "bg": "rgba(142,0,5,.1)"},
    {"title": "Empowerment", "desc": "We believe in the power of individuals to shape their own destinies. Through education, training, and resources, we equip communities with the tools they need to break cycles of poverty and create independent, thriving futures. Our goal is to inspire confidence, self-determination, and lasting transformation.",  "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)"},
    {"title": "Sustainability",  "desc": "We are dedicated to creating long-term, meaningful impact by implementing programs that promote self-sufficiency and environmental stewardship. Our initiatives are designed to ensure sustainable growth and development, benefiting communities for generations to come.", "color": "#8E0005", "bg": "rgba(142,0,5,.1)"},
    
]
GOALS = [
    {"title": "Reach 250,000 Beneficiaries by 2030", "desc": "Double reach through expanded programming.",   "progress": 50},
    {"title": "100% School Retention",               "desc": "Every sponsored child completes their cycle.", "progress": 72},
    {"title": "1,000 New Farmer Cooperatives",        "desc": "Cooperatives in all 12 districts.",           "progress": 38},
    {"title": "Clean Water for 100 Communities",      "desc": "Boreholes and rainwater systems everywhere.",  "progress": 42},
]
TEAM = [
    {"name": "Dr. Sarah Nakamya",  "role": "Board Chair",               "group": "board", "bio": "20 years in community development across East Africa.",     "image": "https://images.unsplash.com/photo-1589156280159-27698a70f29e?w=400&q=80",  "linkedin": "#", "twitter": "#", "email": ""},
    {"name": "Peter Ssemwogerere", "role": "Board Treasurer",           "group": "board", "bio": "CPA with 15 years in NGO financial management.",           "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80",  "linkedin": "#", "twitter": "#", "email": ""},
    {"name": "James Okiror",       "role": "Director of Programs",      "group": "staff", "bio": "Agricultural economist and former UNDP programme officer.", "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80",  "linkedin": "#", "twitter": "#", "email": ""},
    {"name": "Grace Atim",         "role": "Head of Education",         "group": "staff", "bio": "Former headteacher driving literacy and access.",           "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=80",  "linkedin": "#", "twitter": "#", "email": ""},
    {"name": "Annet Nantume",      "role": "Community Engagement Lead", "group": "staff", "bio": "Grassroots organiser working with village councils.",      "image": "https://images.unsplash.com/photo-1531123897727-be9c29b29330?w=400&q=80",  "linkedin": "#", "twitter": "#", "email": ""},
    {"name": "Moses Tumuhairwe",   "role": "M&E Manager",               "group": "staff", "bio": "Data-driven impact measurement specialist.",               "image": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&q=80",  "linkedin": "#", "twitter": "#", "email": ""},
]
PILLARS = [
    {"title": "Agriculture", "desc": "Farmer groups, cooperative support, climate-smart training, and market access for resilient rural livelihoods.", "icon": "bi-flower1", "color": "#3BAD6E"},
    {"title": "Education", "desc": "Child sponsorship, school retention support, mentorship, and pathways into practical skills training.", "icon": "bi-book-half", "color": "#8E0005"},
    {"title": "Skills & Enterprise", "desc": "Vocational and life skills training that helps youth and families build sustainable income.", "icon": "bi-tools", "color": "#3BAD6E"},
    {"title": "Community Wellbeing", "desc": "Partnerships that strengthen household stability, dignity, and long-term self-reliance.", "icon": "bi-people-fill", "color": "#8E0005"},
]

def index(request):
    from django.conf import settings
    try:
        stories      = list(_impact_story_queryset(featured_only=True)[:3]) or FALLBACK_STORIES[:3]
        programs     = list(Program.objects.all()) or FALLBACK_PROGRAMS
        partners     = list(Partner.objects.all()) or FALLBACK_PARTNERS
        approved_testimonials = Testimonial.objects.filter(is_approved=True)
        testimonials = list(approved_testimonials.filter(is_featured=True).order_by('order','-created_at')[:6])
        if not testimonials:
            testimonials = list(approved_testimonials.order_by('order','-created_at')[:6])
        latest_news  = list(NewsPost.objects.filter(is_published=True).order_by('-published_at')[:4])
    except Exception:
        stories, programs, partners = FALLBACK_STORIES[:3], FALLBACK_PROGRAMS, FALLBACK_PARTNERS
        testimonials, latest_news = [], []
    ctx = {
        'stories':      stories,
        'programs':     programs,
        'partners':     partners,
        'stats':        STATS,
        'testimonials': testimonials,
        'latest_news':  latest_news,
        'globalgiving_url': getattr(settings, 'GLOBALGIVING_URL', 'https://www.globalgiving.org/donate/11831/cosma-sustainable-rural-development/'),
    }
    return render(request, 'index.html', ctx)

def logo_view(request):
    return render(request, 'logo.html')

def our_story(request):
    ctx = {'timeline': TIMELINE_EVENTS, 'hero_stats': HERO_STATS, 'values': VALUES, 'goals': GOALS}
    ctx.update(get_seo('our_story'))
    return render(request, 'about-us/our_story.html', ctx)

def team_partners(request):
    try:
        partners = list(Partner.objects.all()) or FALLBACK_PARTNERS
    except Exception:
        partners = FALLBACK_PARTNERS
    team = _team_members()
    ctx = {'team': team, 'team_groups': _team_groups(team), 'partners': partners}
    ctx.update(get_seo('team_partners'))
    return render(request, 'about-us/team-partners.html', ctx)

def resources(request):
    try:
        published = Resource.objects.filter(is_published=True)
        featured  = published.filter(is_featured=True).first()
        res_list  = list(published.exclude(pk=featured.pk) if featured else published)
    except Exception:
        featured, res_list = None, []
    ctx = {'featured': featured, 'resources': res_list}
    ctx.update(get_seo('resources'))
    return render(request, 'about-us/resources.html', ctx)

# Legacy and overview pages
def about_us(request):
    try:
        partners = list(Partner.objects.all()) or FALLBACK_PARTNERS
    except Exception:
        partners = FALLBACK_PARTNERS
    team = _team_members()
    ctx = {'pillars': PILLARS, 'values': VALUES, 'team': team, 'team_groups': _team_groups(team), 'partners': partners}
    ctx.update(get_seo('about_us'))
    return render(request, 'about-us/about-us.html', ctx)
def mission_vision(request): return redirect('cosma_development:our_story')
def core_values(request):    return redirect('cosma_development:our_story')
def our_team(request):       return redirect('cosma_development:team_partners')
def our_partners(request):   return redirect('cosma_development:team_partners')

def agri_why(request):
    ctx = get_seo('agri_why')
    return render(request, 'programs/agri_why.html', ctx)

def agri_approach(request):
    steps = [
        {"title": "Farmer Assessment","desc": "Detailed assessment of each farmer's land, resources, and challenges."},
        {"title": "Training & Capacity","desc": "Hands-on training in modern techniques and climate-smart agriculture."},
        {"title": "Input Support","desc": "Quality seeds, fertilisers, and tools at subsidised rates."},
        {"title": "Market Linkages","desc": "Connecting farmers to buyers, cooperatives, and digital marketplaces."},
        {"title": "Monitoring & Follow-up","desc": "Regular field visits and data to track progress."},
        {"title": "Cooperative Formation","desc": "Supporting farmers to form cooperatives for collective bargaining."},
    ]
    ctx = {'approach_steps': steps}
    ctx.update(get_seo('agri_approach'))
    return render(request, 'programs/agri_approach.html', ctx)

def agri_support(request):
    ctx = get_seo('agri_support')
    return render(request, 'programs/agri_support.html', ctx)

def agri_impact(request):
    return redirect(f"{reverse('cosma_development:impact_stories')}?program=agriculture")

def agri_faqs(request):
    try:
        faqs = list(_published_faqs('agriculture')) or _fallback_faqs('agriculture')
    except Exception:
        faqs = _fallback_faqs('agriculture')
    ctx = {'program_title': 'Agriculture FAQs', 'program_label': 'Agriculture Programme', 'program_icon': 'bi-flower1', 'faqs': faqs}
    ctx.update(get_seo('agri_faqs'))
    return render(request, 'programs/faqs.html', ctx)

def sponsor_why(request):
    ctx = get_seo('sponsor_why')
    return render(request, 'programs/sponsor_why.html', ctx)

def sponsor_child(request):
    steps = [
        {"title": "Choose a Giving Level","desc": "Select a monthly or annual amount that works for you."},
        {"title": "Complete Your Details","desc": "Fill in contact and payment details securely."},
        {"title": "Get Matched","desc": "We match you with a child and send their profile."},
        {"title": "Receive Updates","desc": "Get regular updates, photos, and progress reports."},
    ]
    ctx = {'sponsor_steps': steps}
    ctx.update(get_seo('sponsor_child'))
    return render(request, 'programs/sponsor_child.html', ctx)

def vocational(request):
    courses = [
        {"title": "Tailoring & Fashion Design","desc": "Garment construction, pattern making, and business skills.","icon": "bi-scissors","duration": "3 Months"},
        {"title": "Carpentry & Joinery","desc": "Practical wood-working for furniture and construction.","icon": "bi-tools","duration": "4 Months"},
        {"title": "Catering & Hospitality","desc": "Professional cooking, food safety, and hospitality.","icon": "bi-cup-hot","duration": "3 Months"},
        {"title": "Solar & Electrical","desc": "Installation and maintenance of solar systems.","icon": "bi-lightning-fill","duration": "4 Months"},
        {"title": "Hair & Beauty","desc": "Hairdressing, salon management, and cosmetology.","icon": "bi-stars","duration": "3 Months"},
        {"title": "Financial Literacy","desc": "Budgeting, saving, and small business management.","icon": "bi-cash-stack","duration": "6 Weeks"},
    ]
    ctx = {'courses': courses}
    ctx.update(get_seo('vocational'))
    return render(request, 'programs/vocational.html', ctx)

def sponsorship_impact(request):
    return redirect(f"{reverse('cosma_development:impact_stories')}?program=child-sponsorship")

def sponsorship_faqs(request):
    try:
        faqs = list(_published_faqs('child_sponsorship')) or _fallback_faqs('child_sponsorship')
    except Exception:
        faqs = _fallback_faqs('child_sponsorship')
    ctx = {'program_title': 'Child Sponsorship FAQs', 'program_label': 'Child Sponsorship', 'program_icon': 'bi-mortarboard', 'faqs': faqs}
    ctx.update(get_seo('sponsorship_faqs'))
    return render(request, 'programs/faqs.html', ctx)

def faqs(request):
    try:
        items = list(_published_faqs()) or _fallback_faqs()
    except Exception:
        items = _fallback_faqs()
    ctx = {'faq_groups': _faq_groups(items)}
    ctx.update(get_seo('faqs'))
    return render(request, 'faqs.html', ctx)

def impact_numbers(request):
    big_stats = [
        {"value": "125,000+","label": "Lives Impacted","icon": "bi-people-fill","color": "#8E0005"},
        {"value": "2,400+","label": "Students in School","icon": "bi-book-half","color": "#3BAD6E"},
        {"value": "4,200+","label": "Farmers Supported","icon": "bi-flower1","color": "#8E0005"},
        {"value": "40+","label": "Clean Water Sites","icon": "bi-droplet-half","color": "#3BAD6E"},
        {"value": "800+","label": "Entrepreneurs Trained","icon": "bi-briefcase","color": "#8E0005"},
        {"value": "12","label": "Districts Reached","icon": "bi-geo-alt-fill","color": "#3BAD6E"},
        {"value": "15,000+","label": "Health Consultations","icon": "bi-heart-pulse","color": "#8E0005"},
        {"value": "98%","label": "Fund Efficiency","icon": "bi-graph-up-arrow","color": "#3BAD6E"},
    ]
    programme_stats = [
        {"label": "Education — Students retained","value": "2,400+","pct": 85,"color": "#3BAD6E"},
        {"label": "Agriculture — Farmers with increased yields","value": "4,200+","pct": 72,"color": "#8E0005"},
        {"label": "Health — Communities with clinic access","value": "68%","pct": 68,"color": "#3BAD6E"},
        {"label": "Water — Villages with clean water","value": "40+","pct": 55,"color": "#8E0005"},
        {"label": "Vocational — Graduates now self-employed","value": "78%","pct": 78,"color": "#3BAD6E"},
        {"label": "Sponsorship — Children completing P7","value": "94%","pct": 94,"color": "#8E0005"},
    ]
    ctx = {'big_stats': big_stats, 'programme_stats': programme_stats}
    ctx.update(get_seo('impact_numbers'))
    return render(request, 'impact/impact_numbers.html', ctx)

def impact_stories(request):
    active_program = request.GET.get('program', '').strip()
    active_filter = IMPACT_FILTERS.get(active_program)
    try:
        stories = list(_impact_story_queryset(active_program, featured_only=True)) or _filter_fallback_stories(active_program)
    except Exception:
        stories = _filter_fallback_stories(active_program)
    ctx = {
        'stories': stories,
        'filters': IMPACT_FILTERS,
        'active_program': active_program,
        'active_filter': active_filter,
        'hero_title': active_filter['hero'] if active_filter else 'Impact Stories',
        'hero_description': active_filter['description'] if active_filter else 'Behind every statistic is a person. These are their stories.',
    }
    ctx.update(get_seo('impact_stories'))
    return render(request, 'impact/impact_stories.html', ctx)

def gallery(request):
    try:
        gallery_photos = list(GalleryImage.objects.filter(is_published=True))
    except Exception:
        gallery_photos = []
    ctx = {'fallback_photos': FALLBACK_GALLERY, 'gallery_photos': gallery_photos}
    ctx.update(get_seo('gallery'))
    return render(request, 'impact/gallery.html', ctx)

def partner_with_us(request):
    partnership_types = [
        {"title": "Corporate Sponsor","desc": "Align your brand with measurable community impact through a structured CSR package.","icon": "bi-building","color": "#8E0005","bg": "rgba(142,0,5,.1)"},
        {"title": "Institutional Grant","desc": "Fund a specific programme. We partner with foundations, bilateral donors, and UN agencies.","icon": "bi-bank","color": "#3BAD6E","bg": "rgba(59,173,110,.1)"},
        {"title": "In-Kind Support","desc": "Donate goods, services, or expertise — from medical supplies to professional training.","icon": "bi-box-seam","color": "#8E0005","bg": "rgba(142,0,5,.1)"},
        {"title": "Community Partner","desc": "Local organisations, churches, and schools extend our reach in their districts.","icon": "bi-people-fill","color": "#3BAD6E","bg": "rgba(59,173,110,.1)"},
    ]
    ctx = {'partnership_types': partnership_types}
    ctx.update(get_seo('partner_with_us'))
    return render(request, 'get-involved/partner_with_us.html', ctx)

def share_story(request):
    ctx = get_seo('share_story')
    return render(request, 'get-involved/share_story.html', ctx)

def volunteer(request):
    volunteer_roles = [
        {"title": "Teaching & Tutoring","desc": "Support literacy, numeracy, or vocational skills in our learning centres.","icon": "bi-mortarboard","color": "#8E0005","bg": "rgba(142,0,5,.1)","commitment": "Min. 1 month"},
        {"title": "Healthcare & Medical","desc": "Qualified health professionals supporting mobile clinic teams.","icon": "bi-heart-pulse","color": "#3BAD6E","bg": "rgba(59,173,110,.1)","commitment": "Min. 2 weeks"},
        {"title": "Agriculture","desc": "Agronomists sharing modern techniques with smallholder farming cooperatives.","icon": "bi-flower1","color": "#8E0005","bg": "rgba(142,0,5,.1)","commitment": "Min. 1 month"},
        {"title": "Communications & Media","desc": "Photographers, videographers, and writers helping tell our story.","icon": "bi-camera","color": "#3BAD6E","bg": "rgba(59,173,110,.1)","commitment": "Flexible"},
        {"title": "IT & Technology","desc": "Developers and data analysts supporting our digital work.","icon": "bi-laptop","color": "#8E0005","bg": "rgba(142,0,5,.1)","commitment": "Flexible / Remote"},
        {"title": "Fundraising & Events","desc": "Help organise fundraising events, campaigns, and outreach.","icon": "bi-megaphone","color": "#3BAD6E","bg": "rgba(59,173,110,.1)","commitment": "Flexible"},
    ]
    ctx = {'volunteer_roles': volunteer_roles}
    ctx.update(get_seo('volunteer'))
    return render(request, 'get-involved/volunteer.html', ctx)

def signup_updates(request):
    ctx = get_seo('signup_updates')
    return render(request, 'get-involved/signup_updates.html', ctx)

def contact_page(request):
    ctx = get_seo('contact')
    return render(request, 'contact.html', ctx)


# ── NEWS ─────────────────────────────────────────────────────────────────────

def news_list(request):
    from django.core.paginator import Paginator
    active_category = request.GET.get('cat', '')
    qs = NewsPost.objects.filter(is_published=True)
    if active_category:
        qs = qs.filter(category=active_category)
    featured   = NewsPost.objects.filter(is_published=True, is_featured=True).first()
    paginator  = Paginator(qs.exclude(pk=featured.pk) if featured else qs, 9)
    page       = request.GET.get('page', 1)
    posts      = paginator.get_page(page)
    categories = NewsPost.CATEGORIES
    ctx = {
        'posts':           posts,
        'featured':        featured,
        'categories':      categories,
        'active_category': active_category,
    }
    ctx.update(get_seo('news'))
    return render(request, 'news/news_list.html', ctx)


def news_detail(request, slug):
    from django.shortcuts import get_object_or_404
    from django.conf import settings
    post    = get_object_or_404(NewsPost, slug=slug, is_published=True)
    related = NewsPost.objects.filter(
        is_published=True, category=post.category
    ).exclude(pk=post.pk).order_by('-published_at')[:3]
    ctx = {
        'post':             post,
        'related':          related,
        'globalgiving_url': getattr(settings, 'GLOBALGIVING_URL', 'https://www.globalgiving.org/donate/11831/cosma-sustainable-rural-development/'),
    }
    ctx.update(get_seo('news_detail'))
    return render(request, 'news/news_detail.html', ctx)


# ── TESTIMONIALS ──────────────────────────────────────────────────────────────

def submit_testimonial(request):
    submitted = False
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        role    = request.POST.get('role', 'other')
        org     = request.POST.get('organisation', '').strip()
        body    = request.POST.get('body', '').strip()
        rating  = int(request.POST.get('rating', 5))
        photo   = request.FILES.get('photo')
        if name and body:
            t = Testimonial(
                name=name, role=role, organisation=org,
                body=body, rating=rating,
                is_approved=True, is_featured=False,
            )
            if photo:
                t.photo = photo
            t.save()
            submitted = True
    ctx = {'submitted': submitted}
    ctx.update(get_seo('submit_testimonial'))
    return render(request, 'news/submit_testimonial.html', ctx)


def donate_page(request):
    from django.conf import settings
    globalgiving_url = getattr(settings, 'GLOBALGIVING_URL', 'https://www.globalgiving.org/donate/11831/cosma-sustainable-rural-development/')
    impact_items = [
        {"emoji": "👧", "figure": "2,400+", "desc": "children kept in school each year"},
        {"emoji": "🌾", "figure": "4,200+", "desc": "farmers with better harvests and income"},
        {"emoji": "💧", "figure": "40+",    "desc": "clean water sites across 8 districts"},
        {"emoji": "🏥", "figure": "15,000+","desc": "health consultations delivered annually"},
    ]
    impact_stats = [
        {"value": "125,000+", "label": "Lives Impacted Annually",   "icon": "bi-people-fill",    "color": "#8E0005"},
        {"value": "2,400+",   "label": "Children Supported",        "icon": "bi-book-half",      "color": "#3BAD6E"},
        {"value": "4,200+",   "label": "Farmers in Cooperatives",   "icon": "bi-flower1",        "color": "#8E0005"},
        {"value": "98%",      "label": "Funds Reach Beneficiaries", "icon": "bi-graph-up-arrow", "color": "#3BAD6E"},
    ]
    try:
        stories = list(ImpactStory.objects.filter(is_featured=True)[:3]) or FALLBACK_STORIES[:3]
    except Exception:
        stories = FALLBACK_STORIES[:3]
    ctx = {
        'globalgiving_url': globalgiving_url,
        'impact_items':     impact_items,
        'impact_stats':     impact_stats,
        'stories':          stories,
        'faqs':             DONATE_FAQS,
    }
    ctx.update(get_seo('donate'))
    return render(request, 'donate.html', ctx)

def donate(request):
    try:
        data = json.loads(request.body)
        try:
            DonationLead.objects.create(name=data.get('name',''), email=data.get('email',''), amount=data.get('amount',0), message=data.get('message',''))
        except Exception:
            pass
        return JsonResponse({'status': 'success', 'message': 'Thank you for your generous donation!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
def contact(request):
    try:
        data = json.loads(request.body)
        ContactMessage.objects.create(name=data.get('name',''), email=data.get('email',''), subject=data.get('subject','Website Enquiry'), message=data.get('message',''))
        return JsonResponse({'status': 'success', 'message': 'Message received. We will be in touch shortly.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
