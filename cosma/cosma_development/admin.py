from atexit import register
import csv, os
from datetime import date, timedelta
from decimal import Decimal
from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
from django.shortcuts import render


from .models import CoreValue, ImpactStory, MissionVisionPurpose, Program, TeamMember, Partner, GalleryImage, FAQ, DonationLead, ContactMessage, Resource

def export_csv(queryset, filename, fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    w = csv.writer(response)
    w.writerow(fields)
    for obj in queryset:
        w.writerow([str(getattr(obj, f, '')) for f in fields])
    return response


class cosmaAdminSite(admin.AdminSite):
    site_header = "cosma Uganda"
    site_title  = "cosma Admin"
    index_title = "Dashboard"
    site_url    = "/"

    def get_urls(self):
        urls = super().get_urls()
        return [path('', self.admin_view(self.dashboard_view), name='index')] + urls[1:]

    def dashboard_view(self, request):
        today      = date.today()
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        total_donations  = DonationLead.objects.aggregate(t=Sum('amount'))['t'] or Decimal('0')
        month_donations  = DonationLead.objects.filter(created_at__date__gte=this_month).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        last_m_donations = DonationLead.objects.filter(created_at__date__gte=last_month, created_at__date__lt=this_month).aggregate(t=Sum('amount'))['t'] or Decimal('1')
        mom_pct          = round(float((month_donations - last_m_donations) / last_m_donations * 100), 1)
        chart_labels, chart_data = [], []
        for i in range(5, -1, -1):
            d   = today - timedelta(days=30*i)
            mo  = d.replace(day=1)
            nxt = (mo.replace(month=mo.month%12+1,day=1) if mo.month<12 else mo.replace(year=mo.year+1,month=1,day=1))
            amt = DonationLead.objects.filter(created_at__date__gte=mo,created_at__date__lt=nxt).aggregate(t=Sum('amount'))['t'] or 0
            chart_labels.append(mo.strftime('%b %Y'))
            chart_data.append(float(amt))
        tags = ImpactStory.objects.values('tag').annotate(c=Count('id')).order_by('-c')
        ctx = dict(
            self.each_context(request), title='Dashboard',
            total_donations=total_donations, month_donations=month_donations, mom_pct=mom_pct,
            donation_count=DonationLead.objects.count(),
            unread_messages=ContactMessage.objects.filter(is_read=False).count(),
            total_messages=ContactMessage.objects.count(),
            featured_stories=ImpactStory.objects.filter(is_featured=True).count(),
            total_stories=ImpactStory.objects.count(),
            active_programs=Program.objects.count(),
            total_partners=Partner.objects.count(),
            total_resources=Resource.objects.filter(is_published=True).count(),
            total_users=User.objects.count(),
            recent_donations=DonationLead.objects.order_by('-created_at')[:7],
            recent_messages=ContactMessage.objects.order_by('-created_at')[:6],
            recent_stories=ImpactStory.objects.order_by('-created_at')[:5],
            chart_labels=chart_labels, chart_data=chart_data,
            tag_labels=[t['tag'] for t in tags], tag_data=[t['c'] for t in tags],
        )
        return render(request, 'admin/dashboard.html', ctx)


cosma_admin = cosmaAdminSite(name='admin')


@admin.register(ImpactStory, site=cosma_admin)
class ImpactStoryAdmin(admin.ModelAdmin):
    list_display = ('thumbnail','headline_col','name','programme','location','tag_badge','featured_badge','author','created_at')
    list_filter = ('is_featured','programme','tag','created_at')
    search_fields = ('headline','name','location','story','challenge','intervention','outcome','quote','tag','author')
    list_per_page = 20; date_hierarchy = 'created_at'
    readonly_fields = ('created_at','image_preview')
    list_display_links = ('thumbnail','headline_col','name')
    ordering = ('-created_at',)
    actions = ['make_featured','remove_featured','export_csv_action']
    fieldsets = (
        ('Person Details',{'fields':('name','location','programme','tag')}),
        ('NGO Impact Story',{'description':'Write for accountability and dignity: explain the need, what COSMA did, what changed, and include a participant quote when possible.','fields':('headline','story','challenge','intervention','outcome','quote','author')}),
        ('Photo',{'fields':('image','image_preview')}),
        ('Settings',{'fields':('is_featured','created_at'),'classes':('collapse',)}),
    )
    @admin.display(description='Headline')
    def headline_col(self, obj):
        return obj.display_title
    @admin.display(description='')
    def thumbnail(self, obj):
        if obj.image: return format_html('<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid #3BAD6E;"/>',obj.image.url)
        return format_html('<div style="width:40px;height:40px;border-radius:50%;background:#eee;display:flex;align-items:center;justify-content:center;">👤</div>')
    @admin.display(description='Tag')
    def tag_badge(self, obj):
        c={'Education':'#3BAD6E','Health':'#8E0005','Agriculture':'#E67E22','Livelihoods':'#2980B9','Clean Water':'#16A085','Empowerment':'#8E44AD'}.get(obj.tag,'#666')
        return format_html('<span style="background:{};color:#fff;padding:3px 10px;border-radius:50px;font-size:.75rem;font-weight:600;">{}</span>',c,obj.tag)
    @admin.display(description='Featured')
    def featured_badge(self, obj):
        return format_html('<span style="color:#3BAD6E;font-weight:600;">✔ Yes</span>') if obj.is_featured else format_html('<span style="color:#ccc;">Hidden</span>')
    @admin.display(description='Preview')
    def image_preview(self, obj):
        return format_html('<img src="{}" style="max-width:280px;border-radius:10px;"/>',obj.image.url) if obj.image else "No image yet"
    @admin.action(description='✔ Mark as Featured')
    def make_featured(self,req,qs): n=qs.update(is_featured=True); self.message_user(req,f'{n} stories marked as featured.',messages.SUCCESS)
    @admin.action(description='✖ Remove from Featured')
    def remove_featured(self,req,qs): n=qs.update(is_featured=False); self.message_user(req,f'{n} stories hidden.',messages.WARNING)
    @admin.action(description='⬇ Export to CSV')
    def export_csv_action(self,req,qs): return export_csv(qs,'impact_stories.csv',['headline','name','location','programme','tag','author','is_featured','created_at'])


@admin.register(Program, site=cosma_admin)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('icon_preview','title','color_swatch','stat_label','order')
    list_editable = ('order',); list_per_page = 20; search_fields = ('title','description'); ordering = ('order',)
    fieldsets = (('📋 Programme Details',{'fields':('title','description')}),('🎨 Appearance',{'fields':('icon','color')}),('📊 Stats & Order',{'fields':('stat_label','order')}),)
    @admin.display(description='Icon')
    def icon_preview(self,obj): return format_html('<div style="width:34px;height:34px;border-radius:8px;background:{};display:inline-flex;align-items:center;justify-content:center;color:#fff;font-size:.9rem;">{}</div>',obj.color,obj.icon.replace('bi-','').replace('-',' ')[:3].upper())
    @admin.display(description='Colour')
    def color_swatch(self,obj): name=dict(Program.COLOR_CHOICES).get(obj.color,obj.color); return format_html('<span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:16px;height:16px;border-radius:4px;background:{};border:1px solid rgba(0,0,0,.15);display:inline-block;"></span>{}</span>',obj.color,name)


@admin.register(TeamMember, site=cosma_admin)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('photo_thumb','name','role','group','is_active','order')
    list_editable = ('group','is_active','order')
    list_filter = ('group','is_active','created_at')
    search_fields = ('name','role','bio','email')
    readonly_fields = ('created_at','updated_at','photo_preview')
    list_display_links = ('photo_thumb','name')
    ordering = ('group','order','name')
    list_per_page = 30
    fieldsets = (
        ('Member Details', {'fields': ('name','role','group','bio')}),
        ('Photo', {'fields': ('photo','image_url','photo_preview')}),
        ('Contact Links', {'fields': ('email','linkedin','twitter')}),
        ('Display', {'fields': ('is_active','order')}),
        ('Audit', {'fields': ('created_at','updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='')
    def photo_thumb(self, obj):
        return format_html('<img src="{}" style="width:42px;height:42px;border-radius:50%;object-fit:cover;border:2px solid #3BAD6E;"/>', obj.image_src)

    @admin.display(description='Photo preview')
    def photo_preview(self, obj):
        return format_html('<img src="{}" style="max-width:240px;border-radius:12px;"/>', obj.image_src)


@admin.register(Partner, site=cosma_admin)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('logo_thumb','name','website_link','order'); list_editable = ('order',); list_per_page = 20; search_fields = ('name','website'); ordering = ('order',)
    fieldsets = (('🤝 Partner Info',{'fields':('name','website')}),('🖼 Logo',{'fields':('logo','logo_url')}),('⚙ Display',{'fields':('order',)}),)
    @admin.display(description='Logo')
    def logo_thumb(self,obj):
        src = obj.logo.url if obj.logo else obj.logo_url
        return format_html('<img src="{}" style="height:34px;max-width:90px;object-fit:contain;"/>',src) if src else format_html('<span style="color:#aaa;font-size:.8rem;">No logo</span>')
    @admin.display(description='Website')
    def website_link(self,obj): return format_html('<a href="{}" target="_blank" style="color:#3BAD6E;">🔗 Visit</a>',obj.website) if obj.website else '—'


@admin.register(GalleryImage, site=cosma_admin)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('thumb','caption','category','is_published','order','created_at')
    list_editable = ('is_published','order')
    list_filter = ('is_published','category','created_at')
    search_fields = ('caption',)
    readonly_fields = ('created_at','image_preview')
    ordering = ('order','-created_at')
    list_per_page = 30
    fieldsets = (
        ('Gallery Photo', {'fields': ('image','image_preview','caption','category')}),
        ('Display', {'fields': ('is_published','order','created_at')}),
    )

    @admin.display(description='')
    def thumb(self, obj):
        return format_html('<img src="{}" style="width:52px;height:40px;border-radius:6px;object-fit:cover;"/>', obj.image.url) if obj.image else ''

    @admin.display(description='Preview')
    def image_preview(self, obj):
        return format_html('<img src="{}" style="max-width:320px;border-radius:10px;"/>', obj.image.url) if obj.image else 'No image yet'


@admin.register(FAQ, site=cosma_admin)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question','category','is_published','order','updated_at')
    list_editable = ('is_published','order')
    list_filter = ('is_published','category','created_at')
    search_fields = ('question','answer')
    ordering = ('category','order','-created_at')
    list_per_page = 30
    fieldsets = (
        ('FAQ Content', {'fields': ('question','answer','category')}),
        ('Display', {'fields': ('is_published','order')}),
    )


@admin.register(DonationLead, site=cosma_admin)
class DonationLeadAdmin(admin.ModelAdmin):
    list_display = ('name','email','amount_formatted','level_badge','programme','created_at')
    list_filter = ('created_at',); search_fields = ('name','email','message'); readonly_fields = ('created_at','amount','name','email','message'); list_per_page = 25; date_hierarchy = 'created_at'; ordering = ('-created_at',); actions = ['export_csv_action']
    @admin.display(description='Amount (UGX)',ordering='amount')
    def amount_formatted(self,obj): v=int(obj.amount); c='#3BAD6E' if v>=100000 else ('#E67E22' if v>=50000 else '#8E0005'); return format_html('<strong style="color:{};">UGX {:,}</strong>',c,v)
    @admin.display(description='Level')
    def level_badge(self,obj):
        v=int(obj.amount)
        if v>=500000: lbl,c,s='Champion','#8E0005','★★★★★'
        elif v>=250000: lbl,c,s='Supporter','#3BAD6E','★★★★☆'
        elif v>=100000: lbl,c,s='Friend','#E67E22','★★★☆☆'
        else: lbl,c,s='Donor','#aaa','★★☆☆☆'
        return format_html('<span style="color:{};font-size:.85rem;" title="{}">{}</span>',c,lbl,s)
    @admin.display(description='Programme')
    def programme(self,obj): return obj.message or format_html('<em style="color:#bbb;">Not specified</em>')
    @admin.action(description='⬇ Export to CSV')
    def export_csv_action(self,req,qs): return export_csv(qs,'donations.csv',['name','email','amount','message','created_at'])


@admin.register(ContactMessage, site=cosma_admin)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('status_dot','name','email_link','subject','created_at','quick_reply')
    list_filter = ('is_read','created_at'); search_fields = ('name','email','subject','message'); readonly_fields = ('name','email','subject','message','created_at','quick_reply'); list_per_page = 25; date_hierarchy = 'created_at'; ordering = ('is_read','-created_at'); actions = ['mark_read','mark_unread','export_csv_action']
    fieldsets = (('📨 From',{'fields':('name','email','created_at')}),('💬 Message',{'fields':('subject','message')}),('⚙ Status',{'fields':('is_read','quick_reply')}),)
    @admin.display(description='')
    def status_dot(self,obj): c='#8E0005' if not obj.is_read else '#ddd'; t='Unread' if not obj.is_read else 'Read'; return format_html('<span style="width:10px;height:10px;border-radius:50%;background:{};display:inline-block;" title="{}"></span>',c,t)
    @admin.display(description='Email')
    def email_link(self,obj): return format_html('<a href="mailto:{}" style="color:#3BAD6E;">{}</a>',obj.email,obj.email)
    @admin.display(description='Reply')
    def quick_reply(self,obj): return format_html('<a href="mailto:{}?subject=Re: {}" style="background:#3BAD6E;color:#fff;padding:5px 12px;border-radius:6px;text-decoration:none;font-size:.8rem;">✉ Reply</a>',obj.email,obj.subject)
    @admin.action(description='✔ Mark as Read')
    def mark_read(self,req,qs): n=qs.update(is_read=True); self.message_user(req,f'{n} messages marked as read.',messages.SUCCESS)
    @admin.action(description='✖ Mark as Unread')
    def mark_unread(self,req,qs): n=qs.update(is_read=False); self.message_user(req,f'{n} messages marked as unread.',messages.INFO)
    @admin.action(description='⬇ Export to CSV')
    def export_csv_action(self,req,qs): return export_csv(qs,'messages.csv',['name','email','subject','message','is_read','created_at'])


# ═══════════════════ RESOURCE (reports & publications) ═══════════════════════

@admin.register(Resource, site=cosma_admin)
class ResourceAdmin(admin.ModelAdmin):
    list_display       = ('thumb_preview','title','type_badge','year','pages_col','size_col','featured_col','published_col','order')
    list_editable      = ('order',)
    list_filter        = ('resource_type','is_featured','is_published','year')
    search_fields      = ('title','description')
    list_per_page      = 20
    ordering           = ('-year','order')
    readonly_fields    = ('created_at','updated_at','file_preview_link','ext_ro','size_ro')
    list_display_links = ('thumb_preview','title')
    actions            = ['action_feature','action_publish','action_unpublish','export_csv_action']

    fieldsets = (
        ('📄 Publication Details', {
            'description': 'All fields appear on the public Resources page.',
            'fields': ('title','description','resource_type','year','pages'),
        }),
        ('📁 File Upload', {
            'description': 'Upload a PDF, DOCX, ZIP, or image. Recommended max size: 50 MB.',
            'fields': ('file','file_preview_link','ext_ro','size_ro','cover_image'),
        }),
        ('⚙ Visibility & Ordering', {
            'description': '"Featured" = hero report at top of page (one at a time). "Published" = visible on website.',
            'fields': ('is_published','is_featured','order'),
        }),
        ('🕒 Audit', {'fields': ('created_at','updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='')
    def thumb_preview(self, obj):
        if obj.pk and obj.cover_image:
            return format_html('<img src="{}" style="width:42px;height:42px;border-radius:8px;object-fit:cover;border:2px solid #E5E7EB;"/>',obj.cover_image.url)
        icon = obj.get_thumb_icon if obj.pk else '📁'
        return format_html('<div style="width:42px;height:42px;border-radius:8px;background:rgba(142,0,5,.08);display:flex;align-items:center;justify-content:center;font-size:1.25rem;">{}</div>',icon)

    @admin.display(description='Type')
    def type_badge(self, obj):
        pal = {'annual_report':('#8E0005','#FEE2E2'),'research':('#1D4ED8','#DBEAFE'),'policy_brief':('#6D28D9','#EDE9FE'),'programme_update':('#065F46','#D1FAE5'),'media_kit':('#92400E','#FEF3C7'),'other':('#374151','#F3F4F6')}
        fg,bg = pal.get(obj.resource_type,('#374151','#F3F4F6'))
        return format_html('<span style="background:{};color:{};padding:3px 10px;border-radius:50px;font-size:.72rem;font-weight:700;white-space:nowrap;">{}</span>',bg,fg,obj.get_resource_type_display())

    @admin.display(description='Pages')
    def pages_col(self, obj): return f"{obj.pages}pp" if obj.pages else '—'

    @admin.display(description='Size')
    def size_col(self, obj): return obj.file_size_display if obj.pk else '—'

    @admin.display(description='Featured')
    def featured_col(self, obj):
        return format_html('<span style="color:#D97706;font-weight:700;">⭐ Yes</span>') if obj.is_featured else format_html('<span style="color:#D1D5DB;">—</span>')

    @admin.display(description='Status')
    def published_col(self, obj):
        return format_html('<span style="color:#059669;font-weight:600;">✔ Live</span>') if obj.is_published else format_html('<span style="color:#DC2626;font-weight:600;">✖ Hidden</span>')

    @admin.display(description='File link')
    def file_preview_link(self, obj):
        if obj.pk and obj.file:
            return format_html('<a href="{}" target="_blank" style="color:#3BAD6E;font-weight:600;">🔗 Open {} ({}) in new tab</a>',obj.file.url,os.path.basename(obj.file.name),obj.get_file_ext)
        return format_html('<em style="color:#9CA3AF;">No file yet — save after uploading.</em>')

    @admin.display(description='Format')
    def ext_ro(self, obj): return obj.get_file_ext if obj.pk else '—'

    @admin.display(description='File size')
    def size_ro(self, obj): return obj.file_size_display if obj.pk else '—'

    @admin.action(description='⭐ Set as Featured report (clears others)')
    def action_feature(self, req, qs):
        Resource.objects.update(is_featured=False)
        n = qs.update(is_featured=True)
        self.message_user(req, f'{n} resource(s) set as featured. All others unset.', messages.SUCCESS)

    @admin.action(description='✔ Publish — make visible on website')
    def action_publish(self, req, qs):
        n = qs.update(is_published=True)
        self.message_user(req, f'{n} resources published.', messages.SUCCESS)

    @admin.action(description='✖ Unpublish — hide from website')
    def action_unpublish(self, req, qs):
        n = qs.update(is_published=False)
        self.message_user(req, f'{n} resources hidden.', messages.WARNING)

    @admin.action(description='⬇ Export to CSV')
    def export_csv_action(self, req, qs):
        return export_csv(qs,'resources.csv',['title','resource_type','year','pages','is_featured','is_published','order','created_at'])


from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
@admin.register(User,  site=cosma_admin)
class UserAdmin(BaseUserAdmin): pass
@admin.register(Group, site=cosma_admin)
class GroupAdmin(BaseGroupAdmin): pass


# ═══════════════════════════════════════════════════════════════════
#  TESTIMONIAL
# ═══════════════════════════════════════════════════════════════════

from .models import Testimonial, NewsPost


@admin.register(Testimonial, site=cosma_admin)
class TestimonialAdmin(admin.ModelAdmin):
    list_display       = ('photo_thumb', 'name', 'role_badge', 'organisation',
                          'stars_col', 'approved_col', 'featured_col', 'order', 'created_at')
    list_editable      = ('order',)
    list_filter        = ('is_approved', 'is_featured', 'role', 'created_at')
    search_fields      = ('name', 'organisation', 'body')
    list_per_page      = 25
    ordering           = ('is_approved', 'order', '-created_at')
    readonly_fields    = ('created_at', 'photo_preview')
    list_display_links = ('photo_thumb', 'name')
    actions            = ['approve', 'unapprove', 'make_featured', 'remove_featured', 'export_csv_action']

    fieldsets = (
        ('👤 Person', {
            'description': 'Who is giving this testimonial?',
            'fields': ('name', 'role', 'organisation', 'photo', 'photo_preview'),
        }),
        ('💬 Testimonial', {
            'fields': ('body', 'rating'),
            'description': 'Keep the testimonial to 2–4 sentences. Rating is 1–5 stars.',
        }),
        ('⚙ Visibility', {
            'fields': ('is_approved', 'is_featured', 'order'),
            'description': 'Only approved testimonials appear publicly. Featured = shown in homepage row.',
        }),
        ('🕒 Meta', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    @admin.display(description='')
    def photo_thumb(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid #3BAD6E;"/>', obj.photo.url)
        initials = ''.join(w[0].upper() for w in obj.name.split()[:2])
        return format_html('<div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,var(--red,#8E0005),#c0392b);display:flex;align-items:center;justify-content:center;color:#fff;font-size:.75rem;font-weight:700;">{}</div>', initials)

    @admin.display(description='Role')
    def role_badge(self, obj):
        colours = {'donor':'#2563EB,#DBEAFE','volunteer':'#059669,#D1FAE5','partner':'#7C3AED,#EDE9FE','beneficiary':'#3BAD6E,#D1FAE5','community':'#D97706,#FEF3C7','other':'#6B7280,#F3F4F6'}
        fg, bg = colours.get(obj.role, '#6B7280,#F3F4F6').split(',')
        return format_html('<span style="background:{};color:{};padding:3px 10px;border-radius:50px;font-size:.72rem;font-weight:700;">{}</span>', bg, fg, obj.get_role_display())

    @admin.display(description='Stars')
    def stars_col(self, obj):
        filled = '<span style="color:#F59E0B;">★</span>' * obj.rating
        empty  = '<span style="color:#E5E7EB;">★</span>' * (5 - obj.rating)
        return format_html(filled + empty)

    @admin.display(description='Approved')
    def approved_col(self, obj):
        return format_html('<span style="color:#059669;font-weight:600;">✔ Live</span>') if obj.is_approved else format_html('<span style="color:#DC2626;font-weight:600;">✖ Pending</span>')

    @admin.display(description='Featured')
    def featured_col(self, obj):
        return format_html('<span style="color:#D97706;font-weight:700;">⭐</span>') if obj.is_featured else format_html('<span style="color:#D1D5DB;">—</span>')

    @admin.display(description='Photo')
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-width:200px;border-radius:12px;"/>', obj.photo.url)
        return 'No photo uploaded'

    @admin.action(description='✔ Approve & publish selected')
    def approve(self, req, qs):
        n = qs.update(is_approved=True)
        self.message_user(req, f'{n} testimonials approved and now live.', messages.SUCCESS)

    @admin.action(description='✖ Unapprove (hide from website)')
    def unapprove(self, req, qs):
        n = qs.update(is_approved=False)
        self.message_user(req, f'{n} testimonials hidden.', messages.WARNING)

    @admin.action(description='⭐ Mark as Featured')
    def make_featured(self, req, qs):
        n = qs.update(is_featured=True)
        self.message_user(req, f'{n} testimonials marked as featured.', messages.SUCCESS)

    @admin.action(description='Remove from Featured')
    def remove_featured(self, req, qs):
        n = qs.update(is_featured=False)
        self.message_user(req, f'{n} testimonials removed from featured.', messages.WARNING)

    @admin.action(description='⬇ Export to CSV')
    def export_csv_action(self, req, qs):
        return export_csv(qs, 'testimonials.csv', ['name','role','organisation','rating','is_approved','is_featured','created_at'])


# ═══════════════════════════════════════════════════════════════════
#  NEWS POST
# ═══════════════════════════════════════════════════════════════════

@admin.register(NewsPost, site=cosma_admin)
class NewsPostAdmin(admin.ModelAdmin):
    list_display       = ('cover_thumb', 'title', 'category_badge', 'author',
                          'read_time_col', 'published_col', 'featured_col', 'published_at')
    list_filter        = ('is_published', 'is_featured', 'category', 'published_at')
    search_fields      = ('title', 'summary', 'body', 'author')
    list_per_page      = 20
    ordering           = ('-published_at', '-created_at')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields    = ('created_at', 'updated_at', 'cover_preview', 'read_time_ro', 'slug_note')
    list_display_links = ('cover_thumb', 'title')
    date_hierarchy     = 'published_at'
    actions            = ['publish', 'unpublish', 'make_featured', 'remove_featured', 'export_csv_action']

    fieldsets = (
        ('📰 Article Content', {
            'description': 'Write the article here. The body supports HTML for bold, links, lists etc.',
            'fields': ('title', 'slug', 'slug_note', 'category', 'author', 'summary', 'body'),
        }),
        ('🖼 Cover Image', {
            'fields': ('cover_image', 'cover_preview'),
            'description': 'Recommended size: 1200×630px. If left blank a placeholder is used.',
        }),
        ('📅 Publishing', {
            'description': '"Published" makes the article live. Set published_at to backdate if needed.',
            'fields': ('is_published', 'is_featured', 'published_at'),
        }),
        ('🕒 Audit', {'fields': ('created_at', 'updated_at', 'read_time_ro'), 'classes': ('collapse',)}),
    )

    @admin.display(description='')
    def cover_thumb(self, obj):
        url = obj.cover_image.url if obj.cover_image else obj.cover_url
        return format_html('<img src="{}" style="width:56px;height:40px;border-radius:6px;object-fit:cover;"/>', url)

    @admin.display(description='Category')
    def category_badge(self, obj):
        palette = {
            'programmes':    ('#3BAD6E','#D1FAE5'), 'community': ('#D97706','#FEF3C7'),
            'events':        ('#2563EB','#DBEAFE'), 'agriculture':('#059669','#D1FAE5'),
            'education':     ('#7C3AED','#EDE9FE'), 'health':    ('#DC2626','#FEE2E2'),
            'water':         ('#0891B2','#CFFAFE'), 'partnerships':('#6B7280','#F3F4F6'),
            'announcements': ('#8E0005','#FEE2E2'),
        }
        fg, bg = palette.get(obj.category, ('#6B7280','#F3F4F6'))
        return format_html('<span style="background:{};color:{};padding:3px 9px;border-radius:50px;font-size:.71rem;font-weight:700;">{}</span>', bg, fg, obj.get_category_display())

    @admin.display(description='Read time')
    def read_time_col(self, obj):
        return obj.read_time

    @admin.display(description='Status')
    def published_col(self, obj):
        return format_html('<span style="color:#059669;font-weight:600;">✔ Live</span>') if obj.is_published else format_html('<span style="color:#DC2626;font-weight:600;">✖ Draft</span>')

    @admin.display(description='Featured')
    def featured_col(self, obj):
        return format_html('<span style="color:#D97706;font-weight:700;">⭐ Yes</span>') if obj.is_featured else format_html('<span style="color:#D1D5DB;">—</span>')

    @admin.display(description='Cover preview')
    def cover_preview(self, obj):
        url = obj.cover_image.url if obj.cover_image else (obj.cover_url if obj.pk else None)
        if url:
            return format_html('<img src="{}" style="max-width:320px;border-radius:10px;"/>', url)
        return 'No cover yet'

    @admin.display(description='Estimated read time')
    def read_time_ro(self, obj):
        return obj.read_time if obj.pk else '—'

    @admin.display(description='')
    def slug_note(self, obj):
        return format_html('<span style="color:#6B7280;font-size:.82rem;">Auto-generated from title on first save. Edit carefully — changing breaks existing links.</span>')

    @admin.action(description='✔ Publish selected articles')
    def publish(self, req, qs):
        from django.utils import timezone
        for post in qs:
            if not post.published_at:
                post.published_at = timezone.now()
            post.is_published = True
            post.save()
        self.message_user(req, f'{qs.count()} articles published.', messages.SUCCESS)

    @admin.action(description='✖ Unpublish (set to draft)')
    def unpublish(self, req, qs):
        n = qs.update(is_published=False)
        self.message_user(req, f'{n} articles set to draft.', messages.WARNING)

    @admin.action(description='⭐ Mark as Featured')
    def make_featured(self, req, qs):
        NewsPost.objects.update(is_featured=False)
        n = qs.update(is_featured=True)
        self.message_user(req, f'{n} articles featured (others unset).', messages.SUCCESS)

    @admin.action(description='Remove from Featured')
    def remove_featured(self, req, qs):
        n = qs.update(is_featured=False)
        self.message_user(req, f'{n} articles removed from featured.', messages.WARNING)

    @admin.action(description='⬇ Export to CSV')
    def export_csv_action(self, req, qs):
        return export_csv(qs, 'news.csv', ['title','category','author','is_published','is_featured','published_at'])


class CoreValuesInline(admin.TabularInline):
    model = CoreValue
    extra = 1
    fields = ('icon','title','description','order')
    ordering = ('order',)

@admin.register(MissionVisionPurpose, site=cosma_admin)
class MissionVisionPurposeAdmin(admin.ModelAdmin):
    fieldsets=(
        ("Organisation Directions",{
        'fields':('mission','vision','purpose')
        }),
        ('System Info',{
        'fields':('updated_at',)
        }),
    )

    readonly_fields=('updated_at',)
    inlines=[CoreValuesInline]
    
    def has_add_permission(self, request):
        return not MissionVisionPurpose.objects.exists() or super().has_add_permission(request)