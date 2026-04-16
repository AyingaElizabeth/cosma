"""
/admin.py  —  cosma Professional Admin Dashboard
Features:
  • Custom AdminSite with branded dashboard + KPI cards + donation chart
  • Per-model: rich list_display, search, filters, export CSV bulk actions
  • Inline image thumbnails, colour swatches, star ratings for donations
  • Read/unread badges, one-click email reply, featured toggles
  • Fieldsets with descriptions for every model
"""
import csv
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
from django.shortcuts import render, redirect

from .models import ImpactStory, Program, Partner, DonationLead, ContactMessage


# ── helpers ──────────────────────────────────────────────────────────────────

def export_csv(queryset, filename, fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(fields)
    for obj in queryset:
        writer.writerow([str(getattr(obj, f, '')) for f in fields])
    return response


# ═══════════════════════════════════════════════════════
#  CUSTOM ADMIN SITE
# ═══════════════════════════════════════════════════════

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

        unread_messages  = ContactMessage.objects.filter(is_read=False).count()
        total_messages   = ContactMessage.objects.count()
        featured_stories = ImpactStory.objects.filter(is_featured=True).count()
        total_stories    = ImpactStory.objects.count()
        active_programs  = Program.objects.count()
        total_partners   = Partner.objects.count()
        donation_count   = DonationLead.objects.count()
        total_users      = User.objects.count()

        # 6-month donation chart
        chart_labels, chart_data = [], []
        for i in range(5, -1, -1):
            d   = today - timedelta(days=30 * i)
            mo  = d.replace(day=1)
            nxt = (mo.replace(month=mo.month % 12 + 1, day=1) if mo.month < 12
                   else mo.replace(year=mo.year + 1, month=1, day=1))
            amt = DonationLead.objects.filter(
                created_at__date__gte=mo, created_at__date__lt=nxt
            ).aggregate(t=Sum('amount'))['t'] or 0
            chart_labels.append(mo.strftime('%b %Y'))
            chart_data.append(float(amt))

        # tag distribution for doughnut chart
        tags   = ImpactStory.objects.values('tag').annotate(c=Count('id')).order_by('-c')
        tag_labels = [t['tag'] for t in tags]
        tag_data   = [t['c'] for t in tags]

        ctx = dict(
            self.each_context(request),
            title='Dashboard',
            total_donations=total_donations,
            month_donations=month_donations,
            mom_pct=mom_pct,
            donation_count=donation_count,
            unread_messages=unread_messages,
            total_messages=total_messages,
            featured_stories=featured_stories,
            total_stories=total_stories,
            active_programs=active_programs,
            total_partners=total_partners,
            total_users=total_users,
            recent_donations=DonationLead.objects.order_by('-created_at')[:7],
            recent_messages=ContactMessage.objects.order_by('-created_at')[:6],
            recent_stories=ImpactStory.objects.order_by('-created_at')[:5],
            chart_labels=chart_labels,
            chart_data=chart_data,
            tag_labels=tag_labels,
            tag_data=tag_data,
        )
        return render(request, 'admin/dashboard.html', ctx)


cosma_admin = cosmaAdminSite(name='admin')


# ═══════════════════════════════════════════════════════
#  IMPACT STORY
# ═══════════════════════════════════════════════════════

@admin.register(ImpactStory, site=cosma_admin)
class ImpactStoryAdmin(admin.ModelAdmin):
    list_display       = ('thumbnail', 'name', 'location', 'tag_badge', 'featured_badge', 'created_at')
    list_filter        = ('is_featured', 'tag', 'created_at')
    search_fields      = ('name', 'location', 'story', 'tag')
    list_per_page      = 20
    date_hierarchy     = 'created_at'
    readonly_fields    = ('created_at', 'image_preview')
    list_display_links = ('thumbnail', 'name')
    ordering           = ('-created_at',)
    actions            = ['make_featured', 'remove_featured', 'export_csv_action']

    fieldsets = (
        ('👤 Person Details', {
            'fields': ('name', 'location', 'tag'),
            'description': 'Enter the full name and district/location of this person.'
        }),
        ('📝 Story Content', {'fields': ('story',)}),
        ('📷 Photo', {
            'fields': ('image', 'image_preview'),
            'description': 'Upload a clear portrait. Minimum 400×400px recommended.'
        }),
        ('⚙ Settings', {
            'fields': ('is_featured', 'created_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='')
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid #3BAD6E;"/>', obj.image.url)
        return format_html('<div style="width:40px;height:40px;border-radius:50%;background:#eee;display:flex;align-items:center;justify-content:center;">👤</div>')

    @admin.display(description='Tag')
    def tag_badge(self, obj):
        colors = {'Education':'#3BAD6E','Health':'#8E0005','Agriculture':'#E67E22','Livelihoods':'#2980B9','Clean Water':'#16A085','Empowerment':'#8E44AD'}
        c = colors.get(obj.tag, '#666')
        return format_html('<span style="background:{};color:#fff;padding:3px 10px;border-radius:50px;font-size:.75rem;font-weight:600;">{}</span>', c, obj.tag)

    @admin.display(description='Featured')
    def featured_badge(self, obj):
        if obj.is_featured:
            return format_html('<span style="color:#3BAD6E;font-weight:600;">✔ Yes</span>')
        return format_html('<span style="color:#ccc;">Hidden</span>')

    @admin.display(description='Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width:280px;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,.15);"/>', obj.image.url)
        return "No image yet"

    @admin.action(description='✔ Mark as Featured')
    def make_featured(self, request, queryset):
        n = queryset.update(is_featured=True)
        self.message_user(request, f'{n} stories marked as featured.', messages.SUCCESS)

    @admin.action(description='✖ Remove from Featured')
    def remove_featured(self, request, queryset):
        n = queryset.update(is_featured=False)
        self.message_user(request, f'{n} stories hidden.', messages.WARNING)

    @admin.action(description='⬇ Export to CSV')
    def export_csv_action(self, request, queryset):
        return export_csv(queryset, 'impact_stories.csv', ['name','location','tag','is_featured','created_at'])


# ═══════════════════════════════════════════════════════
#  PROGRAM
# ═══════════════════════════════════════════════════════

@admin.register(Program, site=cosma_admin)
class ProgramAdmin(admin.ModelAdmin):
    list_display  = ('icon_preview', 'title', 'color_swatch', 'stat_label', 'order')
    list_editable = ('order',)
    list_per_page = 20
    search_fields = ('title', 'description')
    ordering      = ('order',)

    fieldsets = (
        ('📋 Programme Details', {'fields': ('title', 'description')}),
        ('🎨 Appearance', {
            'fields': ('icon', 'color'),
            'description': 'These control how the card looks on the website.'
        }),
        ('📊 Stats & Order', {
            'fields': ('stat_label', 'order'),
            'description': 'stat_label shows on the card e.g. "2,400+ Learners". Lower order = shown first.'
        }),
    )

    @admin.display(description='Icon')
    def icon_preview(self, obj):
        return format_html('<div style="width:34px;height:34px;border-radius:8px;background:{};display:inline-flex;align-items:center;justify-content:center;color:#fff;font-size:.9rem;">{}</div>', obj.color, obj.icon.replace('bi-','').replace('-',' ')[:3].upper())

    @admin.display(description='Colour')
    def color_swatch(self, obj):
        name = dict(Program.COLOR_CHOICES).get(obj.color, obj.color)
        return format_html('<span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:16px;height:16px;border-radius:4px;background:{};border:1px solid rgba(0,0,0,.15);display:inline-block;"></span>{}</span>', obj.color, name)


# ═══════════════════════════════════════════════════════
#  PARTNER
# ═══════════════════════════════════════════════════════

@admin.register(Partner, site=cosma_admin)
class PartnerAdmin(admin.ModelAdmin):
    list_display  = ('logo_thumb', 'name', 'website_link', 'order')
    list_editable = ('order',)
    list_per_page = 20
    search_fields = ('name', 'website')
    ordering      = ('order',)

    fieldsets = (
        ('🤝 Partner Info', {'fields': ('name', 'website')}),
        ('🖼 Logo', {
            'fields': ('logo', 'logo_url'),
            'description': 'Upload a file OR paste a URL. Uploaded file takes priority.'
        }),
        ('⚙ Display', {'fields': ('order',)}),
    )

    @admin.display(description='Logo')
    def logo_thumb(self, obj):
        src = obj.logo.url if obj.logo else obj.logo_url
        if src:
            return format_html('<img src="{}" style="height:34px;max-width:90px;object-fit:contain;"/>', src)
        return format_html('<span style="color:#aaa;font-size:.8rem;">No logo</span>')

    @admin.display(description='Website')
    def website_link(self, obj):
        if obj.website:
            return format_html('<a href="{}" target="_blank" style="color:#3BAD6E;text-decoration:none;">🔗 Visit</a>', obj.website)
        return '—'


# ═══════════════════════════════════════════════════════
#  DONATION LEAD
# ═══════════════════════════════════════════════════════

@admin.register(DonationLead, site=cosma_admin)
class DonationLeadAdmin(admin.ModelAdmin):
    list_display    = ('name', 'email', 'amount_formatted', 'level_badge', 'programme', 'created_at')
    list_filter     = ('created_at',)
    search_fields   = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'amount', 'name', 'email', 'message')
    list_per_page   = 25
    date_hierarchy  = 'created_at'
    ordering        = ('-created_at',)
    actions         = ['export_csv_action']

    fieldsets = (
        ('💳 Donor', {'fields': ('name', 'email')}),
        ('💰 Donation', {'fields': ('amount', 'message', 'created_at')}),
    )

    @admin.display(description='Amount (UGX)', ordering='amount')
    def amount_formatted(self, obj):
        v = int(obj.amount)
        c = '#3BAD6E' if v >= 100000 else ('#E67E22' if v >= 50000 else '#8E0005')
        return format_html('<strong style="color:{};">UGX {:,}</strong>', c, v)

    @admin.display(description='Level')
    def level_badge(self, obj):
        v = int(obj.amount)
        if v >= 500000:   lbl,c,s = 'Champion','#8E0005','★★★★★'
        elif v >= 250000: lbl,c,s = 'Supporter','#3BAD6E','★★★★☆'
        elif v >= 100000: lbl,c,s = 'Friend','#E67E22','★★★☆☆'
        else:             lbl,c,s = 'Donor','#aaa','★★☆☆☆'
        return format_html('<span style="color:{};font-size:.85rem;" title="{}">{}</span>', c, lbl, s)

    @admin.display(description='Programme')
    def programme(self, obj):
        return obj.message or format_html('<em style="color:#bbb;">Not specified</em>')

    @admin.action(description='⬇ Export to CSV')
    def export_csv_action(self, request, queryset):
        return export_csv(queryset, 'donations.csv', ['name','email','amount','message','created_at'])


# ═══════════════════════════════════════════════════════
#  CONTACT MESSAGE
# ═══════════════════════════════════════════════════════

@admin.register(ContactMessage, site=cosma_admin)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display    = ('status_dot', 'name', 'email_link', 'subject', 'created_at', 'quick_reply')
    list_filter     = ('is_read', 'created_at')
    search_fields   = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at', 'quick_reply')
    list_per_page   = 25
    date_hierarchy  = 'created_at'
    ordering        = ('is_read', '-created_at')
    actions         = ['mark_read', 'mark_unread', 'export_csv_action']

    fieldsets = (
        ('📨 From', {'fields': ('name', 'email', 'created_at')}),
        ('💬 Message', {'fields': ('subject', 'message')}),
        ('⚙ Status', {'fields': ('is_read', 'quick_reply')}),
    )

    @admin.display(description='')
    def status_dot(self, obj):
        c = '#8E0005' if not obj.is_read else '#ddd'
        t = 'Unread' if not obj.is_read else 'Read'
        return format_html('<span style="width:10px;height:10px;border-radius:50%;background:{};display:inline-block;" title="{}"></span>', c, t)

    @admin.display(description='Email')
    def email_link(self, obj):
        return format_html('<a href="mailto:{}" style="color:#3BAD6E;text-decoration:none;">{}</a>', obj.email, obj.email)

    @admin.display(description='Reply')
    def quick_reply(self, obj):
        return format_html(
            '<a href="mailto:{}?subject=Re: {}" style="background:#3BAD6E;color:#fff;padding:5px 12px;'
            'border-radius:6px;text-decoration:none;font-size:.8rem;">✉ Reply</a>',
            obj.email, obj.subject
        )

    @admin.action(description='✔ Mark as Read')
    def mark_read(self, request, queryset):
        n = queryset.update(is_read=True)
        self.message_user(request, f'{n} messages marked as read.', messages.SUCCESS)

    @admin.action(description='✖ Mark as Unread')
    def mark_unread(self, request, queryset):
        n = queryset.update(is_read=False)
        self.message_user(request, f'{n} messages marked as unread.', messages.INFO)

    @admin.action(description='⬇ Export to CSV')
    def export_csv_action(self, request, queryset):
        return export_csv(queryset, 'messages.csv', ['name','email','subject','message','is_read','created_at'])


# ── Auth models ──────────────────────────────────────────────────────────────
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin

@admin.register(User,  site=cosma_admin)
class UserAdmin(BaseUserAdmin): pass

@admin.register(Group, site=cosma_admin)
class GroupAdmin(BaseGroupAdmin): pass
