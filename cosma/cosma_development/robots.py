"""
This file is served at /robots.txt to tell search engine crawlers
which pages to index and where the sitemap lives.
"""
ROBOTS_TXT = """User-agent: *
Allow: /

# Block admin and API from indexing
Disallow: /admin/
Disallow: /api/

# Sitemap location
Sitemap: https://www.cosmadevelopments.ug/sitemap.xml
"""

from django.http import HttpResponse

def robots_txt(request):
    return HttpResponse(ROBOTS_TXT, content_type="text/plain")
