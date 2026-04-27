from django.db import models

import os


class ImpactStory(models.Model):
    PROGRAMME_CHOICES = [
        ('agriculture', 'Agriculture'),
        ('child_sponsorship', 'Child Sponsorship'),
        ('vocational', 'Vocational & Life Skills'),
        ('education', 'Education'),
        ('health', 'Health'),
        ('water', 'Clean Water'),
        ('community', 'Community Development'),
    ]
    name        = models.CharField(max_length=120)
    location    = models.CharField(max_length=120)
    headline    = models.CharField(max_length=180, blank=True, help_text='Short impact-story headline shown on cards.')
    programme   = models.CharField(max_length=30, choices=PROGRAMME_CHOICES, default='community')
    story       = models.TextField()
    challenge   = models.TextField(blank=True, help_text='What problem did this person, family, or community face?')
    intervention= models.TextField(blank=True, help_text='What did COSMA and partners provide?')
    outcome     = models.TextField(blank=True, help_text='What changed? Include concrete human results where possible.')
    quote       = models.CharField(max_length=260, blank=True, help_text='Optional direct quote from the participant or family.')
    image       = models.ImageField(upload_to='stories/', blank=True)
    tag         = models.CharField(max_length=60)
    author      = models.CharField(max_length=120, default='Webadmin')
    is_featured = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = 'Impact Stories'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.name} — {self.location}"


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
    ICON_CHOICES = [('bi-book-half','Book'),('bi-heart-pulse','Heart Pulse'),('bi-briefcase','Briefcase'),('bi-droplet-half','Droplet'),('bi-house-heart','House Heart'),('bi-people-fill','People')]
    COLOR_CHOICES = [('#8E0005','Red'),('#3BAD6E','Green')]
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
    GROUP_CHOICES = [
        ('board', 'Board Member'),
        ('staff', 'Staff'),
    ]

    name        = models.CharField(max_length=120)
    role        = models.CharField(max_length=120)
    group       = models.CharField(max_length=20, choices=GROUP_CHOICES, default='staff')
    bio         = models.TextField(blank=True)
    photo       = models.ImageField(upload_to='team/', blank=True)
    image_url   = models.URLField(blank=True, help_text='Optional external image URL if no photo is uploaded.')
    email       = models.EmailField(blank=True)
    linkedin    = models.URLField(blank=True)
    twitter     = models.URLField(blank=True)
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveSmallIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['group', 'order', 'name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return f"{self.name} - {self.role}"

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
        ('education', 'Education'),
        ('agriculture', 'Agriculture'),
        ('health', 'Health'),
        ('community', 'Community'),
        ('water', 'Water'),
        ('sponsorship', 'Child Sponsorship'),
        ('vocational', 'Vocational Training'),
    ]

    image        = models.ImageField(upload_to='gallery/')
    caption      = models.CharField(max_length=255)
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='community')
    order        = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Gallery Photo'
        verbose_name_plural = 'Gallery Photos'

    def __str__(self):
        return self.caption

    @property
    def image_url(self):
        return self.image.url if self.image else ''


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('agriculture', 'Agriculture'),
        ('child_sponsorship', 'Child Sponsorship'),
        ('vocational', 'Vocational & Life Skills'),
        ('donations', 'Donations'),
        ('volunteering', 'Volunteering'),
        ('partnerships', 'Partnerships'),
        ('general', 'General'),
    ]

    question     = models.CharField(max_length=255)
    answer       = models.TextField()
    category     = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    is_published = models.BooleanField(default=True)
    order        = models.PositiveSmallIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', '-created_at']
        verbose_name = 'FAQ'
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
        return f"{self.name} — UGX {self.amount:,}"


