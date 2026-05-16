from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import (
    SiteSettings, HeroSection, HomeSlide, HomeStat, ImpactItem,
    MissionVisionPurpose, CoreValue, TimelineEvent, OrgGoal, HeroStat,
    VocationalCourse, AgriApproachStep, SponsorStep,
    PartnershipType, VolunteerRole,
    ImpactBigStat, ImpactProgrammeStat,
    ImpactStory, Program, TeamMember, Partner, GalleryImage,
    FAQ, DonationLead, ContactMessage, Resource, Testimonial, NewsPost,
)
from .seo import get_seo


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _settings():
    return SiteSettings.get()


def _hero(page_key):
    """Return the HeroSection for a page, or None."""
    try:
        return HeroSection.objects.filter(page=page_key, is_active=True).first()
    except Exception:
        return None


def _mvp():
    try:
        return MissionVisionPurpose.objects.prefetch_related('core_values').first()
    except Exception:
        return None


def _values():
    mvp = _mvp()
    if mvp:
        values = list(mvp.core_values.order_by('order'))
        # Assign alternating colours if not set
        for i, v in enumerate(values):
            v.color = '#8E0005' if i % 2 == 0 else '#3BAD6E'
            v.bg   = 'rgba(142,0,5,.1)' if i % 2 == 0 else 'rgba(59,173,110,.1)'
        return values
    return FALLBACK_VALUES


def _team_members():
    try:
        members = list(TeamMember.objects.filter(is_active=True))
        return members or FALLBACK_TEAM
    except Exception:
        return FALLBACK_TEAM


def _team_groups(members):
    groups = []
    for key, title, intro in [
        ('board', 'Board Members', 'Our board provides governance, oversight, and strategic guidance.'),
        ('staff', 'Staff', 'Our staff lead day-to-day programme delivery and community engagement.'),
    ]:
        if members and hasattr(members[0], 'group'):
            grp = [m for m in members if m.group == key]
        else:
            grp = [m for m in members if m.get('group', 'staff') == key]
        if grp:
            groups.append({'key': key, 'title': title, 'intro': intro, 'members': grp})
    return groups


def _published_faqs(category=None):
    qs = FAQ.objects.filter(is_published=True)
    if category:
        qs = qs.filter(category=category)
    return qs.order_by('category', 'order', '-created_at')


def _faq_groups(items):
    groups = []
    for key, label in FAQ.CATEGORY_CHOICES:
        if hasattr(items, 'filter'):
            grp = list(items.filter(category=key))
        else:
            grp = [i for i in items if (i.category if hasattr(i, 'category') else i.get('category')) == key]
        if grp:
            groups.append({'key': key, 'label': label, 'items': grp})
    return groups


def _filter_fallback_stories(program_key=''):
    if not program_key:
        return FALLBACK_STORIES
    config = IMPACT_FILTERS.get(program_key)
    if not config:
        return FALLBACK_STORIES
    return [s for s in FALLBACK_STORIES
            if s.get('programme') == config['programme'] or s.get('tag') in config['tags']] or FALLBACK_STORIES


def _impact_story_queryset(program_key='', featured_only=False):
    qs = ImpactStory.objects.all()
    if featured_only:
        qs = qs.filter(is_featured=True)
    config = IMPACT_FILTERS.get(program_key)
    if config:
        qs = qs.filter(Q(programme=config['programme']) | Q(tag__in=config['tags']))
    return qs


# ─────────────────────────────────────────────────────────────────────────────
#  FALLBACK DATA
# ─────────────────────────────────────────────────────────────────────────────

FALLBACK_STORIES = [
    {"name": "Grace Mutesi", "location": "Mbarara, Uganda",
     "slug": "grace-mutesi-mbarara-uganda", "has_full_story": True,
     "headline": "Grace turned one acre into a reliable family income",
     "programme": "agriculture", "story": "Grace joined a COSMA-supported farmer group after two failed planting seasons.",
     "challenge": "Unpredictable rainfall kept Grace's farm income unstable.",
     "intervention": "COSMA provided climate-smart training and market access.",
     "outcome": "Grace now earns regular income and keeps all three children in school.",
     "quote": "The training helped me plan before planting.", "author": "Webadmin",
     "image": "imgs/hero2.jpg", "tag": "Agriculture"},
    {"name": "David Ochieng", "location": "Gulu, Uganda",
    "slug": "david-ochieng-gulu-uganda", "has_full_story": True,
     "headline": "Sponsorship kept David learning after his family lost income",
     "programme": "child_sponsorship", "story": "COSMA child sponsorship covered fees, books, uniform, and mentorship.",
     "challenge": "School costs were pushing David toward dropout.",
     "intervention": "Sponsorship paid essential school costs.",
     "outcome": "David returned to consistent attendance.",
     "quote": "I want to become an engineer.", "author": "Webadmin",
     "image": "imgs/kids.png", "tag": "Child Sponsorship"},
    {"name": "Amara Nkosi", "location": "Kampala, Uganda",
     "slug": "amara-nkosi-kampala-uganda", "has_full_story": True,
     "headline": "Skills training helped Amara create work for others",
     "programme": "vocational", "story": "After tailoring training, Amara now runs a small workshop.",
     "challenge": "Amara had talent but no certified skills.",
     "intervention": "COSMA supported vocational training and startup guidance.",
     "outcome": "Her work supports her household and trains three apprentices.",
     "quote": "I learned how to sew, price my work, and keep records.", "author": "Webadmin",
     "image": "imgs/about-us.jpeg", "tag": "Vocational"},
]

