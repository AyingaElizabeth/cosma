from django.db import models
import os


# ═══════════════════════════════════════════════════════════════
#  SITE SETTINGS — global admin-controlled content
# ═══════════════════════════════════════════════════════════════

class SiteSettings(models.Model):
    """One-row settings table for global site content."""
    # Contact info
    office_address  = models.CharField(max_length=255, default='Plot 45, Kampala Road, Kampala, Uganda')
    phone           = models.CharField(max_length=50, default='+256 700 123 456')
    email           = models.EmailField(default='info@cosmadevelopments.org')
    office_hours    = models.CharField(max_length=200, default='Mon–Fri: 8am – 5pm | Sat: 9am – 1pm')
    # Social
    facebook_url    = models.URLField(blank=True)
    twitter_url     = models.URLField(blank=True)
    instagram_url   = models.URLField(blank=True)
    linkedin_url    = models.URLField(blank=True)
    youtube_url     = models.URLField(blank=True)
    # Donation
    globalgiving_url = models.URLField(
        default='https://www.globalgiving.org/donate/11831/cosma-sustainable-rural-development/')
    # Footer tagline
    footer_tagline  = models.CharField(
        max_length=300,
        default='Building resilient communities across Uganda through education, health, livelihoods, and clean water since 2006.')
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ═══════════════════════════════════════════════════════════════
#  HERO SECTION — per-page hero images + content
# ═══════════════════════════════════════════════════════════════