class ContactMessage(models.Model):
    name       = models.CharField(max_length=120)
    email      = models.EmailField()
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read    = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name}: {self.subject}"


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
    description   = models.TextField(help_text='Short summary shown on the card (1–2 sentences).')
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPES, default='annual_report')
    file          = models.FileField(upload_to='resources/%Y/', help_text='Upload PDF, DOCX, ZIP, or image.')
    cover_image   = models.ImageField(upload_to='resources/covers/', blank=True, help_text='Optional cover thumbnail.')
    year          = models.PositiveSmallIntegerField(help_text='Publication year e.g. 2024')
    pages         = models.PositiveSmallIntegerField(blank=True, null=True, help_text='Number of pages (optional)')
    is_featured   = models.BooleanField(default=False, help_text='Show as the hero Latest Report at top of page')
    is_published  = models.BooleanField(default=True,  help_text='Uncheck to hide from the public page')
    order         = models.PositiveSmallIntegerField(default=0, help_text='Lower = shown first')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'order', '-created_at']
        verbose_name        = 'Resource'
        verbose_name_plural = 'Resources'

    def __str__(self):
        return f"{self.title} ({self.year})"

    @property
    def file_size_display(self):
        try:
            size = self.file.size
            for unit in ['B','KB','MB','GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} GB"
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
        if ext == 'pdf':  return '📄'
        if ext in ('doc','docx'): return '📝'
        if ext in ('xls','xlsx'): return '📊'
        if ext in ('ppt','pptx'): return '📋'
        if ext == 'zip':  return '📦'
        return {'annual_report':'📊','research':'🔬','policy_brief':'📋','programme_update':'📢','media_kit':'🖼','other':'📁'}.get(self.resource_type,'📁')


# ═══════════════════════════════════════════════════════════════════
#  TESTIMONIAL
# ═══════════════════════════════════════════════════════════════════

class Testimonial(models.Model):
    ROLE_TYPES = [
        ('donor',       'Donor'),
        ('volunteer',   'Volunteer'),
        ('partner',     'Partner Organisation'),
        ('beneficiary', 'Beneficiary'),
        ('community',   'Community Member'),
        ('other',       'Other'),
    ]
    name        = models.CharField(max_length=120, help_text='Full name of the person')
    role        = models.CharField(max_length=20, choices=ROLE_TYPES, default='donor')
    organisation= models.CharField(max_length=120, blank=True, help_text='Organisation or location (optional)')
    body        = models.TextField(help_text='The testimonial text — keep it to 2–4 sentences for best display.')
    photo       = models.ImageField(upload_to='testimonials/', blank=True, help_text='Headshot (optional but recommended)')
    rating      = models.PositiveSmallIntegerField(default=5, help_text='Star rating 1–5')
    is_approved = models.BooleanField(default=False, help_text='Only approved testimonials show on the website')
    is_featured = models.BooleanField(default=False, help_text='Show in the homepage featured row')
    order       = models.PositiveSmallIntegerField(default=0, help_text='Lower = shown first')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name        = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

    @property
    def stars_html(self):
        return '★' * self.rating + '☆' * (5 - self.rating)


# ═══════════════════════════════════════════════════════════════════
#  NEWS POST
# ═══════════════════════════════════════════════════════════════════

class NewsPost(models.Model):
    CATEGORIES = [
        ('programmes',  'Programmes'),
        ('community',   'Community'),
        ('events',      'Events'),
        ('agriculture', 'Agriculture'),
        ('education',   'Education'),
        ('health',      'Health'),
        ('water',       'Clean Water'),
        ('partnerships','Partnerships'),
        ('announcements','Announcements'),
    ]

    title        = models.CharField(max_length=220)
    slug         = models.SlugField(max_length=240, unique=True, blank=True,
                                    help_text='Leave blank — auto-generated from title')
    category     = models.CharField(max_length=30, choices=CATEGORIES, default='announcements')
    summary      = models.CharField(max_length=300,
                                    help_text='One-sentence summary shown on cards (max 300 chars)')
    body         = models.TextField(help_text='Full article body. HTML is supported.')
    cover_image  = models.ImageField(upload_to='news/covers/', blank=True,
                                     help_text='Cover image shown on card and article header')
    author       = models.CharField(max_length=120, default='cosma development Team')
    is_published = models.BooleanField(default=False,
                                       help_text='Check to make this article visible on the website')
    is_featured  = models.BooleanField(default=False,
                                       help_text='Pin to top of news feed as the featured story')
    published_at = models.DateTimeField(blank=True, null=True,
                                        help_text='Leave blank to use today\'s date when publishing')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name        = 'News Post'
        verbose_name_plural = 'News Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.title)[:230]
            slug = base
            n = 1
            while NewsPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        # Auto-set published_at on first publish
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def read_time(self):
        """Rough read-time estimate based on word count."""
        words = len(self.body.split())
        minutes = max(1, round(words / 200))
        return f"{minutes} min read"

    @property
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        # Default placeholder keyed to category
        placeholders = {
            'agriculture': 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800&q=80',
            'education':   'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=800&q=80',
            'health':      'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80',
            'water':       'https://images.unsplash.com/photo-1594608661623-aa0bd3a69d98?w=800&q=80',
            'community':   'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&q=80',
        }
        return placeholders.get(self.category,
               'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=800&q=80')

class MissionVisionPurpose(models.Model):
    mission=models.TextField()
    vision=models.TextField()
    purpose=models.TextField()
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return "organisation Content"
    
class CoreValue(models.Model):
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    mission_vision = models.ForeignKey(
        MissionVisionPurpose,
        on_delete=models.CASCADE,
        related_name='core_values'
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
   