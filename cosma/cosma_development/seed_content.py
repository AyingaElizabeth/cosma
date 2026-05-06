"""
Management command: seed_content
Place at: cosma/cosma_development/management/commands/seed_content.py

Run with: python manage.py seed_content

Seeds sensible default data for every admin-controlled model so the site
looks complete immediately after migration. Safe to run multiple times
(uses get_or_create / update_or_create where possible).
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed initial admin-configurable content for all models'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding content...\n')
        self._site_settings()
        self._hero_sections()
        self._home_slides()
        self._home_stats()
        self._impact_items()
        self._mission_vision()
        self._timeline()
        self._org_goals()
        self._hero_stats()
        self._vocational_courses()
        self._agri_steps()
        self._sponsor_steps()
        self._partnership_types()
        self._volunteer_roles()
        self._impact_big_stats()
        self._impact_programme_stats()
        self.stdout.write(self.style.SUCCESS('\n✅ All content seeded successfully!\n'))

    # ── Site Settings ──────────────────────────────────────────────────────

    def _site_settings(self):
        from cosma_development.models import SiteSettings
        obj, created = SiteSettings.objects.get_or_create(pk=1, defaults={
            'office_address': 'Plot 45, Kampala Road, Kampala, Uganda',
            'phone':          '+256 700 123 456',
            'email':          'info@cosmadevelopments.org',
            'office_hours':   'Mon–Fri: 8am – 5pm | Sat: 9am – 1pm',
            'footer_tagline': 'Building resilient communities across Uganda through education, health, livelihoods, and clean water since 2006.',
            'globalgiving_url': 'https://www.globalgiving.org/donate/11831/cosma-sustainable-rural-development/',
        })
        self.stdout.write(f'  SiteSettings {"created" if created else "already exists"}')

    # ── Hero Sections ──────────────────────────────────────────────────────

    def _hero_sections(self):
        from cosma_development.models import HeroSection
        pages = [
            ('home',            'bi-globe-africa', 'Serving Uganda Since 2006',
             'Building Brighter Futures Together',
             'We partner with communities across Uganda to deliver education, healthcare, livelihoods, and clean water.',
             'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1800&q=80'),
            ('about',           'bi-building-heart', 'Who We Are',
             'About cosma development',
             'A community-driven force for sustainable change across Uganda since 2006.',
             'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1800&q=80'),
            ('our_story',       'bi-map', 'Our Journey',
             'Our Story',
             'From a single after-school programme in 2006 to a national force serving over 125,000 lives.',
             'https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=1800&q=80'),
            ('team_partners',   'bi-people-fill', 'Who Stands With Us',
             'Team & Partners',
             'The passionate people who drive our work daily, and the trusted organisations that walk alongside us.',
             'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=1800&q=80'),
            ('resources',       'bi-folder2-open', 'Publications',
             'Resources',
             'Annual reports, research publications, policy briefs, and programme materials.',
             'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1800&q=80'),
            ('agri_why',        'bi-flower1', 'Agriculture Program',
             'Why Agriculture?',
             'Over 70% of Ugandans depend on agriculture. It is the engine of food security and community resilience.',
             'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1800&q=80'),
            ('agri_approach',   'bi-diagram-3', 'Agriculture Program',
             'Our Approach',
             'Evidence-based, farmer-led, and climate-smart — how we deliver lasting agricultural transformation.',
             'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=1800&q=80'),
            ('agri_support',    'bi-person-heart', 'Get Involved',
             'Support a Farmer',
             'Your contribution directly funds inputs, training, and market access for a smallholder farmer.',
             'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=1800&q=80'),
            ('sponsor_why',     'bi-mortarboard', 'Sponsorship Program',
             'Why Sponsorship?',
             'Education is the most powerful tool we can give a child to change their world.',
             'https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=1800&q=80'),
            ('sponsor_child',   'bi-person-plus', 'Take Action',
             'Sponsor a Child',
             'For as little as UGX 150,000 per month you can keep a child in school and change their trajectory forever.',
             'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1800&q=80'),
            ('vocational',      'bi-tools', 'Skills Program',
             'Vocational & Life Skills Training',
             'Equipping youth and women with market-relevant skills to build independent, sustainable livelihoods.',
             'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=1800&q=80'),
            ('impact_numbers',  'bi-graph-up-arrow', 'Our Impact',
             'Impact in Numbers',
             'Measurable, verified, and growing — the data behind our community transformation.',
             'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1800&q=80'),
            ('impact_stories',  'bi-chat-quote', 'Real People, Real Change',
             'Impact Stories',
             'Behind every statistic is a person. These are their stories.',
             'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1800&q=80'),
            ('gallery',         'bi-images', 'Visual Impact',
             'Our Gallery',
             'A window into the communities, programmes, and lives we are privileged to serve across Uganda.',
             'https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=1800&q=80'),
            ('partner_with_us', 'bi-handshake', 'Get Involved',
             'Partner With Us',
             'Together we go further. Join us as a corporate, institutional, or community partner.',
             'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=1800&q=80'),
            ('volunteer',       'bi-person-heart', 'Get Involved',
             'Volunteer With Us',
             'Make a meaningful, hands-on impact by volunteering with our programmes.',
             'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1800&q=80'),
            ('share_story',     'bi-share', 'Get Involved',
             'Share Our Story',
             'Awareness changes lives. Every share connects us with potential donors, volunteers, and partners.',
             'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1800&q=80'),
            ('signup_updates',  'bi-bell', 'Stay Connected',
             'Stay Updated',
             'Be the first to hear our impact stories, programme updates, and opportunities to get involved.',
             'https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=1800&q=80'),
            ('news',            'bi-newspaper', 'Latest from cosma',
             'News & Updates',
             'Stories from the field, programme milestones, partnerships, and everything happening across our communities.',
             'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=1800&q=80'),
            ('contact',         'bi-envelope', 'Reach Out',
             'Contact Us',
             "We'd love to hear from you — whether you want to partner, volunteer, or learn more.",
             'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1800&q=80'),
            ('donate',          'bi-heart-fill', 'Make a Difference',
             'Your Gift Transforms Real Lives',
             'cosma development Uganda is on GlobalGiving. Your donation is secure and 98% goes directly to programmes.',
             'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1800&q=80'),
            ('faqs',            'bi-patch-question', 'Help Centre',
             'Frequently Asked Questions',
             'Answers grouped by programme and topic — from agriculture and sponsorship to donations and volunteering.',
             'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=1800&q=80'),
            ('agri_faqs',       'bi-patch-question', 'Agriculture Programme',
             'Agriculture FAQs',
             'Common questions about how the programme works, who it serves, and how impact is tracked.',
             'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1800&q=80'),
            ('sponsorship_faqs','bi-patch-question', 'Child Sponsorship',
             'Sponsorship FAQs',
             'Everything you need to know about sponsoring a child through cosma development.',
             'https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=1800&q=80'),
        ]
        for page, tag_icon, tag_text, heading, subheading, image_url in pages:
            obj, created = HeroSection.objects.update_or_create(
                page=page,
                defaults={'tag_icon': tag_icon, 'tag_text': tag_text,
                          'heading': heading, 'subheading': subheading,
                          'image_url': image_url, 'overlay_opacity': 0.55, 'is_active': True}
            )
            self.stdout.write(f'  Hero/{page} {"created" if created else "updated"}')

    # ── Home Slides ────────────────────────────────────────────────────────

    def _home_slides(self):
        from cosma_development.models import HomeSlide
        slides = [
            ('Children supported through cosma development programmes', 'https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=1800&q=80', 0),
            ('Farmers building practical skills for stronger harvests',  'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1800&q=80', 1),
            ('Communities gathering for programme outreach',             'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1800&q=80', 2),
            ('Young people taking part in skills development',           'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=1800&q=80', 3),
        ]
        for caption, url, order in slides:
            HomeSlide.objects.update_or_create(
                order=order,
                defaults={'caption': caption, 'image_url': url, 'is_active': True})
        self.stdout.write(f'  HomeSlides seeded ({len(slides)})')

    # ── Home Stats ─────────────────────────────────────────────────────────

    def _home_stats(self):
        from cosma_development.models import HomeStat
        stats = [
            ('125,000+', 125000, '+', 'Lives Impacted',    0),
            ('2,400+',   2400,   '+', 'Students in School',1),
            ('4,200+',   4200,   '+', 'Farmers Supported', 2),
            ('98%',      98,     '%', 'Fund Efficiency',   3),
        ]
        for value, raw, suffix, label, order in stats:
            HomeStat.objects.update_or_create(
                order=order,
                defaults={'value': value, 'raw': raw, 'suffix': suffix, 'label': label})
        self.stdout.write(f'  HomeStats seeded ({len(stats)})')

    # ── Impact Items ───────────────────────────────────────────────────────

    def _impact_items(self):
        from cosma_development.models import ImpactItem
        items = [
            ('👧', '2,400+', 'children kept in school each year',        0),
            ('🌾', '4,200+', 'farmers with better harvests and income',   1),
            ('💧', '40+',    'clean water sites across 8 districts',      2),
            ('🏥', '15,000+','health consultations delivered annually',   3),
        ]
        for emoji, figure, desc, order in items:
            ImpactItem.objects.update_or_create(
                order=order,
                defaults={'emoji': emoji, 'figure': figure, 'desc': desc})
        self.stdout.write(f'  ImpactItems seeded ({len(items)})')

    # ── Mission Vision Purpose ─────────────────────────────────────────────

    def _mission_vision(self):
        from cosma_development.models import MissionVisionPurpose, CoreValue
        mvp, created = MissionVisionPurpose.objects.get_or_create(pk=1, defaults={
            'mission': 'To increase household incomes by providing sustainable agricultural solutions and education programs through the village Cooperatives model.',
            'vision':  'Prosperous and self-reliant rural communities in Uganda.',
            'purpose': 'We exist to build bridges between communities and the resources they need to thrive — removing barriers to education, income, health, and dignity.',
            'goal':    'To empower rural communities in Uganda by providing educational sponsorships and equipping farmers with the skills and resources to sustainably produce and profit from agriculture, fostering long-term community resilience and self-sufficiency.',
        })
        if created:
            values = [
                ('bi-shield-check', 'Accountability',  'Transparency and integrity guide everything we do. We hold ourselves responsible to beneficiaries, partners, and stakeholders.',     0),
                ('bi-people-fill',  'Empowerment',     'We believe in communities\' power to shape their own destinies. Through education and resources, we build confidence and self-determination.', 1),
                ('bi-recycle',      'Sustainability',  'We create long-term impact through programmes designed for self-sufficiency and environmental stewardship.',                          2),
                ('bi-heart-fill',   'Compassion',      'Every decision is guided by deep respect for the dignity and potential of every person we serve.',                                   3),
                ('bi-diagram-3',    'Partnership',     'We believe no organisation succeeds alone. Collaboration with communities, governments, and donors multiplies our impact.',         4),
                ('bi-graph-up',     'Innovation',      'We continuously learn, adapt, and adopt evidence-based approaches to solve the root causes of poverty.',                            5),
            ]
            for icon, title, desc, order in values:
                CoreValue.objects.create(mission_vision=mvp, icon=icon, title=title, description=desc, order=order)
        self.stdout.write(f'  MissionVisionPurpose {"created" if created else "already exists"}')

    # ── Timeline ───────────────────────────────────────────────────────────

    def _timeline(self):
        from cosma_development.models import TimelineEvent
        events = [
            ('2006','bi-house-heart',   'The Beginning',             'cosma development was founded by Ugandan educators in Kampala. The first after-school programme launched in a single classroom, serving 42 children.',                                         '42 children in Year 1',      'https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=600&q=80', 0),
            ('2008','bi-heart-pulse',   'Community Health Begins',   'Responding to high maternal mortality, we launched mobile health clinics across two districts. Over 800 health consultations were delivered in the first year.',                               '800+ health visits',         None, 1),
            ('2010','bi-flower1',       'Agriculture Programme',     'We launched our first cooperative model — connecting 120 smallholder farmers with inputs, training, and market access.',                                                                        '120 farmers in first cohort','https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600&q=80', 2),
            ('2012','bi-droplet-half',  'Clean Water Initiative',    'Partnering with UNICEF, we drilled our first 10 boreholes in Luwero district, bringing safe water to over 4,000 people.',                                                                      '4,000+ gained clean water',  None, 3),
            ('2014','bi-award',         'National Recognition',      'cosma development received the Uganda NGO Excellence Award. Our model was adopted as a best-practice case study by the Ministry of Agriculture.',                                              'Best-practice designation',  None, 4),
            ('2016','bi-briefcase',     'Vocational Centres Open',   'Two vocational training centres opened in Kampala and Jinja, offering tailoring, carpentry, solar, and catering to youth aged 16–35.',                                                         '600+ graduates in 2 years',  'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=600&q=80', 5),
            ('2018','bi-globe-africa',  'Expanding to 12 Districts', 'With USAID and GIZ support, we expanded to all 12 target districts. The 100,000th beneficiary was served.',                                                                                   '100,000th beneficiary reached',None, 6),
            ('2021','bi-shield-check',  'COVID-19 Response',         'When the pandemic struck, cosma development distributed food to 8,000 households and kept 1,200 children in remote schooling.',                                                                '8,000 households supported', None, 7),
            ('2023','bi-graph-up-arrow','125,000 Lives Impacted',    'Our annual impact count crossed 125,000 — 17 years of consistent, community-led work. The cooperative model now includes 4,200+ farmers.',                                                      '125,000+ lives annually',    'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=600&q=80', 8),
            ('Today','bi-stars',        'Looking Forward',           'With a plan to reach 250,000 beneficiaries by 2030, cosma development builds on 18 years of trust and partnership — one community at a time.',                                                  'Target: 250,000 by 2030',    None, 9),
        ]
        for year, icon, title, desc, stat, img_url, order in events:
            TimelineEvent.objects.update_or_create(
                order=order,
                defaults={'year': year, 'icon': icon, 'title': title, 'desc': desc,
                          'stat': stat, 'image_url': img_url or '', 'order': order})
        self.stdout.write(f'  TimelineEvents seeded ({len(events)})')

    # ── Org Goals ──────────────────────────────────────────────────────────

    def _org_goals(self):
        from cosma_development.models import OrgGoal
        goals = [
            ('Reach 250,000 Beneficiaries by 2030', 'Double reach through expanded programming in all 12 districts.',          50, 0),
            ('100% School Retention',               'Every sponsored child completes their cycle without interruption.',         72, 1),
            ('1,000 New Farmer Cooperatives',        'Cooperatives operational and profitable in all 12 districts.',             38, 2),
            ('Clean Water for 100 Communities',      'Boreholes and rainwater harvesting systems in every target village.',      42, 3),
        ]
        for title, desc, progress, order in goals:
            OrgGoal.objects.update_or_create(order=order, defaults={'title': title, 'desc': desc, 'progress': progress})
        self.stdout.write(f'  OrgGoals seeded ({len(goals)})')

    # ── Hero Stats ─────────────────────────────────────────────────────────

    def _hero_stats(self):
        from cosma_development.models import HeroStat
        stats = [
            ('Years of service',  18,     '+', 0),
            ('Lives impacted',    125000, '+', 1),
            ('Districts reached', 12,     '',  2),
            ('Fund efficiency',   98,     '%', 3),
        ]
        for label, raw, suffix, order in stats:
            HeroStat.objects.update_or_create(order=order, defaults={'label': label, 'raw': raw, 'suffix': suffix})
        self.stdout.write(f'  HeroStats seeded ({len(stats)})')

    # ── Vocational Courses ─────────────────────────────────────────────────

    def _vocational_courses(self):
        from cosma_development.models import VocationalCourse
        courses = [
            ('Tailoring & Fashion Design', 'Garment construction, pattern making, and small business skills.',    'bi-scissors',       '3 Months', 0),
            ('Carpentry & Joinery',        'Practical wood-working for furniture and construction projects.',     'bi-tools',          '4 Months', 1),
            ('Catering & Hospitality',     'Professional cooking, food safety, and hospitality management.',     'bi-cup-hot',        '3 Months', 2),
            ('Solar & Electrical',         'Installation and maintenance of solar systems and wiring.',          'bi-lightning-fill', '4 Months', 3),
            ('Hair & Beauty',              'Hairdressing, salon management, and cosmetology fundamentals.',      'bi-stars',          '3 Months', 4),
            ('Financial Literacy',         'Budgeting, saving, recordkeeping, and small business management.',   'bi-cash-stack',     '6 Weeks',  5),
        ]
        for title, desc, icon, duration, order in courses:
            VocationalCourse.objects.update_or_create(
                order=order,
                defaults={'title': title, 'desc': desc, 'icon': icon, 'duration': duration, 'is_active': True})
        self.stdout.write(f'  VocationalCourses seeded ({len(courses)})')

    # ── Agriculture Approach Steps ─────────────────────────────────────────

    def _agri_steps(self):
        from cosma_development.models import AgriApproachStep
        steps = [
            ('Farmer Assessment',    'Detailed assessment of each farmer\'s land, resources, and challenges.',             0),
            ('Training & Capacity',  'Hands-on training in modern techniques and climate-smart agriculture.',              1),
            ('Input Support',        'Quality seeds, fertilisers, and tools at subsidised rates.',                         2),
            ('Market Linkages',      'Connecting farmers to reliable buyers, cooperatives, and digital marketplaces.',     3),
            ('Monitoring & Follow-up','Regular field visits and data collection to track and improve outcomes.',            4),
            ('Cooperative Formation','Supporting farmers to form cooperatives for collective bargaining power.',            5),
        ]
        for title, desc, order in steps:
            AgriApproachStep.objects.update_or_create(order=order, defaults={'title': title, 'desc': desc})
        self.stdout.write(f'  AgriApproachSteps seeded ({len(steps)})')

    # ── Sponsor Steps ──────────────────────────────────────────────────────

    def _sponsor_steps(self):
        from cosma_development.models import SponsorStep
        steps = [
            ('Choose a Giving Level', 'Select a monthly or annual amount that works for you.', 0),
            ('Complete Your Details', 'Fill in contact and payment details securely.',         1),
            ('Get Matched',           'We match you with a child and send their profile.',     2),
            ('Receive Updates',       'Get regular updates, photos, and progress reports.',    3),
        ]
        for title, desc, order in steps:
            SponsorStep.objects.update_or_create(order=order, defaults={'title': title, 'desc': desc})
        self.stdout.write(f'  SponsorSteps seeded ({len(steps)})')

    # ── Partnership Types ──────────────────────────────────────────────────

    def _partnership_types(self):
        from cosma_development.models import PartnershipType
        types = [
            ('Corporate Sponsor',   'Align your brand with measurable community impact through a structured CSR package.',     'bi-building',    '#8E0005', 'rgba(142,0,5,.1)',    0),
            ('Institutional Grant', 'Fund a specific programme. We partner with foundations, bilateral donors, and UN agencies.','bi-bank',        '#3BAD6E', 'rgba(59,173,110,.1)', 1),
            ('In-Kind Support',     'Donate goods, services, or expertise — from medical supplies to professional training.',   'bi-box-seam',    '#8E0005', 'rgba(142,0,5,.1)',    2),
            ('Community Partner',   'Local organisations, churches, and schools that extend our reach in their districts.',    'bi-people-fill', '#3BAD6E', 'rgba(59,173,110,.1)', 3),
        ]
        for title, desc, icon, color, bg, order in types:
            PartnershipType.objects.update_or_create(
                order=order,
                defaults={'title': title, 'desc': desc, 'icon': icon, 'color': color, 'bg': bg})
        self.stdout.write(f'  PartnershipTypes seeded ({len(types)})')

    # ── Volunteer Roles ────────────────────────────────────────────────────

    def _volunteer_roles(self):
        from cosma_development.models import VolunteerRole
        roles = [
            ('Teaching & Tutoring',    'Support literacy and numeracy in our learning centres.',         'bi-mortarboard',  '#8E0005', 'rgba(142,0,5,.1)',    'Min. 1 month',       0),
            ('Healthcare & Medical',   'Qualified health professionals supporting mobile clinic teams.', 'bi-heart-pulse',  '#3BAD6E', 'rgba(59,173,110,.1)', 'Min. 2 weeks',       1),
            ('Agriculture',            'Agronomists sharing modern techniques with farmer cooperatives.','bi-flower1',      '#8E0005', 'rgba(142,0,5,.1)',    'Min. 1 month',       2),
            ('Communications & Media', 'Photographers, videographers, and writers telling our story.',  'bi-camera',       '#3BAD6E', 'rgba(59,173,110,.1)', 'Flexible',           3),
            ('IT & Technology',        'Developers and data analysts supporting our digital work.',      'bi-laptop',       '#8E0005', 'rgba(142,0,5,.1)',    'Flexible / Remote',  4),
            ('Fundraising & Events',   'Help organise fundraising events, campaigns, and outreach.',     'bi-megaphone',    '#3BAD6E', 'rgba(59,173,110,.1)', 'Flexible',           5),
        ]
        for title, desc, icon, color, bg, commitment, order in roles:
            VolunteerRole.objects.update_or_create(
                order=order,
                defaults={'title': title, 'desc': desc, 'icon': icon, 'color': color,
                          'bg': bg, 'commitment': commitment, 'is_active': True})
        self.stdout.write(f'  VolunteerRoles seeded ({len(roles)})')

    # ── Impact Big Stats ───────────────────────────────────────────────────

    def _impact_big_stats(self):
        from cosma_development.models import ImpactBigStat
        stats = [
            ('125,000+','Lives Impacted Annually',    'bi-people-fill',    '#8E0005', 0),
            ('2,400+',  'Students in School',         'bi-book-half',      '#3BAD6E', 1),
            ('4,200+',  'Farmers Supported',          'bi-flower1',        '#8E0005', 2),
            ('40+',     'Clean Water Sites',          'bi-droplet-half',   '#3BAD6E', 3),
            ('800+',    'Entrepreneurs Trained',      'bi-briefcase',      '#8E0005', 4),
            ('12',      'Districts Reached',          'bi-geo-alt-fill',   '#3BAD6E', 5),
            ('15,000+', 'Health Consultations',       'bi-heart-pulse',    '#8E0005', 6),
            ('98%',     'Fund Efficiency',            'bi-graph-up-arrow', '#3BAD6E', 7),
        ]
        for value, label, icon, color, order in stats:
            ImpactBigStat.objects.update_or_create(
                order=order,
                defaults={'value': value, 'label': label, 'icon': icon, 'color': color})
        self.stdout.write(f'  ImpactBigStats seeded ({len(stats)})')

    # ── Impact Programme Stats ─────────────────────────────────────────────

    def _impact_programme_stats(self):
        from cosma_development.models import ImpactProgrammeStat
        stats = [
            ('Education — Students retained',              '2,400+', 85, '#3BAD6E', 0),
            ('Agriculture — Farmers with increased yields','4,200+', 72, '#8E0005', 1),
            ('Health — Communities with clinic access',    '68%',    68, '#3BAD6E', 2),
            ('Water — Villages with clean water',          '40+',    55, '#8E0005', 3),
            ('Vocational — Graduates now self-employed',   '78%',    78, '#3BAD6E', 4),
            ('Sponsorship — Children completing P7',       '94%',    94, '#8E0005', 5),
        ]
        for label, value, pct, color, order in stats:
            ImpactProgrammeStat.objects.update_or_create(
                order=order,
                defaults={'label': label, 'value': value, 'pct': pct, 'color': color})
        self.stdout.write(f'  ImpactProgrammeStats seeded ({len(stats)})')