# DropShip Pakistan - Django Dropshipping Platform

## 🚀 Quick Start

### 1. Install Requirements
```bash
pip install django pillow
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Admin Account
```bash
python manage.py createsuperuser
```
Or use the pre-created:
- **Username:** admin  
- **Password:** admin123

### 4. Run Server
```bash
python manage.py runserver
```

Open: http://127.0.0.1:8000

---

## 👥 User Roles

### Admin (admin / admin123)
- Verify/reject reseller & wholesaler accounts
- Approve/reject products submitted by wholesalers
- Manage all orders (update status, tracking, courier)
- Process payout requests
- Access: `/admin-panel/`

### Wholesaler
- Register → wait for admin verification
- Add products (with images, prices)
- Products go to admin for approval before going live
- View orders placed on their products

### Reseller
- Register → wait for admin verification
- Browse all approved products
- Set their own selling price (profit = selling - wholesale)
- Place orders with customer details
- Track order status & tracking numbers
- Request payouts for delivered orders

---

## 📁 Project Structure
```
dropship_project/
├── core/
│   ├── models.py      # User, Product, Order, Payout, Category
│   ├── views.py       # All views
│   ├── urls.py        # URL routing
│   ├── forms.py       # Django forms
│   └── admin.py       # Django admin
├── templates/core/    # All HTML templates
├── static/css/        # Stylesheet
├── media/             # Uploaded images
└── dropship_project/
    ├── settings.py
    └── urls.py
```

## 🔗 Key URLs
| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/register/` | Register account |
| `/login/` | Login |
| `/dashboard/` | Role-based dashboard |
| `/products/` | Browse products |
| `/wholesaler/add-product/` | Add product |
| `/reseller/place-order/` | Place order |
| `/admin-panel/users/` | Admin: manage users |
| `/admin-panel/products/` | Admin: approve products |
| `/admin-panel/orders/` | Admin: manage orders |
| `/django-admin/` | Django built-in admin |

## ⚙️ Production Tips
1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Use PostgreSQL instead of SQLite
4. Configure `ALLOWED_HOSTS`
5. Set up static files with `collectstatic`
