# Laundrex mobile integration guide

## What the uploaded Django app already has
- `orders.Customer`
- `orders.Order`
- `orders.OrderItem`
- `orders.OrderStatusLog`
- `management.Branch`
- `catalog.Service`
- `catalog.Item`
- `catalog.BranchItemServicePrice`
- `payments.Payment`

## Important finding
The current web app supports customer records, but **not customer authentication accounts for the mobile app**.
That means the mobile app still needs a small backend extension for:
- customer account login
- phone OTP
- saved addresses
- JWT auth

## What this patch adds
- `CustomerAccount` linked to Django `User` and `orders.Customer`
- `SavedAddress`
- `PhoneOTP`
- `/api/auth/*`
- `/api/laundries`
- `/api/laundries/{id}/catalog`
- `/api/addresses`
- `/api/orders`
- `/api/orders/{id}`
- `/api/orders/{id}/tracking`
- `/api/payment-methods`

## Existing-to-mobile field mapping
- Laundry shop: existing `management.Branch`
- Order branch: existing `orders.Order.branch` (branch code string)
- Catalog prices: existing `catalog.BranchItemServicePrice`
- Customer identity: existing `orders.Customer`, now linked to `CustomerAccount`
- Payment methods: existing `payments.Payment.Method`
- Tracking timeline: existing `orders.OrderStatusLog`

## Install patch
1. Copy `django_patch/apps/mobile_api` into your Django project `apps/` folder.
2. Add settings and URLs from `django_patch/patch_instructions.md`.
3. Install packages:
   ```bash
   pip install djangorestframework djangorestframework-simplejwt
   ```
4. Run migrations:
   ```bash
   python manage.py makemigrations mobile_api
   python manage.py migrate
   ```
5. Start backend:
   ```bash
   python manage.py runserver
   ```

## Flutter base URL
- Android emulator: `http://10.0.2.2:8000`
- iOS simulator / desktop: `http://127.0.0.1:8000`
- Real phone on same Wi‑Fi: `http://YOUR_PC_IP:8000`
