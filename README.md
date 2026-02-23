## Premium Services Store API
This is a Django Rest Framework (DRF) based e-commerce API for selling premium subscription services for platforms like Telegram, Spotify, YouTube, and more. Users can browse applications (categories), select services, add them to a cart with custom fields (e.g., username, password), proceed to checkout, and complete payments via Zarinpal gateway. It includes features like user authentication, phone verification via SMS (using Kavenegar), discounts, order management, and admin controls. The project is containerized with Docker for easy deployment and uses Celery for asynchronous tasks like SMS sending.

## Installation
Use the package manager pip to install packages.
```bash
pip install -r requirements.txt
```

Then you should add .env file in the project to set environment variables
```bash
SECRET_KEY=example
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost


POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=store_db
POSTGRES_USER=example
POSTGRES_PASSWORD=example
POSTGRES_HOST=example
POSTGRES_PORT=5432


ZARINPAL_MERCHANT_ID=00000000-0000-0000-0000-000000000000
ZARINPAL_SANDBOX=True
ZARINPAL_REQUEST_URL=https://sandbox.zarinpal.com/pg/v4/payment/request.json
ZARINPAL_VERIFY_URL=https://sandbox.zarinpal.com/pg/v4/payment/verify.json
ZARINPAL_START_PAY_URL=https://sandbox.zarinpal.com/pg/StartPay/
ZARINPAL_CALLBACK_URL=http://127.0.0.1:8000/orders/{order_id}/callback/


KAVENEGAR_API_KEY=YOUR_KAVENEGAR_API_KEY
KAVENEGAR_SENDER=YOUR_KAVENEGAR_API_KEY_PHONE_NUMBER


CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_ACCEPT_CONTENT=json
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_TIMEZONE=UTC
```