class HeroSection(models.Model):
    PAGE_CHOICES = [
        ('home',               'Home Page'),
        ('about',              'About Us — Who We Are'),
        ('our_approach',       'About Us — Our Approach'),          # NEW
        ('our_story',          'Our Story'),
        ('team_partners',      'Team & Partners'),
        ('resources',          'Resources'),
        ('agri_why',           'Agriculture – Why Agriculture'),
        ('agri_approach',      'Agriculture – Our Approach'),
        ('agri_support',       'Agriculture – Support a Farmer'),
        ('agri_impact',        'Agriculture – Impact Stories'),
        ('agri_faqs',          'Agriculture – FAQs'),
        ('sponsor_why',        'Sponsorship – Why Sponsorship'),
        ('sponsor_child',      'Sponsorship – Sponsor a Child'),
        ('vocational',         'Sponsorship – Vocational & Life Skills'),
        ('sponsorship_impact', 'Sponsorship – Impact Stories'),
        ('sponsorship_faqs',   'Sponsorship – FAQs'),
        ('impact_numbers',     'Impact in Numbers'),
        ('impact_stories',     'Impact Stories'),
        ('gallery',            'Gallery'),
        ('partner_with_us',    'Partner With Us'),
        ('volunteer',          'Volunteer With Us'),
        ('fund_project',       'Fund a Project — Wishlist'),        # NEW
        ('share_story',        'Share Our Story'),
        ('signup_updates',     'Sign Up for Updates'),
        ('news',               'News & Updates'),
        ('contact',            'Contact'),
        ('donate',             'Donate'),
        ('faqs',               'FAQs'),
]
    page        = models.CharField(max_length=40, choices=PAGE_CHOICES, unique=True)
    tag_text    = models.CharField(max_length=80,  blank=True, help_text='Small pill label above the heading')
    tag_icon    = models.CharField(max_length=40,  blank=True, default='bi-stars',
                                   help_text='Bootstrap icon class e.g. bi-globe-africa')
    heading     = models.CharField(max_length=200, blank=True)
    subheading  = models.TextField(blank=True, help_text='Paragraph text below the heading')
    # Image options: upload takes priority, then URL, then CSS gradient
    image       = models.ImageField(upload_to='heroes/', blank=True,
                                    help_text='Upload a hero image (recommended ≥1800×900px)')
    image_url   = models.URLField(blank=True,
                                  help_text='Or paste an external image URL')
    overlay_opacity = models.FloatField(
        default=0.55,
        help_text='Dark overlay strength 0 (none) → 1 (full black). Default 0.55')
    is_active   = models.BooleanField(default=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['page']
        verbose_name        = 'Hero Section'
        verbose_name_plural = 'Hero Sections'

    def __str__(self):
        return f'{self.get_page_display()} Hero'

    @property
    def bg_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ''


# ═══════════════════════════════════════════════════════════════
#  HOME PAGE SECTIONS
# ═══════════════════════════════════════════════════════════════

class HomeSlide(models.Model):
    """Hero slider slides on the home page."""
    image       = models.ImageField(upload_to='home_slides/', blank=True)
    image_url   = models.URLField(blank=True)
    caption     = models.CharField(max_length=200, blank=True)
    order       = models.PositiveSmallIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Home Slide'
        verbose_name_plural = 'Home Slides'

    def __str__(self):
        return f'Slide {self.order}: {self.caption or "(no caption)"}'

    @property
    def bg_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ''


class HomeStat(models.Model):
    """Animated counters in the hero strip."""
    value   = models.CharField(max_length=20, help_text='Display value e.g. "125,000+" or "98%"')
    raw     = models.PositiveIntegerField(help_text='Numeric value for the counter animation')
    suffix  = models.CharField(max_length=10, blank=True, help_text='Appended to the counter e.g. "+"')
    label   = models.CharField(max_length=80)
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name        = 'Home Stat'
        verbose_name_plural = 'Home Stats'

    def __str__(self):
        return f'{self.value} — {self.label}'


class ImpactItem(models.Model):
    """Emoji + figure cards in the Donate section."""
    emoji   = models.CharField(max_length=10)
    figure  = models.CharField(max_length=30)
    desc    = models.CharField(max_length=200)
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name        = 'Impact Item (Donate)'
        verbose_name_plural = 'Impact Items (Donate)'

    def __str__(self):
        return f'{self.figure} — {self.desc}'


# ═══════════════════════════════════════════════════════════════
#  MISSION / VISION / PURPOSE + CORE VALUES
# ═══════════════════════════════════════════════════════════════

class MissionVisionPurpose(models.Model):
    mission = models.TextField()
    vision  = models.TextField()
    purpose = models.TextField()
    # Goal (displayed as full-width card on About page)
    goal    = models.TextField(
        blank=True,
        help_text='Organisation goal statement shown beneath Mission & Vision')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Mission, Vision & Purpose'
        verbose_name_plural = 'Mission, Vision & Purpose'

    def __str__(self):
        return 'Organisation Content'


class CoreValue(models.Model):
    title           = models.CharField(max_length=100)
    icon            = models.CharField(max_length=50, blank=True,
                                       help_text='Bootstrap icon class e.g. bi-shield-check')
    description     = models.TextField(blank=True)
    order           = models.PositiveSmallIntegerField(default=0)
    mission_vision  = models.ForeignKey(
        MissionVisionPurpose, on_delete=models.CASCADE, related_name='core_values')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# ═══════════════════════════════════════════════════════════════
#  OUR STORY — TIMELINE EVENTS
# ═══════════════════════════════════════════════════════════════

class TimelineEvent(models.Model):
    year    = models.CharField(max_length=10, help_text='e.g. "2006" or "Today"')
    icon    = models.CharField(max_length=50, default='bi-star',
                               help_text='Bootstrap icon class e.g. bi-house-heart')
    title   = models.CharField(max_length=200)
    desc    = models.TextField()
    stat    = models.CharField(max_length=120, blank=True,
                               help_text='Optional statistic pill e.g. "42 children in Year 1"')
    image   = models.ImageField(upload_to='timeline/', blank=True)
    image_url = models.URLField(blank=True)
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Timeline Event'
        verbose_name_plural = 'Timeline Events'

    def __str__(self):
        return f'{self.year}: {self.title}'

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url or None


class OrgGoal(models.Model):
    """2025–2030 strategic goals shown on the Our Story page."""
    title    = models.CharField(max_length=200)
    desc     = models.TextField()
    progress = models.PositiveSmallIntegerField(default=0, help_text='Percentage 0–100')
    order    = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Organisation Goal'
        verbose_name_plural = 'Organisation Goals'

    def __str__(self):
        return self.title


class HeroStat(models.Model):
    """Stats shown in the Our Story hero stat strip."""
    label   = models.CharField(max_length=80)
    raw     = models.PositiveIntegerField()
    suffix  = models.CharField(max_length=10, blank=True)
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Our-Story Hero Stat'
        verbose_name_plural = 'Our-Story Hero Stats'

    def __str__(self):
        return f'{self.raw}{self.suffix} — {self.label}'


# ═══════════════════════════════════════════════════════════════
#  PROGRAMME PAGES — VOCATIONAL COURSES
# ═══════════════════════════════════════════════════════════════

class VocationalCourse(models.Model):
    title    = models.CharField(max_length=200)
    desc     = models.TextField()
    icon     = models.CharField(max_length=50, default='bi-tools',
                                help_text='Bootstrap icon class')
    duration = models.CharField(max_length=50, help_text='e.g. "3 Months"')
    order    = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Vocational Course'
        verbose_name_plural = 'Vocational Courses'

    def __str__(self):
        return self.title


class AgriApproachStep(models.Model):
    title = models.CharField(max_length=200)
    desc  = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Agriculture Approach Step'
        verbose_name_plural = 'Agriculture Approach Steps'

    def __str__(self):
        return self.title


class SponsorStep(models.Model):
    title = models.CharField(max_length=200)
    desc  = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Sponsor-a-Child Step'
        verbose_name_plural = 'Sponsor-a-Child Steps'

    def __str__(self):
        return self.title


# ═══════════════════════════════════════════════════════════════
#  PARTNERSHIP TYPES
# ═══════════════════════════════════════════════════════════════

class PartnershipType(models.Model):
    title  = models.CharField(max_length=200)
    desc   = models.TextField()
    icon   = models.CharField(max_length=50, default='bi-building')
    color  = models.CharField(max_length=20, default='#8E0005')
    bg     = models.CharField(max_length=40, default='rgba(142,0,5,.1)')
    order  = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Partnership Type'
        verbose_name_plural = 'Partnership Types'

    def __str__(self):
        return self.title


# ═══════════════════════════════════════════════════════════════
#  VOLUNTEER ROLES
# ═══════════════════════════════════════════════════════════════

class VolunteerRole(models.Model):
    title      = models.CharField(max_length=200)
    desc       = models.TextField()
    icon       = models.CharField(max_length=50, default='bi-person-heart')
    color      = models.CharField(max_length=20, default='#3BAD6E')
    bg         = models.CharField(max_length=40, default='rgba(59,173,110,.1)')
    commitment = models.CharField(max_length=80, help_text='e.g. "Min. 1 month"')
    order      = models.PositiveSmallIntegerField(default=0)
    is_active  = models.BooleanField(default=True)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Volunteer Role'
        verbose_name_plural = 'Volunteer Roles'

    def __str__(self):
        return self.title


# ═══════════════════════════════════════════════════════════════
#  IMPACT — BIG STATS & PROGRAMME STATS
# ═══════════════════════════════════════════════════════════════

class ImpactBigStat(models.Model):
    value   = models.CharField(max_length=30)
    label   = models.CharField(max_length=120)
    icon    = models.CharField(max_length=50, default='bi-people-fill')
    color   = models.CharField(max_length=20, default='#8E0005')
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Impact Big Stat'
        verbose_name_plural = 'Impact Big Stats'

    def __str__(self):
        return f'{self.value} — {self.label}'


class ImpactProgrammeStat(models.Model):
    label   = models.CharField(max_length=200)
    value   = models.CharField(max_length=30)
    pct     = models.PositiveSmallIntegerField(help_text='Bar width % 0–100')
    color   = models.CharField(max_length=20, default='#3BAD6E')
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering            = ['order']
        verbose_name        = 'Impact Programme Stat'
        verbose_name_plural = 'Impact Programme Stats'

    def __str__(self):
        return self.label


# ═══════════════════════════════════════════════════════════════
#  EXISTING MODELS (unchanged, reproduced for completeness)
# ═══════════════════════════════════════════════════════════════

class ImpactStory(models.Model):
    PROGRAMME_CHOICES = [
        ('agriculture',       'Agriculture'),
        ('child_sponsorship', 'Child Sponsorship'),
        ('vocational',        'Vocational & Life Skills'),
        ('education',         'Education'),
        ('health',            'Health'),
        ('water',             'Clean Water'),
        ('community',         'Community Development'),
    ]
    name         = models.CharField(max_length=120)
    location     = models.CharField(max_length=120)
    headline     = models.CharField(max_length=180, blank=True)
    programme    = models.CharField(max_length=30, choices=PROGRAMME_CHOICES, default='community')
    story        = models.TextField()
    challenge    = models.TextField(blank=True)
    intervention = models.TextField(blank=True)
    outcome      = models.TextField(blank=True)
    quote        = models.CharField(max_length=260, blank=True)
    image        = models.ImageField(upload_to='stories/', blank=True)
    tag          = models.CharField(max_length=60)
    author       = models.CharField(max_length=120, default='Webadmin')
    is_featured  = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Impact Stories'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.location}'

    @property
    def display_title(self):
        return self.headline or f"{self.name}'s story"

    @property
    def narrative(self):
        return self.quote or self.story

    @property
    def image_url(self):
        return self.image.url if self.image else ''


class Program(models.Model):
    ICON_CHOICES = [
        ('bi-book-half', 'Book'), ('bi-heart-pulse', 'Heart Pulse'),
        ('bi-briefcase', 'Briefcase'), ('bi-droplet-half', 'Droplet'),
        ('bi-house-heart', 'House Heart'), ('bi-people-fill', 'People'),
        ('bi-flower1', 'Flower'), ('bi-tools', 'Tools'),
    ]
    COLOR_CHOICES = [('#8E0005', 'Red'), ('#3BAD6E', 'Green')]
    title       = models.CharField(max_length=120)
    description = models.TextField()
    icon        = models.CharField(max_length=40, choices=ICON_CHOICES, default='bi-book-half')
    color       = models.CharField(max_length=10, choices=COLOR_CHOICES, default='#3BAD6E')
    stat_label  = models.CharField(max_length=60)
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    GROUP_CHOICES = [('board', 'Board Member'), ('staff', 'Staff')]
    name       = models.CharField(max_length=120)
    role       = models.CharField(max_length=120)
    group      = models.CharField(max_length=20, choices=GROUP_CHOICES, default='staff')
    bio        = models.TextField(blank=True)
    photo      = models.ImageField(upload_to='team/', blank=True)
    image_url  = models.URLField(blank=True)
    email      = models.EmailField(blank=True)
    linkedin   = models.URLField(blank=True)
    twitter    = models.URLField(blank=True)
    is_active  = models.BooleanField(default=True)
    order      = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['group', 'order', 'name']
        verbose_name        = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return f'{self.name} - {self.role}'

    @property
    def image_src(self):
        if self.photo:
            return self.photo.url
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=500&q=80'


class Partner(models.Model):
    name     = models.CharField(max_length=120)
    logo     = models.ImageField(upload_to='partners/', blank=True)
    logo_url = models.URLField(blank=True)
    website  = models.URLField(blank=True)
    order    = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_logo(self):
        return self.logo.url if self.logo else self.logo_url


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('education', 'Education'), ('agriculture', 'Agriculture'),
        ('health', 'Health'), ('community', 'Community'),
        ('water', 'Water'), ('sponsorship', 'Child Sponsorship'),
        ('vocational', 'Vocational Training'),
    ]
    image        = models.ImageField(upload_to='gallery/')
    caption      = models.CharField(max_length=255)
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='community')
    order        = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ['order', '-created_at']
        verbose_name        = 'Gallery Photo'
        verbose_name_plural = 'Gallery Photos'

    def __str__(self):
        return self.caption

    @property
    def image_url(self):
        return self.image.url if self.image else ''


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('agriculture',       'Agriculture'),
        ('child_sponsorship', 'Child Sponsorship'),
        ('vocational',        'Vocational & Life Skills'),
        ('donations',         'Donations'),
        ('volunteering',      'Volunteering'),
        ('partnerships',      'Partnerships'),
        ('general',           'General'),
    ]
    question     = models.CharField(max_length=255)
    answer       = models.TextField()
    category     = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    is_published = models.BooleanField(default=True)
    order        = models.PositiveSmallIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['category', 'order', '-created_at']
        verbose_name        = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class DonationLead(models.Model):
    name       = models.CharField(max_length=120)
    email      = models.EmailField()
    amount     = models.DecimalField(max_digits=12, decimal_places=2)
    message    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} — UGX {self.amount:,}'


