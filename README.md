# HopeForward — Django Landing Page

## Quick Start

```bash
# 1. Create & activate virtual environment
python -m venv venv
source vmyenbe
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migratedjang

# 4. Create admin user
python manage.py createsuperuser

# 5. Start development server
python manage.py runserver
```

Visit **http://127.0.0.1:8000** for the landing page.  
Visit **http://127.0.0.1:8000/admin** to manage content.

---

## Project Structure

```
hopeforward/
├── manage.py
├── requirements.txt
├── hopeforward/          ← Django project package
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── home/                 ← Main app
    ├── models.py         ← ImpactStory, Program, Partner, DonationLead, ContactMessage
    ├── views.py          ← index, donate (POST), contact (POST)
    ├── urls.py
    ├── admin.py
    └── templates/
        └── home/
            └── index.html   ← Full Bootstrap 5 landing page
```

## Admin — Add Content
- **Impact Stories** → `/admin/home/impactstory/`
- **Programmes** → `/admin/home/program/`
- **Partners** → `/admin/home/partner/`
- **Donation Leads** → `/admin/home/donationlead/`
- **Contact Messages** → `/admin/home/contactmessage/`

> When the DB is empty the site displays built-in fallback data so it looks great immediately.

## Production Checklist
1. Set `DEBUG = False` and `SECRET_KEY` via environment variables.
2. Add `whitenoise` middleware for static files.
3. Run `python manage.py collectstatic`.
4. Integrate a payment gateway (Flutterwave / Pesapal) in `views.py → donate`.
5. Configure `EMAIL_BACKEND` in `settings.py` for real email sending.
