# Asset Tracker (Django MVP)

A personal inventory tracker where users can:
- create an account and sign in
- add items they own
- categorize items
- track purchase price and estimated current value
- view potential gain/loss
- switch display currency (USD, GBP, EUR, CAD, AUD)
- manage profile info and avatar photo

## Tech stack

- Django 5
- SQLite (default)
- Tailwind CSS via CDN in templates

## Local setup

1. Install dependencies:
	 - `pip install -r requirements.txt`
2. Run migrations:
	 - `python manage.py migrate`
3. Start server:
	 - `python manage.py runserver`
4. Open:
	 - http://127.0.0.1:8000/

## Current features (MVP)

- Authentication: register, login, logout, password reset
- Dashboard (`/home/`):
	- total purchase value
	- total estimated value
	- total gain/loss
	- item list with edit/delete
- Categories:
	- create category
- Items:
	- create/edit/delete
	- fields: name, category, condition, purchase price, estimated value, purchase date, description, photo
- Currency conversion:
	- per-user selected display currency
	- converted totals and item-level values shown on the dashboard
- Profile:
	- upload profile photo
	- update display name, bio, and basic user info

## Key routes

- `/login/` – sign in
- `/register/` – create account
- `/logout/` – sign out
- `/home/` – dashboard (authenticated)
- `/profile/` – profile settings
- `/categories/new/` – create category
- `/items/new/` – add item
- `/items/<id>/edit/` – edit item
- `/items/<id>/delete/` – delete item
- `/currency/update/` – update display currency (POST)
- `/password-reset/` – request reset
- `/password-reset/done/` – reset request confirmation
- `/reset/<uidb64>/<token>/` – set new password
- `/reset/done/` – reset complete

## Development notes

- Password reset emails are printed to the console (`EMAIL_BACKEND = console`), so use the reset link shown in terminal output.
- Uploaded images are served from `/media/` in `DEBUG=True`.
- Exchange rates are currently static in code (for MVP) and can be replaced with a live API later.