FALLBACK_PROGRAMS = [
    {"icon": "bi-book-half",    "title": "Education Access",  "description": "Scholarships, school supplies, and mentorship for 2,400+ learners.", "color": "#3BAD6E", "stat_label": "2,400+ Learners"},
    {"icon": "bi-heart-pulse",  "title": "Community Health",  "description": "Mobile clinics, maternal care, and nutrition programmes.",           "color": "#8E0005", "stat_label": "15,000+ Served"},
    {"icon": "bi-briefcase",    "title": "Livelihoods",        "description": "Vocational training, micro-finance, and market linkages.",            "color": "#3BAD6E", "stat_label": "800+ Entrepreneurs"},
    {"icon": "bi-droplet-half", "title": "Clean Water",        "description": "Borehole drilling, rainwater harvesting, and WASH education.",        "color": "#8E0005", "stat_label": "40+ Villages"},
]

FALLBACK_PARTNERS = [
    {"name": "UNICEF",     "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Logo_of_UNICEF.svg/200px-Logo_of_UNICEF.svg.png",        "website": ""},
    {"name": "USAID",      "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/USAID-Identity.svg/200px-USAID-Identity.svg.png",          "website": ""},
    {"name": "WHO",        "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/WHO-EM.svg/200px-WHO-EM.svg.png",                          "website": ""},
    {"name": "World Bank", "get_logo": lambda: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/The_World_Bank_logo.svg/200px-The_World_Bank_logo.svg.png","website": ""},
]

FALLBACK_VALUES = [
    {"title": "Accountability",  "desc": "Transparency and integrity are at the heart of everything we do.",
     "color": "#8E0005", "_bg": "rgba(142,0,5,.1)", "icon": "bi-shield-check"},
    {"title": "Empowerment",     "desc": "We equip communities with the tools to break cycles of poverty.",
     "color": "#3BAD6E", "_bg": "rgba(59,173,110,.1)", "icon": "bi-people-fill"},
    {"title": "Sustainability",  "desc": "Creating long-term impact that benefits communities for generations.",
     "color": "#8E0005", "_bg": "rgba(142,0,5,.1)", "icon": "bi-recycle"},
]

FALLBACK_TEAM = [
    {"name": "Dr. Sarah Nakamya",  "role": "Board Chair",          "group": "board", "bio": "20 years in community development across East Africa.", "image": "https://images.unsplash.com/photo-1589156280159-27698a70f29e?w=400&q=80", "linkedin": "#", "twitter": "#", "email": ""},
    {"name": "James Okiror",       "role": "Director of Programs",  "group": "staff", "bio": "Agricultural economist and former UNDP programme officer.", "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80", "linkedin": "#", "twitter": "#", "email": ""},
    {"name": "Grace Atim",         "role": "Head of Education",     "group": "staff", "bio": "Former headteacher driving literacy and access.", "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=80", "linkedin": "#", "twitter": "#", "email": ""},
]

FALLBACK_GALLERY = [
    {"image": "imgs/kids.png",      "caption": "Children supported through learning and mentorship", "category": "education"},
    {"image": "imgs/hero2.jpg",     "caption": "Farmers building practical skills for stronger harvests", "category": "agriculture"},
    {"image": "imgs/about-us.jpeg", "caption": "COSMA staff working alongside community members", "category": "community"},
    {"image": "imgs/hero3.jpg",     "caption": "Families gathering for programme outreach", "category": "community"},
    {"image": "imgs/hero5.png",     "caption": "Young people in skills development", "category": "vocational"},
]

FALLBACK_TIMELINE = [
    {"year": "2006", "icon": "bi-house-heart",    "title": "The Beginning",            "desc": "cosma development was founded in Kampala. The first after-school programme launched, serving 42 children.", "stat": "42 children in Year 1", "image_src": "https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=600&q=80"},
    {"year": "2010", "icon": "bi-flower1",        "title": "Agriculture Programme",    "desc": "We launched our first cooperative model — connecting 120 smallholder farmers with inputs, training, and market access.", "stat": "120 farmers in first cohort", "image_src": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600&q=80"},
    {"year": "2016", "icon": "bi-briefcase",      "title": "Vocational Centres Open", "desc": "Two vocational training centres opened in Kampala and Jinja.", "stat": "600+ graduates in 2 years", "image_src": None},
    {"year": "2023", "icon": "bi-graph-up-arrow", "title": "125,000 Lives Impacted",  "desc": "Our annual impact count crossed 125,000 — 17 years of consistent work.", "stat": "125,000+ lives annually", "image_src": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=600&q=80"},
    {"year": "Today","icon": "bi-stars",          "title": "Looking Forward",          "desc": "With a plan to reach 250,000 beneficiaries by 2030, cosma development builds on 18 years of trust.", "stat": "Target: 250,000 by 2030", "image_src": None},
]

FALLBACK_HERO_STATS = [
    {"label": "Years of service",  "raw": 18,     "suffix": "+"},
    {"label": "Lives impacted",    "raw": 125000, "suffix": "+"},
    {"label": "Districts reached", "raw": 12,     "suffix": ""},
    {"label": "Fund efficiency",   "raw": 98,     "suffix": "%"},
]

FALLBACK_GOALS = [
    {"title": "Reach 250,000 Beneficiaries by 2030", "desc": "Double reach through expanded programming.",   "progress": 50},
    {"title": "100% School Retention",               "desc": "Every sponsored child completes their cycle.", "progress": 72},
    {"title": "1,000 New Farmer Cooperatives",        "desc": "Cooperatives in all 12 districts.",           "progress": 38},
]

FALLBACK_IMPACT_BIG = [
    {"value": "125,000+", "label": "Lives Impacted",          "icon": "bi-people-fill",    "color": "#8E0005"},
    {"value": "2,400+",   "label": "Students in School",      "icon": "bi-book-half",      "color": "#3BAD6E"},
    {"value": "4,200+",   "label": "Farmers Supported",       "icon": "bi-flower1",        "color": "#8E0005"},
    {"value": "40+",      "label": "Clean Water Sites",       "icon": "bi-droplet-half",   "color": "#3BAD6E"},
    {"value": "800+",     "label": "Entrepreneurs Trained",   "icon": "bi-briefcase",      "color": "#8E0005"},
    {"value": "12",       "label": "Districts Reached",       "icon": "bi-geo-alt-fill",   "color": "#3BAD6E"},
    {"value": "15,000+",  "label": "Health Consultations",    "icon": "bi-heart-pulse",    "color": "#8E0005"},
    {"value": "98%",      "label": "Fund Efficiency",         "icon": "bi-graph-up-arrow", "color": "#3BAD6E"},
]

FALLBACK_IMPACT_PROG = [
    {"label": "Education — Students retained",             "value": "2,400+", "pct": 85, "color": "#3BAD6E"},
    {"label": "Agriculture — Farmers with increased yields","value": "4,200+", "pct": 72, "color": "#8E0005"},
    {"label": "Health — Communities with clinic access",   "value": "68%",    "pct": 68, "color": "#3BAD6E"},
    {"label": "Water — Villages with clean water",         "value": "40+",    "pct": 55, "color": "#8E0005"},
    {"label": "Vocational — Graduates now self-employed",  "value": "78%",    "pct": 78, "color": "#3BAD6E"},
    {"label": "Sponsorship — Children completing P7",      "value": "94%",    "pct": 94, "color": "#8E0005"},
]

FALLBACK_IMPACT_ITEMS = [
    {"emoji": "👧", "figure": "2,400+", "desc": "children kept in school each year"},
    {"emoji": "🌾", "figure": "4,200+", "desc": "farmers with better harvests and income"},
    {"emoji": "💧", "figure": "40+",    "desc": "clean water sites across 8 districts"},
    {"emoji": "🏥", "figure": "15,000+","desc": "health consultations delivered annually"},
]

FALLBACK_STATS = [
    {"value": "125,000+", "label": "Lives Impacted"},
    {"value": "98%",      "label": "Fund Efficiency"},
    {"value": "12",       "label": "Districts"},
    {"value": "18+",      "label": "Years"},
]

FALLBACK_VOCATIONAL = [
    {"title": "Tailoring & Fashion Design", "desc": "Garment construction, pattern making, and business skills.", "icon": "bi-scissors", "duration": "3 Months"},
    {"title": "Carpentry & Joinery",        "desc": "Practical wood-working for furniture and construction.",     "icon": "bi-tools",    "duration": "4 Months"},
    {"title": "Catering & Hospitality",     "desc": "Professional cooking, food safety, and hospitality.",       "icon": "bi-cup-hot",  "duration": "3 Months"},
    {"title": "Solar & Electrical",         "desc": "Installation and maintenance of solar systems.",            "icon": "bi-lightning-fill", "duration": "4 Months"},
    {"title": "Hair & Beauty",              "desc": "Hairdressing, salon management, and cosmetology.",          "icon": "bi-stars",    "duration": "3 Months"},
    {"title": "Financial Literacy",         "desc": "Budgeting, saving, and small business management.",         "icon": "bi-cash-stack","duration": "6 Weeks"},
]

FALLBACK_AGRI_STEPS = [
    {"title": "Farmer Assessment",    "desc": "Detailed assessment of each farmer's land, resources, and challenges."},
    {"title": "Training & Capacity",  "desc": "Hands-on training in modern techniques and climate-smart agriculture."},
    {"title": "Input Support",        "desc": "Quality seeds, fertilisers, and tools at subsidised rates."},
    {"title": "Market Linkages",      "desc": "Connecting farmers to buyers, cooperatives, and digital marketplaces."},
    {"title": "Monitoring & Follow-up","desc": "Regular field visits and data to track progress."},
    {"title": "Cooperative Formation","desc": "Supporting farmers to form cooperatives for collective bargaining."},
]

FALLBACK_SPONSOR_STEPS = [
    {"title": "Choose a Giving Level", "desc": "Select a monthly or annual amount that works for you."},
    {"title": "Complete Your Details", "desc": "Fill in contact and payment details securely."},
    {"title": "Get Matched",           "desc": "We match you with a child and send their profile."},
    {"title": "Receive Updates",       "desc": "Get regular updates, photos, and progress reports."},
]

FALLBACK_PARTNERSHIP_TYPES = [
    {"title": "Corporate Sponsor",   "desc": "Align your brand with measurable community impact.",     "icon": "bi-building",   "color": "#8E0005", "bg": "rgba(142,0,5,.1)"},
    {"title": "Institutional Grant", "desc": "Fund a specific programme through grant partnerships.",  "icon": "bi-bank",       "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)"},
    {"title": "In-Kind Support",     "desc": "Donate goods, services, or expertise.",                 "icon": "bi-box-seam",   "color": "#8E0005", "bg": "rgba(142,0,5,.1)"},
    {"title": "Community Partner",   "desc": "Local organisations extend our reach in their districts.","icon": "bi-people-fill","color": "#3BAD6E", "bg": "rgba(59,173,110,.1)"},
]

FALLBACK_VOLUNTEER_ROLES = [
    {"title": "Teaching & Tutoring",    "desc": "Support literacy and numeracy in our learning centres.", "icon": "bi-mortarboard",  "color": "#8E0005", "bg": "rgba(142,0,5,.1)",    "commitment": "Min. 1 month"},
    {"title": "Healthcare & Medical",   "desc": "Health professionals supporting mobile clinic teams.",   "icon": "bi-heart-pulse",  "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)", "commitment": "Min. 2 weeks"},
    {"title": "Agriculture",            "desc": "Agronomists sharing techniques with farmer cooperatives.","icon": "bi-flower1",      "color": "#8E0005", "bg": "rgba(142,0,5,.1)",    "commitment": "Min. 1 month"},
    {"title": "Communications & Media", "desc": "Photographers and writers helping tell our story.",      "icon": "bi-camera",       "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)", "commitment": "Flexible"},
    {"title": "IT & Technology",        "desc": "Developers and data analysts supporting digital work.",  "icon": "bi-laptop",       "color": "#8E0005", "bg": "rgba(142,0,5,.1)",    "commitment": "Flexible / Remote"},
    {"title": "Fundraising & Events",   "desc": "Help organise fundraising campaigns and outreach.",      "icon": "bi-megaphone",    "color": "#3BAD6E", "bg": "rgba(59,173,110,.1)", "commitment": "Flexible"},
]

IMPACT_FILTERS = {
    'agriculture': {
        'label': 'Agriculture',
        'hero': 'Agriculture Impact Stories',
        'description': 'Stories of smallholder farmers building resilient livelihoods through agriculture.',
        'tags': ['Agriculture', 'Livelihoods'],
        'programme': 'agriculture',
        'icon': 'bi-flower1',
    },
    'child-sponsorship': {
        'label': 'Child Sponsorship',
        'hero': 'Child Sponsorship Impact Stories',
        'description': "Stories of children whose education journey is strengthened through sponsorship.",
        'tags': ['Child Sponsorship', 'Sponsorship', 'Education'],
        'programme': 'child_sponsorship',
        'icon': 'bi-mortarboard',
    },
}

DONATE_FAQS = [
    {"q": "How is my donation processed?",            "a": "Donations are processed securely through GlobalGiving. You receive an email confirmation and official receipt immediately."},
    {"q": "Can I donate in other currencies?",        "a": "Yes. GlobalGiving accepts USD, GBP, EUR, and other major currencies."},
    {"q": "Is my donation tax-deductible?",           "a": "We issue official receipts. Tax eligibility depends on your country."},
    {"q": "Can I set up a recurring donation?",       "a": "Yes — select Monthly during the donation process on GlobalGiving."},
    {"q": "How do I know funds reach beneficiaries?", "a": "We publish audited annual reports. 98% of all donations go directly to programmes."},
    {"q": "Can I donate to a specific programme?",    "a": "Yes. Contact us for restricted gift arrangements."},
]

FALLBACK_FAQS = [
    {"category": "agriculture", "q": "Who can join the agriculture programme?", "a": "Smallholder farmers in COSMA-supported communities."},
    {"category": "agriculture", "q": "What is the Village Cooperative Model?", "a": "A community-led system that organizes farmers into cooperatives for shared training, financing, input access, and collective market participation."},
    {"category": "agriculture", "q": "How does COSMA support farmers to access finance?", "a": "Through village savings groups, deferred-input financing, and training in financial planning so households can invest in productivity."},
    {"category": "child_sponsorship", "q": "Is the Education Program the same as Sponsor a Child?", "a": "Yes. In this website, the Education Program is delivered through our child sponsorship programme, which helps children stay in school while also strengthening household livelihoods."},
    {"category": "child_sponsorship", "q": "What does the Education Program cover?", "a": "It combines school fee support, learning materials, mentorship, wellbeing care, and household income support through the Enterprise-to-Education model."},
    {"category": "child_sponsorship", "q": "How does sponsorship help a family become self-reliant?", "a": "Families receive income-generation support alongside education support so they can gradually begin contributing to school costs on their own."},
    {"category": "child_sponsorship", "q": "Can I receive updates about the child I sponsor?", "a": "Yes. Sponsors receive progress reports, photos, and stories that keep you connected to the child’s education journey."},
    {"category": "donations", "q": "Can I donate to a specific programme?", "a": "Yes. Contact us to discuss directed support for the Education Program, Agriculture Programme, or specific project wishlist items."},
]


# ─────────────────────────────────────────────────────────────────────────────
#  VIEWS
# ─────────────────────────────────────────────────────────────────────────────

def index(request):
    site = _settings()
    try:
        slides = list(HomeSlide.objects.filter(is_active=True)) or []
        stats  = list(HomeStat.objects.all()) or FALLBACK_STATS
        stories   = list(_impact_story_queryset(featured_only=True)[:3]) or FALLBACK_STORIES[:3]
        programs  = list(Program.objects.all()) or FALLBACK_PROGRAMS
        partners  = list(Partner.objects.all()) or FALLBACK_PARTNERS
        approved  = Testimonial.objects.filter(is_approved=True)
        testimonials = list(approved.filter(is_featured=True).order_by('order', '-created_at')[:6])
        if not testimonials:
            testimonials = list(approved.order_by('order', '-created_at')[:6])
        latest_news = list(NewsPost.objects.filter(is_published=True).order_by('-published_at')[:4])
        impact_items = list(ImpactItem.objects.all()) or FALLBACK_IMPACT_ITEMS
    except Exception:
        slides, stats, stories, programs, partners = [], FALLBACK_STATS, FALLBACK_STORIES[:3], FALLBACK_PROGRAMS, FALLBACK_PARTNERS
        testimonials, latest_news, impact_items = [], [], FALLBACK_IMPACT_ITEMS

    ctx = {
        'hero': _hero('home'),
        'site': site,
        'slides': slides,
        'stats': stats,
        'stories': stories,
        'programs': programs,
        'partners': partners,
        'testimonials': testimonials,
        'latest_news': latest_news,
        'impact_items': impact_items,
        'globalgiving_url': site.globalgiving_url,
    }
    return render(request, 'index.html', ctx)


def logo_view(request):
    return render(request, 'logo.html')

def our_approach(request):
    principles = [
        {'icon': 'bi-people-fill',   'title': 'Community Ownership',  'desc': 'Communities are active drivers, not passive recipients, of their own development.'},
        {'icon': 'bi-arrow-repeat',  'title': 'Long-Term Systems',     'desc': 'We build local systems that sustain progress beyond external support.'},
        {'icon': 'bi-diagram-3',     'title': 'Collective Action',     'desc': 'We organise communities into cooperatives and groups for shared strength.'},
        {'icon': 'bi-graph-up-arrow','title': 'Measurable Impact',     'desc': 'Every intervention is tracked, reported, and evaluated for real outcomes.'},
    ]
    ctx = {
        'hero': _hero('our_approach'),
        'site': _settings(),
        'principles': principles,
    }
    ctx.update(get_seo('our_approach'))
    return render(request, 'about-us/our_approach.html', ctx)


def our_story(request):
    try:
        timeline   = list(TimelineEvent.objects.order_by('order')) or FALLBACK_TIMELINE
        hero_stats = list(HeroStat.objects.order_by('order')) or FALLBACK_HERO_STATS
        goals      = list(OrgGoal.objects.order_by('order')) or FALLBACK_GOALS
    except Exception:
        timeline, hero_stats, goals = FALLBACK_TIMELINE, FALLBACK_HERO_STATS, FALLBACK_GOALS

    ctx = {
        'hero': _hero('our_story'),
        'site': _settings(),
        'timeline': timeline,
        'hero_stats': hero_stats,
        'values': _values(),
        'goals': goals,
    }
    ctx.update(get_seo('our_story'))
    return render(request, 'about-us/our_story.html', ctx)


def team_partners(request):
    try:
        partners = list(Partner.objects.all()) or FALLBACK_PARTNERS
    except Exception:
        partners = FALLBACK_PARTNERS
    team = _team_members()
    ctx = {
        'hero': _hero('team_partners'),
        'site': _settings(),
        'team': team,
        'team_groups': _team_groups(team),
        'partners': partners,
    }
    ctx.update(get_seo('team_partners'))
    return render(request, 'about-us/team-partners.html', ctx)


def resources(request):
    try:
        published = Resource.objects.filter(is_published=True)
        featured  = published.filter(is_featured=True).first()
        res_list  = list(published.exclude(pk=featured.pk) if featured else published)
    except Exception:
        featured, res_list = None, []
    ctx = {
        'hero': _hero('resources'),
        'site': _settings(),
        'featured': featured,
        'resources': res_list,
    }
    ctx.update(get_seo('resources'))
    return render(request, 'about-us/resources.html', ctx)


def about_us(request):
    mvp = _mvp()
    try:
        partners = list(Partner.objects.all()) or FALLBACK_PARTNERS
    except Exception:
        partners = FALLBACK_PARTNERS
    team = _team_members()
    ctx = {
        'hero': _hero('about'),
        'site': _settings(),
        'mvp': mvp,
        'values': _values(),
        'team': team,
        'team_groups': _team_groups(team),
        'partners': partners,
    }
    ctx.update(get_seo('about_us'))
    return render(request, 'about-us/about-us.html', ctx)


# Legacy redirects
def mission_vision(request): return redirect('cosma_development:our_story')
def core_values(request):    return redirect('cosma_development:our_story')
def our_team(request):       return redirect('cosma_development:team_partners')
def our_partners(request):   return redirect('cosma_development:team_partners')


def agri_why(request):
    ctx = {'hero': _hero('agri_why'), 'site': _settings()}
    ctx.update(get_seo('agri_why'))
    return render(request, 'programs/agri_why.html', ctx)


def agri_approach(request):
    try:
        steps = list(AgriApproachStep.objects.order_by('order')) or FALLBACK_AGRI_STEPS
    except Exception:
        steps = FALLBACK_AGRI_STEPS
    ctx = {'hero': _hero('agri_approach'), 'site': _settings(), 'approach_steps': steps}
    ctx.update(get_seo('agri_approach'))
    return render(request, 'programs/agri_approach.html', ctx)


def agri_support(request):
    ctx = {'hero': _hero('agri_support'), 'site': _settings()}
    ctx.update(get_seo('agri_support'))
    return render(request, 'programs/agri_support.html', ctx)


def agri_impact(request):
    return redirect(f"{reverse('cosma_development:impact_stories')}?program=agriculture")


def agri_faqs(request):
    try:
        faqs = list(_published_faqs('agriculture')) or [f for f in FALLBACK_FAQS if f.get('category') == 'agriculture']
    except Exception:
        faqs = [f for f in FALLBACK_FAQS if f.get('category') == 'agriculture']
    ctx = {
        'hero': _hero('agri_faqs'), 'site': _settings(),
        'program_title': 'Agriculture FAQs', 'program_label': 'Agriculture Programme',
        'program_icon': 'bi-flower1', 'faqs': faqs,
    }
    ctx.update(get_seo('agri_faqs'))
    return render(request, 'programs/faqs.html', ctx)


def sponsor_why(request):
    ctx = {'hero': _hero('sponsor_why'), 'site': _settings()}
    ctx.update(get_seo('sponsor_why'))
    return render(request, 'programs/sponsor_why.html', ctx)


def sponsor_child(request):
    try:
        steps = list(SponsorStep.objects.order_by('order')) or FALLBACK_SPONSOR_STEPS
    except Exception:
        steps = FALLBACK_SPONSOR_STEPS
    ctx = {'hero': _hero('sponsor_child'), 'site': _settings(), 'sponsor_steps': steps}
    ctx.update(get_seo('sponsor_child'))
    return render(request, 'programs/sponsor_child.html', ctx)


def vocational(request):
    try:
        courses = list(VocationalCourse.objects.filter(is_active=True).order_by('order')) or FALLBACK_VOCATIONAL
    except Exception:
        courses = FALLBACK_VOCATIONAL
    ctx = {'hero': _hero('vocational'), 'site': _settings(), 'courses': courses}
    ctx.update(get_seo('vocational'))
    return render(request, 'programs/vocational.html', ctx)


def sponsorship_impact(request):
    return redirect(f"{reverse('cosma_development:impact_stories')}?program=child-sponsorship")


def sponsorship_faqs(request):
    try:
        faqs = list(_published_faqs('child_sponsorship')) or [f for f in FALLBACK_FAQS if f.get('category') == 'child_sponsorship']
    except Exception:
        faqs = [f for f in FALLBACK_FAQS if f.get('category') == 'child_sponsorship']
    ctx = {
        'hero': _hero('sponsorship_faqs'), 'site': _settings(),
        'program_title': 'Child Sponsorship FAQs', 'program_label': 'Child Sponsorship',
        'program_icon': 'bi-mortarboard', 'faqs': faqs,
    }
    ctx.update(get_seo('sponsorship_faqs'))
    return render(request, 'programs/faqs.html', ctx)


def faqs(request):
    try:
        items = _published_faqs()
        groups = _faq_groups(items)
        if not groups:
            groups = _faq_groups(FALLBACK_FAQS)
    except Exception:
        groups = _faq_groups(FALLBACK_FAQS)
    ctx = {'hero': _hero('faqs'), 'site': _settings(), 'faq_groups': groups}
    ctx.update(get_seo('faqs'))
    return render(request, 'faqs.html', ctx)


def impact_numbers(request):
    try:
        big_stats      = list(ImpactBigStat.objects.order_by('order')) or FALLBACK_IMPACT_BIG
        programme_stats = list(ImpactProgrammeStat.objects.order_by('order')) or FALLBACK_IMPACT_PROG
    except Exception:
        big_stats, programme_stats = FALLBACK_IMPACT_BIG, FALLBACK_IMPACT_PROG
    ctx = {
        'hero': _hero('impact_numbers'), 'site': _settings(),
        'big_stats': big_stats, 'programme_stats': programme_stats,
    }
    ctx.update(get_seo('impact_numbers'))
    return render(request, 'impact/impact_numbers.html', ctx)


def impact_stories(request):
    active_program = request.GET.get('program', '').strip()
    active_filter  = IMPACT_FILTERS.get(active_program)
    try:
        stories = list(_impact_story_queryset(active_program, featured_only=True)) or _filter_fallback_stories(active_program)
    except Exception:
        stories = _filter_fallback_stories(active_program)
    ctx = {
        'hero': _hero('impact_stories'), 'site': _settings(),
        'stories': stories,
        'filters': IMPACT_FILTERS,
        'active_program': active_program,
        'active_filter': active_filter,
        'hero_title': active_filter['hero'] if active_filter else 'Impact Stories',
        'hero_description': active_filter['description'] if active_filter else 'Behind every statistic is a person. These are their stories.',
    }
    ctx.update(get_seo('impact_stories'))
    return render(request, 'impact/impact_stories.html', ctx)


def impact_story_detail(request, slug):

    story = get_object_or_404(
        ImpactStory,
        slug=slug
    )

    related_stories = ImpactStory.objects.filter(
        programme=story.programme
    ).exclude(id=story.id)[:3]

    context = {
        'story': story,
        'related_stories': related_stories,
    }

    return render(
        request,
        'impact/impact_story_detail.html',
        context
    )

def gallery(request):
    try:
        gallery_photos = list(GalleryImage.objects.filter(is_published=True))
    except Exception:
        gallery_photos = []
    ctx = {
        'hero': _hero('gallery'), 'site': _settings(),
        'fallback_photos': FALLBACK_GALLERY, 'gallery_photos': gallery_photos,
    }
    ctx.update(get_seo('gallery'))
    return render(request, 'impact/gallery.html', ctx)




def partner_with_us(request):
    """Updated with exact content from requirements document."""
    ways = [
        {
            'title': 'Sponsor a Child',
            'desc':  'Support a child\'s education by contributing to school fees, healthcare, and essential learning needs — while strengthening the household systems that sustain their future.',
            'icon':  'bi-person-plus',
            'color': '#8E0005',
            'bg':    'rgba(142,0,5,.1)',
            'cta':   'Learn More',
            'url':   'cosma_development:sponsor_child',
        },
        {
            'title': 'Support a Farmer',
            'desc':  'Help farmers access training, quality agricultural inputs, and financial support to improve productivity and increase their incomes.',
            'icon':  'bi-flower1',
            'color': '#3BAD6E',
            'bg':    'rgba(59,173,110,.1)',
            'cta':   'Donate to Agriculture',
            'url':   'cosma_development:donate_page',
        },
        {
            'title': 'Volunteer',
            'desc':  'Share your time and skills to support our programmes and expand our reach across rural communities.',
            'icon':  'bi-person-heart',
            'color': '#8E0005',
            'bg':    'rgba(142,0,5,.1)',
            'cta':   'Learn More',
            'url':   'cosma_development:volunteer',
        },
        {
            'title': 'Share Our Story',
            'desc':  'Help us raise awareness by sharing our work within your networks and communities.',
            'icon':  'bi-share',
            'color': '#3BAD6E',
            'bg':    'rgba(59,173,110,.1)',
            'cta':   'Read More',
            'url':   'cosma_development:share_story',
        },
        {
            'title': 'Fund a Project',
            'desc':  'Support a specific initiative from our project wishlist and directly contribute to community transformation.',
            'icon':  'bi-bullseye',
            'color': '#8E0005',
            'bg':    'rgba(142,0,5,.1)',
            'cta':   'View Wishlist',
            'url':   'cosma_development:fund_project',
        },
        {
            'title': 'Stay Connected',
            'desc':  'Subscribe to receive updates on our programmes, impact stories, and opportunities to get involved.',
            'icon':  'bi-bell-fill',
            'color': '#3BAD6E',
            'bg':    'rgba(59,173,110,.1)',
            'cta':   'Subscribe',
            'url':   'cosma_development:signup_updates',
        },
    ]
    try:
        partnership_types = list(PartnershipType.objects.order_by('order')) or FALLBACK_PARTNERSHIP_TYPES
    except Exception:
        partnership_types = FALLBACK_PARTNERSHIP_TYPES
 
    ctx = {
        'hero': _hero('partner_with_us'),
        'site': _settings(),
        'ways': ways,
        'partnership_types': partnership_types,
    }
    ctx.update(get_seo('partner_with_us'))
    return render(request, 'get-involved/partner_with_us.html', ctx)

def share_story(request):
    how_to_help = [
        'Celebrate special occasions by fundraising instead of receiving gifts.',
        'Share our work with friends, colleagues, and community groups.',
        'Organise awareness or fundraising events in universities, schools, churches, or social groups.',
        'Share our stories and updates on social media.',
    ]
    ctx = {
        'hero': _hero('share_story'),
        'site': _settings(),
        'how_to_help': how_to_help,
    }
    ctx.update(get_seo('share_story'))
    return render(request, 'get-involved/share_story.html', ctx)
def volunteer(request):
    """Updated with exact content from requirements document."""
    why_volunteer = [
        {
            'icon':  'bi-heart-fill',
            'color': 'var(--red)',
            'bg':    'rgba(142,0,5,.1)',
            'title': 'Make a Meaningful Impact',
            'desc':  'Contribute directly to programmes that strengthen livelihoods and enable children to access and stay in school in vulnerable rural communities in Uganda.',
        },
        {
            'icon':  'bi-graph-up-arrow',
            'color': 'var(--green)',
            'bg':    'rgba(59,173,110,.1)',
            'title': 'Build Skills & Experience',
            'desc':  'Apply and develop your skills in a real-world setting while contributing to sustainable community development.',
        },
        {
            'icon':  'bi-people-fill',
            'color': 'var(--red)',
            'bg':    'rgba(142,0,5,.1)',
            'title': 'Work Alongside Communities',
            'desc':  'Engage with farmers, women, youth, and families actively working to improve their lives and build resilient futures.',
        },
        {
            'icon':  'bi-globe-africa',
            'color': 'var(--green)',
            'bg':    'rgba(59,173,110,.1)',
            'title': 'Drive Sustainable Change',
            'desc':  'Be part of a community-driven approach that creates lasting, self-sustaining transformation — not just short-term relief.',
        },
    ]
 
    how_to_contribute = [
        'Support farmer training in sustainable climate-smart agriculture and financial literacy.',
        'Mentor and support children in education programmes.',
        'Assist in organising community events and workshops.',
        'Provide expertise in resource mobilisation, communication, financial management, or project management.',
        'Lead fundraising initiatives in your community through churches, universities, schools, social clubs, family gatherings, or workplaces.',
    ]
 
    try:
        volunteer_roles = list(VolunteerRole.objects.filter(is_active=True).order_by('order')) or FALLBACK_VOLUNTEER_ROLES
    except Exception:
        volunteer_roles = FALLBACK_VOLUNTEER_ROLES
 
    ctx = {
        'hero': _hero('volunteer'),
        'site': _settings(),
        'volunteer_roles': volunteer_roles,
        'why_volunteer': why_volunteer,
        'how_to_contribute': how_to_contribute,
    }
    ctx.update(get_seo('volunteer'))
    return render(request, 'get-involved/volunteer.html', ctx)
 
def signup_updates(request):
    ctx = {'hero': _hero('signup_updates'), 'site': _settings()}
    ctx.update(get_seo('signup_updates'))
    return render(request, 'get-involved/signup_updates.html', ctx)


def contact_page(request):
    site = _settings()
    ctx = {'hero': _hero('contact'), 'site': site}
    ctx.update(get_seo('contact'))
    return render(request, 'contact.html', ctx)


def news_list(request):
    active_category = request.GET.get('cat', '')
    qs = NewsPost.objects.filter(is_published=True)
    if active_category:
        qs = qs.filter(category=active_category)
    featured  = NewsPost.objects.filter(is_published=True, is_featured=True).first()
    paginator = Paginator(qs.exclude(pk=featured.pk) if featured else qs, 9)
    posts     = paginator.get_page(request.GET.get('page', 1))
    ctx = {
        'hero': _hero('news'), 'site': _settings(),
        'posts': posts, 'featured': featured,
        'categories': NewsPost.CATEGORIES, 'active_category': active_category,
    }
    ctx.update(get_seo('news'))
    return render(request, 'news/news_list.html', ctx)


def news_detail(request, slug):
    post    = get_object_or_404(NewsPost, slug=slug, is_published=True)
    related = NewsPost.objects.filter(is_published=True, category=post.category).exclude(pk=post.pk).order_by('-published_at')[:3]
    site    = _settings()
    ctx = {
        'post': post, 'related': related,
        'site': site, 'globalgiving_url': site.globalgiving_url,
    }
    ctx.update(get_seo('news_detail'))
    return render(request, 'news/news_detail.html', ctx)


def submit_testimonial(request):
    submitted = False
    if request.method == 'POST':
        name   = request.POST.get('name', '').strip()
        role   = request.POST.get('role', 'other')
        org    = request.POST.get('organisation', '').strip()
        body   = request.POST.get('body', '').strip()
        rating = int(request.POST.get('rating', 5))
        photo  = request.FILES.get('photo')
        if name and body:
            t = Testimonial(name=name, role=role, organisation=org, body=body, rating=rating, is_approved=True)
            if photo:
                t.photo = photo
            t.save()
            submitted = True
    ctx = {'submitted': submitted, 'site': _settings()}
    ctx.update(get_seo('submit_testimonial'))
    return render(request, 'news/submit_testimonial.html', ctx)


def donate_page(request):
    site = _settings()
    try:
        impact_items = list(ImpactItem.objects.order_by('order')) or FALLBACK_IMPACT_ITEMS
        stories      = list(ImpactStory.objects.filter(is_featured=True)[:3]) or FALLBACK_STORIES[:3]
        big_stats    = list(ImpactBigStat.objects.order_by('order')[:4]) or FALLBACK_IMPACT_BIG[:4]
    except Exception:
        impact_items, stories, big_stats = FALLBACK_IMPACT_ITEMS, FALLBACK_STORIES[:3], FALLBACK_IMPACT_BIG[:4]
    ctx = {
        'hero': _hero('donate'), 'site': site,
        'globalgiving_url': site.globalgiving_url,
        'impact_items': impact_items,
        'impact_stats': big_stats,
        'stories': stories,
        'faqs': DONATE_FAQS,
    }
    ctx.update(get_seo('donate'))
    return render(request, 'donate.html', ctx)


# ─── API endpoints ────────────────────────────────────────────────────────────

def donate(request):
    try:
        data = json.loads(request.body)
        try:
            DonationLead.objects.create(
                name=data.get('name', ''), email=data.get('email', ''),
                amount=data.get('amount', 0), message=data.get('message', ''))
        except Exception:
            pass
        return JsonResponse({'status': 'success', 'message': 'Thank you for your generous donation!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def contact(request):
    try:
        data = json.loads(request.body)
        ContactMessage.objects.create(
            name=data.get('name', ''), email=data.get('email', ''),
            subject=data.get('subject', 'Website Enquiry'), message=data.get('message', ''))
        return JsonResponse({'status': 'success', 'message': 'Message received. We will be in touch shortly.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
def fund_project(request):
    """Project wishlist page """
    projects = [
        {
            'title':        'Mobile Irrigation System',
            'desc':         'Climate change is increasing drought risks, limiting farmers\' ability to produce year-round. A mobile irrigation system will enable water distribution to farms during dry seasons, supporting continuous production, improving food security, and stabilising household incomes.',
            'amount':        27400,
            'amount_display':'27,400',
            'icon':         'bi-droplet-half',
            'funded_pct':   0,
            'image':        'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=700&q=80',
        },
        {
            'title':        'Motorcycle',
            'desc':         'Reaching farmers in remote areas remains a challenge. A motorcycle will enable our team to deliver training, monitor progress, and respond quickly to farmer needs — ensuring consistent and timely support.',
            'amount':        2200,
            'amount_display':'2,200',
            'icon':         'bi-bicycle',
            'funded_pct':   0,
            'image':        'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=700&q=80',
        },
        {
            'title':        'Maize Milling Machine',
            'desc':         'A milling machine will allow farmers to process maize into higher-value products like cornmeal and animal feeds, improving market competitiveness and significantly increasing earnings per harvest.',
            'amount':        12350,
            'amount_display':'12,350',
            'icon':         'bi-gear-fill',
            'funded_pct':   0,
            'image':        'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=700&q=80',
        },
        {
            'title':        'Walking Tractors',
            'desc':         'Most of our farmers rely on manual labour, which is physically demanding and time-consuming on larger plots. Walking tractors will enable farmers to cultivate larger areas efficiently, reducing labour intensity and increasing yields and income.',
            'amount':        19200,
            'amount_display':'19,200',
            'icon':         'bi-tools',
            'funded_pct':   0,
            'image':        'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=700&q=80',
        },
        {
            'title':        'Agricultural Warehouse',
            'desc':         'Farmers are often forced to sell produce at low farm-gate prices due to lack of storage. A warehouse will enable safe storage and strategic, delayed sales — allowing farmers to sell when market prices are more favourable.',
            'amount':        31440,
            'amount_display':'31,440',
            'icon':         'bi-building',
            'funded_pct':   0,
            'image':        'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=700&q=80',
        },
        {
            'title':        'Electric Paper Guillotine Machine',
            'desc':         'This machine will improve the quality and efficiency of book production under our Enterprise-to-Education programme — enabling us to produce high-quality books that generate income for vulnerable households.',
            'amount':        4800,
            'amount_display':'4,800',
            'icon':         'bi-book-half',
            'funded_pct':   0,
            'image':        'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=700&q=80',
        },
    ]
    ctx = {
        'hero': _hero('fund_project'),
        'site': _settings(),
        'projects': projects,
        'total_amount': sum(p['amount'] for p in projects),
    }
    ctx.update(get_seo('fund_project'))
    return render(request, 'get-involved/fund_project.html', ctx)
 