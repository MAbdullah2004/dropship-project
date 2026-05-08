from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Products
    path('products/', views.product_list, name='products'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('wholesaler/products/', views.my_products, name='my_products'),
    path('wholesaler/add-product/', views.add_product, name='add_product'),
    path('wholesaler/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('wholesaler/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('wholesaler/orders/', views.wholesaler_orders, name='wholesaler_orders'),
    path('wholesaler/orders/dispatch/<int:pk>/', views.dispatch_order, name='dispatch_order'),

    # Orders
    path('reseller/place-order/', views.place_order, name='place_order'),
    path('reseller/place-order/<slug:slug>/', views.place_order, name='place_order_product'),
    path('reseller/orders/', views.my_orders, name='my_orders'),
    path('reseller/orders/cancel/<int:pk>/', views.cancel_order, name='cancel_order'),
    path('reseller/payout/', views.request_payout, name='request_payout'),
    path('reseller/payouts/', views.my_payouts, name='my_payouts'),

    # Admin
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/verify/<int:pk>/', views.verify_user, name='verify_user'),
    path('admin-panel/users/reject/<int:pk>/', views.reject_user, name='reject_user'),
    path('admin-panel/users/restore/<int:pk>/', views.restore_user, name='restore_user'),
    path('admin-panel/products/', views.admin_products, name='admin_products'),
    path('admin-panel/products/approve/<int:pk>/', views.approve_product, name='approve_product'),
    path('admin-panel/products/reject/<int:pk>/', views.reject_product, name='reject_product'),
    path('admin-panel/products/delete/<int:pk>/', views.delete_product_admin, name='delete_product_admin'),
    path('admin-panel/orders/', views.admin_orders, name='admin_orders'),
    path('admin-panel/orders/update/<int:pk>/', views.update_order_status, name='update_order_status'),
    path('admin-panel/payouts/', views.admin_payouts, name='admin_payouts'),
    path('admin-panel/payouts/paid/<int:pk>/', views.mark_payout_paid, name='mark_payout_paid'),

    # Separate Admin Login
    path('admin-login/', views.admin_login_view, name='admin_login'),
]
