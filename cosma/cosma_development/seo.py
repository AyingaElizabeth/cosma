"""
./cosma_development/seo.py
Per-page SEO configuration — title, description, keywords, OG image.
Import get_seo() in any view and pass it to the template context.
"""

SITE_NAME    = "cosma development Uganda"
SITE_URL     = "https://www.cosma development.ug"          # ← change to your real domain
SITE_TWITTER = "@cosma developmentUG"
DEFAULT_OG_IMAGE = "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1200&q=80"

# ── Per-page SEO data ────────────────────────────────────────────────────────
SEO_DATA = {

    # ── Home ────────────────────────────────────────────────────────────────
    "index": {
        "title": "cosma development Uganda | Empowering Communities Through Education, Health & Agriculture",
        "description": "cosma development is a Uganda-based NGO transforming lives in 12 districts through education scholarships, community health, agriculture training, child sponsorship, and clean water programmes since 2006.",
        "keywords": "Uganda NGO, community development Uganda, child sponsorship Uganda, education Africa, agriculture support Uganda, donate Uganda charity, cosma development, Kampala NGO",
        "og_image": DEFAULT_OG_IMAGE,
        "og_type": "website",
    },

    # ── About ────────────────────────────────────────────────────────────────
    "about_us": {
        "title": "About Us | cosma development Uganda – 18 Years of Community Impact",
        "description": "Learn about cosma development Uganda – our story, values, and commitment to building resilient communities across 12 Ugandan districts since 2006.",
        "keywords": "about cosma development, Uganda NGO history, community development organisation Uganda, transparent charity Uganda",
        "og_image": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1200&q=80",
        "og_type": "article",
    },
    "mission_vision": {
        "title": "Mission & Vision | cosma development Uganda",
        "description": "cosma development's mission is to empower Ugandan communities to break the poverty cycle through education, health, livelihoods, and clean water. Our vision: a Uganda of equal opportunity for all.",
        "keywords": "cosma development mission, NGO vision Uganda, sustainable development Uganda, poverty alleviation Uganda",
        "og_image": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1200&q=80",
        "og_type": "article",
    },
    "core_values": {
        "title": "Core Values & Goals | cosma development Uganda",
        "description": "Discover the six core values driving cosma development Uganda – community ownership, integrity, innovation, compassion, sustainability, and Ubuntu.",
        "keywords": "NGO core values, cosma development values, transparent NGO Uganda, accountable charity Uganda",
        "og_image": "https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=1200&q=80",
        "og_type": "article",
    },
    "our_team": {
        "title": "Our Team | cosma development Uganda Leadership",
        "description": "Meet the passionate Ugandan leaders, development experts, and field staff behind cosma development's 18 years of community transformation.",
        "keywords": "cosma development team, Uganda NGO staff, development professionals Uganda",
        "og_image": "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=1200&q=80",
        "og_type": "profile",
    },
    "our_partners": {
        "title": "Our Partners | cosma development Uganda – UNICEF, USAID, WHO & More",
        "description": "cosma development Uganda partners with UNICEF, USAID, WHO, UN Women, GIZ, and the World Bank to deliver sustainable development programmes across Uganda.",
        "keywords": "cosma development partners, UNICEF Uganda, USAID Uganda, NGO partnerships Uganda",
        "og_image": "https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=1200&q=80",
        "og_type": "article",
    },

    # ── Programs ─────────────────────────────────────────────────────────────
    "agri_why": {
        "title": "Why Agriculture? | cosma development Uganda Farming Programme",
        "description": "Over 70% of Ugandans depend on agriculture. cosma development equips smallholder farmers with modern techniques, quality seeds, and market access to end food insecurity.",
        "keywords": "Uganda agriculture programme, smallholder farmers Uganda, food security Uganda, farming NGO Uganda, agricultural development East Africa",
        "og_image": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80",
        "og_type": "article",
    },
    "agri_approach": {
        "title": "Our Agricultural Approach | cosma development Uganda Farmer Field Schools",
        "description": "cosma development uses Farmer Field Schools, quality input support, and direct market linkages to help 3,200+ Ugandan smallholder farmers increase yields by 180%.",
        "keywords": "farmer field school Uganda, agricultural training Uganda, smallholder farming approach Uganda",
        "og_image": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80",
        "og_type": "article",
    },
    "agri_support": {
        "title": "Support a Farmer | cosma development Uganda – Donate to Agriculture",
        "description": "UGX 100,000/month supports one Ugandan farming family with seeds, tools, and coaching. Your donation tracks real impact with quarterly reports.",
        "keywords": "support farmer Uganda, donate agriculture Uganda, sponsor farmer Africa, farm donation Uganda",
        "og_image": "https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=1200&q=80",
        "og_type": "article",
    },
    "agri_impact": {
        "title": "Agriculture Impact Stories | cosma development Uganda",
        "description": "Real stories of Ugandan farmers who tripled yields, sent children to school, and built sustainable businesses through cosma development's agriculture programme.",
        "keywords": "Uganda farmer success stories, agriculture impact Africa, smallholder farming results Uganda",
        "og_image": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80",
        "og_type": "article",
    },
    "sponsor_why": {
        "title": "Why Sponsorship? | cosma development Uganda Child Sponsorship",
        "description": "1.3 million Ugandan children are out of school. Child sponsorship is one of the most proven ways to break intergenerational poverty. Learn why it works.",
        "keywords": "child sponsorship Uganda, why sponsor a child Africa, education sponsorship Uganda, out of school children Uganda",
        "og_image": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1200&q=80",
        "og_type": "article",
    },
    "sponsor_child": {
        "title": "Sponsor a Child | cosma development Uganda – UGX 150,000/month",
        "description": "For UGX 150,000 per month you can sponsor a Ugandan child's full school year. Exchange letters, receive photos, and see your child graduate.",
        "keywords": "sponsor a child Uganda, child sponsorship Africa, donate education Uganda, school fees Uganda, cosma development sponsor",
        "og_image": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=1200&q=80",
        "og_type": "article",
    },
    "vocational": {
        "title": "Vocational & Life Skills Training | cosma development Uganda",
        "description": "cosma development provides UBTEB-certified vocational training in carpentry, tailoring, digital skills, and entrepreneurship. 78% of graduates employed within 6 months.",
        "keywords": "vocational training Uganda, UBTEB skills Uganda, youth empowerment Uganda, life skills training Africa",
        "og_image": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1200&q=80",
        "og_type": "article",
    },

    # ── Impact ───────────────────────────────────────────────────────────────
    "impact_numbers": {
        "title": "Impact in Numbers | cosma development Uganda – 125,000+ Lives Changed",
        "description": "125,000+ lives impacted, 12 districts reached, 98% fund efficiency. See cosma development Uganda's full programme impact data across education, health, agriculture, and water.",
        "keywords": "cosma development impact, Uganda NGO results, charity transparency Uganda, development results Uganda",
        "og_image": "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=1200&q=80",
        "og_type": "article",
    },
    "impact_stories": {
        "title": "Impact Stories | cosma development Uganda – Real Lives Changed",
        "description": "Read real stories of Ugandans whose lives were transformed through cosma development's education, agriculture, sponsorship, and health programmes.",
        "keywords": "Uganda impact stories, charity success stories Africa, NGO transformation stories Uganda",
        "og_image": "https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=1200&q=80",
        "og_type": "article",
    },

    # ── Contact ──────────────────────────────────────────────────────────────
    "contact": {
        "title": "Contact Us | cosma development Uganda – Kampala Office",
        "description": "Get in touch with cosma development Uganda. Contact our Kampala office to partner, volunteer, donate, or learn more about our community programmes.",
        "keywords": "contact cosma development, Uganda NGO contact, Kampala charity office, partner with NGO Uganda",
        "og_image": DEFAULT_OG_IMAGE,
        "og_type": "website",
    },
}


def get_seo(url_name: str, overrides: dict = None) -> dict:
    """
    Return SEO context dict for a given URL name.
    Pass overrides={} to replace any field dynamically.
    """
    data = SEO_DATA.get(url_name, {}).copy()
    defaults = {
        "title":       f"{SITE_NAME} | Empowering Communities in Uganda",
        "description": "cosma development Uganda delivers education, health, agriculture, and clean water programmes across 12 districts.",
        "keywords":    "Uganda NGO, charity Uganda, community development Africa",
        "og_image":    DEFAULT_OG_IMAGE,
        "og_type":     "website",
        "site_name":   SITE_NAME,
        "site_url":    SITE_URL,
        "twitter":     SITE_TWITTER,
    }
    defaults.update(data)
    if overrides:
        defaults.update(overrides)
    # Ensure site_name and site_url always present
    defaults["site_name"] = SITE_NAME
    defaults["site_url"]  = SITE_URL
    defaults["twitter"]   = SITE_TWITTER
    return {"seo": defaults}
