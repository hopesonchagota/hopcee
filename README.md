# Hopcee Bulk Ordering Service

**Buy at Ordering Price with Just Half Way Transport.**

A full-stack Django website for LUANAR Bunda Campus students to *request*
bulk goods (Irish Potato, Electrical Equipment, Soya Pieces/Thumba, Mafuta,
Bonya small fish, and more) from Mitundu Market and Town — Hopcee sources
and delivers, and the price is always confirmed with the customer directly
on WhatsApp.

**This is a browsing + order-request site, not an online shop:**
- No login or account is required to browse or order — anyone can visit and order as a guest.
- No prices, subtotals, or totals are ever shown to customers, anywhere.
- No online payment of any kind exists on the site.
- Submitting an order request opens **WhatsApp** with the order details
  pre-filled, addressed to Hopcee's own number — the customer taps Send and
  that message *is* the order request. A WhatsApp number is required from
  every customer at checkout so Hopcee can reply.

## Tech Stack

- **Backend:** Python 3.12, Django 5
- **Database:** SQLite (dev, zero setup) → PostgreSQL (production, via `DATABASE_URL`)
- **Styling:** Tailwind CSS (CDN), Times New Roman throughout, mobile-first, blue → teal theme
- **Ordering:** Guest, session-based cart — no account needed
- **Order handoff:** `wa.me` click-to-chat link (no API credentials needed for this part)
- **Status updates (optional):** WhatsApp Cloud API when configured, DB log otherwise
- **Admin:** Django Admin (staff-only login), customized for markets, categories, products,
  orders (internal prices visible here only), and a **Money-Safe Ledger**
- **Static/Deploy:** WhiteNoise, Gunicorn, Procfile — ready for Render / Railway / Heroku

## Project Structure

```
hopcee/
├── config/          # settings, root urls, wsgi/asgi
├── accounts/        # custom User model (kept only for AUTH_USER_MODEL / staff
│                     # Admin login — no customer-facing login/register routes)
├── catalog/         # Market, Category, Product models + admin
├── orders/          # Cart, Order, OrderItem, status tracking, money ledger,
│                     # WhatsApp notifications (utils.py, signals.py)
├── core/            # homepage, product listing, about, contact, testimonials
│                     # + `seed_demo_data` management command
├── templates/        # Tailwind-based templates (base, partials, per-app pages)
├── static/           # custom static assets (currently minimal — Tailwind via CDN)
├── requirements.txt
├── .env.example       # copy to .env and fill in real values
├── Procfile           # release + web process for Render/Railway/Heroku
└── runtime.txt
```

## Local Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# edit .env — at minimum set a real SECRET_KEY

# 4. Run migrations
python manage.py migrate

# 5. Create an admin account
python manage.py createsuperuser

# 6. (Optional but recommended) seed demo markets/products/testimonials
python manage.py seed_demo_data

# 7. Run the dev server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the site and `http://127.0.0.1:8000/admin/`
for the Admin Dashboard.

## How the Order Flow Works

1. **Browse** — anyone (no account needed) visits `/orders/products/`-style
   catalog pages, filters by market/category, and adds products + quantity
   to a guest, session-based **Order List** (cart). No prices are shown —
   just "Ordering price confirmed after sourcing."
2. **Order Details** — the customer enters their **name** and **WhatsApp
   number** (required), a preferred delivery date, and delivery point on
   campus. Still no prices anywhere on this screen.
3. **Submit → WhatsApp handoff** — on submit, an `Order` + `OrderItem`s are
   saved (status `Pending`) purely for tracking/admin purposes, and the
   customer lands on a confirmation page that opens **WhatsApp** with the
   order details pre-filled, addressed to Hopcee's own number
   (`HOPCEE_WHATSAPP_NUMBER`). The customer taps Send — that outgoing
   message *is* the order request Hopcee receives. See `orders/utils.py:
   order_whatsapp_message()` / `order_hopcee_link()`.
4. **Staff update status** in Django Admin (`Pending → Bought → In Transit →
   Delivered`) — each change optionally fires a WhatsApp notification back
   to the customer via `orders/signals.py` (no prices in these either).
5. **Customer tracks** their order any time at `/orders/track/` using their
   order code + phone number, seeing a visual status stepper — no account
   needed.
6. **Money-Safe Ledger** — staff log every kwacha collected from the
   customer, paid to the market vendor, and paid for transport against each
   order in the admin (staff-only), backing up the trust guarantee shown to
   customers as "your order is recorded and tracked."

## WhatsApp Integration

Two separate channels, on purpose:

- **Customer → Hopcee (the order itself):** a plain `wa.me` click-to-chat
  link, built in `orders/utils.py: order_hopcee_link()`. This needs **zero
  external setup or API credentials** — it just opens the customer's own
  WhatsApp with the message ready to send.
- **Hopcee → Customer (optional status pings):** by default (no API
  credentials), these are just logged to the `WhatsAppNotificationLog`
  model (visible read-only in the admin). To send them automatically for
  real, sign up for Meta's **WhatsApp Cloud API** and set in `.env`:

```
WHATSAPP_CLOUD_API_TOKEN=...
WHATSAPP_CLOUD_API_PHONE_ID=...
HOPCEE_WHATSAPP_NUMBER=+265988609202   # the number order requests are sent TO
```

## Switching to PostgreSQL

Local dev uses SQLite automatically. For production, just set `DATABASE_URL`
in your environment, e.g.:

```
DATABASE_URL=postgres://hopcee_user:hopcee_pass@localhost:5432/hopcee_db
```

No code changes needed — `config/settings.py` already reads this via
`dj-database-url`.

## Deploying (Render / Railway / Heroku-style)

1. Push this project to a Git repository.
2. Create a new **Web Service**, connect the repo.
3. Set environment variables: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`,
   `DATABASE_URL` (attach a managed PostgreSQL add-on), and the `HOPCEE_*` /
   `WHATSAPP_*` variables from `.env.example`.
4. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
5. Start command is already defined in `Procfile` (`gunicorn config.wsgi:application`),
   and `release: python manage.py migrate` runs migrations automatically on deploy.
6. After first deploy, run once (via the platform's shell/console):
   ```
   python manage.py createsuperuser
   python manage.py seed_demo_data   # optional
   ```

## Notes on Images

Product/market photos are stored as plain `image_url` fields (editable in
the admin). Demo data now falls back to clean, locally-hosted SVG
placeholders in `static/img/placeholders/` (no external image host, so
nothing ever breaks if a third-party URL changes or disappears). Swap in
real product/market photography any time via **Admin → Catalog** — prefer
Unsplash, Pexels or Wikimedia Commons, and record `image_source` /
`image_credit` in your own notes if you add attribution fields later.

## Contact (shown across the site)

- WhatsApp: `+265988609202`
- Normal Calls: `+265897470024`
- Location: LUANAR Bunda Campus
- Registration Number: Available on Request — Your Money is Safe