class ContactMessage(models.Model):
    name       = models.CharField(max_length=120)
    email      = models.EmailField()
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read    = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}: {self.subject}'


class Resource(models.Model):
    RESOURCE_TYPES = [
        ('annual_report',    'Annual Report'),
        ('research',         'Research Publication'),
        ('policy_brief',     'Policy Brief'),
        ('programme_update', 'Programme Update'),
        ('media_kit',        'Media Kit'),
        ('other',            'Other'),
    ]
    title         = models.CharField(max_length=200)
    description   = models.TextField()
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPES, default='annual_report')
    file          = models.FileField(upload_to='resources/%Y/')
    cover_image   = models.ImageField(upload_to='resources/covers/', blank=True)
    year          = models.PositiveSmallIntegerField()
    pages         = models.PositiveSmallIntegerField(blank=True, null=True)
    is_featured   = models.BooleanField(default=False)
    is_published  = models.BooleanField(default=True)
    order         = models.PositiveSmallIntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['-year', 'order', '-created_at']
        verbose_name        = 'Resource'
        verbose_name_plural = 'Resources'

    def __str__(self):
        return f'{self.title} ({self.year})'

    @property
    def file_size_display(self):
        try:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f'{size:.1f} {unit}'
                size /= 1024
        except Exception:
            return ''

    @property
    def get_file_ext(self):
        try:
            return os.path.splitext(self.file.name)[1].lstrip('.').upper()
        except Exception:
            return 'FILE'

    @property
    def get_thumb_icon(self):
        ext = self.get_file_ext.lower()
        if ext == 'pdf': return '📄'
        if ext in ('doc', 'docx'): return '📝'
        if ext in ('xls', 'xlsx'): return '📊'
        if ext in ('ppt', 'pptx'): return '📋'
        if ext == 'zip': return '📦'
        return {'annual_report': '📊', 'research': '🔬', 'policy_brief': '📋',
                'programme_update': '📢', 'media_kit': '🖼', 'other': '📁'}.get(self.resource_type, '📁')


