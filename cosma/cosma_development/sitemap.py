"""
cosma_development/sitemap.py
Django sitemap framework — tells Google about every page.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import date


class StaticPageSitemap(Sitemap):
    protocol  = "https"
    i18n      = False

    # (url_name, priority, changefreq)
    PAGES = [
        ("cosma_development:index",              1.0,  "weekly"),
        ("cosma_development:about-us",           0.9,  "monthly"),
        ("cosma_development:our_approach",       0.9,  "monthly"),   # NEW
        ("cosma_development:our_story",          0.8,  "monthly"),
        ("cosma_development:team_partners",      0.7,  "monthly"),
        ("cosma_development:resources",          0.7,  "monthly"),
        ("cosma_development:agri_why",           0.9,  "monthly"),
        ("cosma_development:agri_approach",      0.8,  "monthly"),
        ("cosma_development:agri_support",       0.9,  "weekly"),
        ("cosma_development:agri_impact",        0.8,  "weekly"),
        ("cosma_development:agri_faqs",          0.7,  "monthly"),
        ("cosma_development:sponsor_why",        0.9,  "monthly"),
        ("cosma_development:sponsorship_impact", 0.8,  "weekly"),
        ("cosma_development:sponsor_child",      0.9,  "weekly"),
        ("cosma_development:vocational",         0.8,  "monthly"),
        ("cosma_development:sponsorship_faqs",   0.7,  "monthly"),
        ("cosma_development:impact_numbers",     0.8,  "monthly"),
        ("cosma_development:impact_stories",     0.9,  "weekly"),
        ("cosma_development:gallery",            0.7,  "weekly"),
        ("cosma_development:partner_with_us",    0.8,  "monthly"),
        ("cosma_development:volunteer",          0.8,  "monthly"),
        ("cosma_development:fund_project",       0.9,  "monthly"),   # NEW
        ("cosma_development:share_story",        0.7,  "monthly"),
        ("cosma_development:signup_updates",     0.6,  "monthly"),
        ("cosma_development:news",               0.8,  "weekly"),
        ("cosma_development:faqs",               0.7,  "monthly"),
        ("cosma_development:contact",            0.7,  "yearly"),
        ("cosma_development:donate_page",        0.9,  "monthly"),
    ]

    def items(self):
        return self.PAGES

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]

    def lastmod(self, item):
        return date.today()


class ImpactStorySitemap(Sitemap):
    """Dynamic sitemap for ImpactStory model pages (future use)."""
    protocol   = "https"
    changefreq = "weekly"
    priority   = 0.8

    def items(self):
        try:
            from .models import ImpactStory
            return ImpactStory.objects.filter(is_featured=True)
        except Exception:
            return []

    def lastmod(self, obj):
        return obj.created_at.date() if hasattr(obj, "created_at") else date.today()


class NewsPostSitemap(Sitemap):
    """Dynamic sitemap for published news articles."""
    protocol   = "https"
    changefreq = "weekly"
    priority   = 0.7

    def items(self):
        try:
            from .models import NewsPost
            return NewsPost.objects.filter(is_published=True).order_by('-published_at')
        except Exception:
            return []

    def location(self, obj):
        return reverse('cosma_development:news_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at.date() if hasattr(obj, 'updated_at') else date.today()