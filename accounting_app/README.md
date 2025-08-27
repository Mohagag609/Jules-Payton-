# Modern Accounting System (Django + HTMX)

This is a full-stack accounting system built with Django, HTMX, and TailwindCSS, designed for managing contracts, installments, vouchers, and inventory for a small to medium-sized enterprise. The UI is modern, responsive, and supports RTL languages (Arabic).

## ✨ Features

- **Dashboard:** At-a-glance KPIs for total receipts, payments, net balance, and late installments.
- **Dynamic CRUD:** HTMX-powered, modal-based forms for managing all core models without page reloads.
- **Contract Management:** A multi-step wizard for creating detailed sales contracts.
- **Installment Automation:** Automatic generation of installment schedules based on contract terms.
- **Payment Tracking:** Easy payment recording for installments, with automatic status updates (Pending, Late, Paid).
- **Voucher System:** Separate modules for creating and listing receipt and payment vouchers.
- **Inventory & Projects:** Management of projects, inventory items, and stock movements (IN/OUT).
- **Reporting:** A flexible reporting engine with initial support for a detailed Treasury Report, exportable to HTML, CSV, and PDF.
- **Demo Data:** A command to seed the database with realistic sample data for immediate testing and demonstration.
- **Unit Tests:** A test suite to ensure the reliability of core financial calculations.

## 🛠️ Tech Stack

- **Backend:** Python 3.11, Django 5.x, Gunicorn
- **Frontend:** Django Templates, HTMX, TailwindCSS (via CDN)
- **Database:** SQLite (local), PostgreSQL (production)
- **PDF Generation:** WeasyPrint
- **Deployment:** Netlify, WhiteNoise

---

## 🚀 Local Development Setup

1.  **Clone the repository and navigate to the project directory.**

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser to access the admin panel and the app:**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Seed the database with demo data (Highly Recommended):**
    This command populates the database with a full set of sample data to showcase all features.
    ```bash
    python manage.py seed_demo
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000`. Log in with the superuser credentials you created.

---

## 🧪 Running Tests

To run the unit tests and ensure all core logic is working correctly:
```bash
python manage.py test accounting
```

---

## ☁️ Production Deployment (Netlify + Neon)

This project is configured for deployment on Netlify with a PostgreSQL database from Neon.

### Step 1: Set up Neon Database

1.  Go to [Neon](https://neon.tech/) and create a new project.
2.  In your project dashboard, find the **Connection Details** section.
3.  Select the **psql** connection string. It will look something like `postgres://user:password@ep-plain-moon-123456.us-east-2.aws.neon.tech/neondb?sslmode=require`. This is your `DATABASE_URL`.

### Step 2: Deploy to Netlify

1.  Push your code to a GitHub repository.
2.  Go to your Netlify dashboard and click "Add new site" -> "Import an existing project".
3.  Connect to your Git provider and select your repository.
4.  Netlify should automatically detect the `netlify.toml` and `requirements.txt` files. The build settings will be pre-filled:
    - **Build command:** `python manage.py collectstatic --noinput`
    - **Publish directory:** `staticfiles/`
5.  Before deploying, go to **Site settings** -> **Build & deploy** -> **Environment**.
6.  Add the following **environment variables**:
    - `DATABASE_URL`: The full connection string from Neon.
    - `DJANGO_SECRET_KEY`: A new, strong secret key. You can generate one using an online tool or `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`.
    - `ALLOWED_HOSTS`: The URL of your Netlify site (e.g., `your-site-name.netlify.app`).
    - `DEBUG`: `False`

7.  Trigger a deploy. Netlify will install dependencies, run the build command, and deploy your site.

### Step 3: Run Production Migrations

Your code is deployed, but the production database is empty. You need to run migrations.

1.  In the Netlify dashboard for your site, go to **Functions**.
2.  You may need to add a simple "hello world" function to your repo to enable the "Invoke function" button if it's disabled.
3.  A more robust way is to use Netlify's CLI or a build hook to run a one-off task, but a common workaround is to temporarily change your `Procfile`:
    - Change `web: gunicorn core.wsgi` to `web: python manage.py migrate && gunicorn core.wsgi`.
    - Push this change and let it deploy. It will run migrations on startup.
    - **IMPORTANT:** Change the `Procfile` back to `web: gunicorn core.wsgi` and redeploy immediately after to avoid running migrations on every deploy.
4.  You will also need to create a superuser on the production database. You can do this by temporarily changing the `Procfile` to `web: python manage.py createsuperuser && gunicorn core.wsgi` and following the interactive prompts in the deploy logs. Remember to change it back.