class Testimonial(models.Model):
    ROLE_TYPES = [
        ('donor',       'Donor'),
        ('volunteer',   'Volunteer'),
        ('partner',     'Partner Organisation'),
        ('beneficiary', 'Beneficiary'),
        ('community',   'Community Member'),
        ('other',       'Other'),
    ]
    name         = models.CharField(max_length=120)
    role         = models.CharField(max_length=20, choices=ROLE_TYPES, default='donor')
    organisation = models.CharField(max_length=120, blank=True)
    body         = models.TextField()
    photo        = models.ImageField(upload_to='testimonials/', blank=True)
    rating       = models.PositiveSmallIntegerField(default=5)
    is_approved  = models.BooleanField(default=False)
    is_featured  = models.BooleanField(default=False)
    order        = models.PositiveSmallIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ['order', '-created_at']
        verbose_name        = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f'{self.name} ({self.get_role_display()})'

    @property
    def stars_html(self):
        return '★' * self.rating + '☆' * (5 - self.rating)


class NewsPost(models.Model):
    CATEGORIES = [
        ('programmes',    'Programmes'),
        ('community',     'Community'),
        ('events',        'Events'),
        ('agriculture',   'Agriculture'),
        ('education',     'Education'),
        ('health',        'Health'),
        ('water',         'Clean Water'),
        ('partnerships',  'Partnerships'),
        ('announcements', 'Announcements'),
    ]
    title        = models.CharField(max_length=220)
    slug         = models.SlugField(max_length=240, unique=True, blank=True)
    category     = models.CharField(max_length=30, choices=CATEGORIES, default='announcements')
    summary      = models.CharField(max_length=300)
    body         = models.TextField(help_text='Full article body. HTML supported.')
    cover_image  = models.ImageField(upload_to='news/covers/', blank=True)
    author       = models.CharField(max_length=120, default='cosma development Team')
    is_published = models.BooleanField(default=False)
    is_featured  = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['-published_at', '-created_at']
        verbose_name        = 'News Post'
        verbose_name_plural = 'News Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.title)[:230]
            slug, n = base, 1
            while NewsPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def read_time(self):
        words = len(self.body.split())
        return f'{max(1, round(words / 200))} min read'

    @property
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        placeholders = {
            'agriculture': 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800&q=80',
            'education':   'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=800&q=80',
            'health':      'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80',
            'water':       'https://images.unsplash.com/photo-1594608661623-aa0bd3a69d98?w=800&q=80',
            'community':   'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&q=80',
        }
        return placeholders.get(
            self.category,
            'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=800&q=80')