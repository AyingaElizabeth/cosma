from django.db import models

# Create your models here.
class ImpactStory(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    story = models.TextField()
    image = models.ImageField(upload_to='stories/', blank=True)
    tag = models.CharField(max_length=60)
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Impact Stories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.location}"


class Program(models.Model):
    ICON_CHOICES = [
        ('bi-book-half', 'Book'),
        ('bi-heart-pulse', 'Heart Pulse'),
        ('bi-briefcase', 'Briefcase'),
        ('bi-droplet-half', 'Droplet'),
        ('bi-house-heart', 'House Heart'),
        ('bi-people-fill', 'People'),
    ]
    COLOR_CHOICES = [
        ('#8E0005', 'Red'),
        ('#3BAD6E', 'Green'),
    ]
    title = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.CharField(max_length=40, choices=ICON_CHOICES, default='bi-book-half')
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='#3BAD6E')
    stat_label = models.CharField(max_length=60, help_text='e.g. 2,400+ Learners')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Partner(models.Model):
    name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to='partners/', blank=True)
    logo_url = models.URLField(blank=True, help_text='Use URL if not uploading a file')
    website = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_logo(self):
        if self.logo:
            return self.logo.url
        return self.logo_url


class DonationLead(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — UGX {self.amount:,}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}: {self.subject}"