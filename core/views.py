from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import User, Product, Order, Payout, Category
from .forms import RegisterForm, ProductForm, OrderForm, PayoutRequestForm
from functools import wraps


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    products = Product.objects.filter(status='approved').order_by('-created_at')[:12]
    categories = Category.objects.all()
    return render(request, 'core/home.html', {'products': products, 'categories': categories})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False
            # Save bank / payment info
            user.bank_name = request.POST.get('bank_name', '')
            user.bank_account_title = request.POST.get('bank_account_title', '')
            user.bank_account_number = request.POST.get('bank_account_number', '')
            user.easypaisa_number = request.POST.get('easypaisa_number', '')
            user.jazzcash_number = request.POST.get('jazzcash_number', '')
            user.save()
            messages.success(request, '✅ Account created! Wait for admin verification.')
            return redirect('login')
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.role == 'admin':
                messages.error(request, '⚠️ Admins must use the Admin Login page.')
                return redirect('admin_login')
            if not user.is_verified:
                messages.error(request, 'Your account is pending admin verification.')
                return redirect('login')
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')


def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('dashboard')
        logout(request)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.role == 'admin':
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}! Admin panel is ready.')
            return redirect('dashboard')
        messages.error(request, 'Invalid admin credentials or insufficient permissions.')
    return render(request, 'core/admin_login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    if user.role == 'admin':
        context.update({
            'total_users': User.objects.count(),
            'pending_users': User.objects.filter(is_verified=False).exclude(role='admin').count(),
            'total_products': Product.objects.count(),
            'pending_products': Product.objects.filter(status='pending').count(),
            'total_orders': Order.objects.count(),
            'recent_orders': Order.objects.order_by('-created_at')[:10],
            'pending_payouts': Payout.objects.filter(status='pending').count(),
        })
    elif user.role == 'wholesaler':
        my_products = Product.objects.filter(wholesaler=user)
        context.update({
            'my_products': my_products.count(),
            'approved_products': my_products.filter(status='approved').count(),
            'pending_products': my_products.filter(status='pending').count(),
            'recent_products': my_products.order_by('-created_at')[:5],
            'total_orders': Order.objects.filter(product__wholesaler=user).count(),
        })
    elif user.role == 'reseller':
        my_orders = Order.objects.filter(reseller=user)
        total_profit = my_orders.aggregate(Sum('profit'))['profit__sum'] or 0
        featured_products = Product.objects.filter(status='approved').order_by('-created_at')[:8]
        context.update({
            'total_orders': my_orders.count(),
            'delivered_orders': my_orders.filter(status='delivered').count(),
            'pending_orders': my_orders.filter(status='pending').count(),
            'total_profit': total_profit,
            'recent_orders': my_orders.order_by('-created_at')[:5],
            'available_products': Product.objects.filter(status='approved').count(),
            'featured_products': featured_products,
        })
    return render(request, 'core/dashboard.html', context)


# ===== PRODUCT VIEWS =====
@login_required
def product_list(request):
    category_id = request.GET.get('category')
    search = request.GET.get('q', '')
    products = Product.objects.filter(status='approved')
    if category_id:
        products = products.filter(category_id=category_id)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    categories = Category.objects.all()
    return render(request, 'core/products.html', {'products': products, 'categories': categories, 'search': search})


@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, status='approved')
    return render(request, 'core/product_detail.html', {'product': product})


@role_required('wholesaler')
def add_product(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.wholesaler = request.user
            product.status = 'pending'
            product.save()
            messages.success(request, 'Product submitted for admin approval!')
            return redirect('my_products')
    categories = Category.objects.all().order_by('name')
    return render(request, 'core/add_product.html', {'form': form, 'categories': categories})


@role_required('wholesaler')
def my_products(request):
    products = Product.objects.filter(wholesaler=request.user).order_by('-created_at')
    return render(request, 'core/my_products.html', {'products': products})


@role_required('wholesaler')
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, wholesaler=request.user)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.status = 'pending'
            product.save()
            messages.success(request, 'Product updated and resubmitted for approval.')
            return redirect('my_products')
    categories = Category.objects.all().order_by('name')
    return render(request, 'core/add_product.html', {'form': form, 'edit': True, 'categories': categories})


@role_required('wholesaler')
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, wholesaler=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Product "{product.name}" deleted.')
    return redirect('my_products')


# ===== WHOLESALER ORDER VIEWS =====
@role_required('wholesaler')
def wholesaler_orders(request):
    """Wholesaler sees all orders placed for their products."""
    orders = Order.objects.filter(
        product__wholesaler=request.user
    ).select_related('product', 'reseller').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'core/wholesaler_orders.html', {'orders': orders, 'status_filter': status_filter})


@role_required('wholesaler')
def dispatch_order(request, pk):
    """Wholesaler dispatches an order — sets tracking number & courier."""
    order = get_object_or_404(Order, pk=pk, product__wholesaler=request.user)
    if request.method == 'POST':
        courier = request.POST.get('courier', '').strip()
        tracking = request.POST.get('tracking_number', '').strip()
        if courier and tracking:
            order.status = 'dispatched'
            order.courier = courier
            order.tracking_number = tracking
            order.save()
            messages.success(request, f'✅ Order #{pk} dispatched via {courier}. Tracking: {tracking}')
        else:
            messages.error(request, 'Please enter both courier name and tracking number.')
        return redirect('wholesaler_orders')
    return render(request, 'core/dispatch_order.html', {'order': order})


@role_required('reseller')
def place_order(request, slug=None):
    product = None
    if slug:
        product = get_object_or_404(Product, slug=slug, status='approved')
    form = OrderForm(initial={'product': product})
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.reseller = request.user
            order.save()
            messages.success(request, f'Order #{order.pk} placed successfully!')
            return redirect('my_orders')
    return render(request, 'core/place_order.html', {'form': form, 'product': product})


@role_required('reseller')
def my_orders(request):
    orders = Order.objects.filter(reseller=request.user).order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'core/my_orders.html', {'orders': orders})


@role_required('reseller')
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, reseller=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'❌ Order #{pk} has been cancelled.')
    else:
        messages.error(request, f'Order #{pk} cannot be cancelled (status: {order.status}).')
    return redirect('my_orders')


@role_required('reseller')
def request_payout(request):
    delivered = Order.objects.filter(reseller=request.user, status='delivered')
    total_earnings = delivered.aggregate(Sum('profit'))['profit__sum'] or 0
    form = PayoutRequestForm()
    if request.method == 'POST':
        form = PayoutRequestForm(request.POST)
        if form.is_valid():
            payout = form.save(commit=False)
            payout.reseller = request.user
            payout.save()
            messages.success(request, 'Payout request submitted!')
            return redirect('my_payouts')
    return render(request, 'core/request_payout.html', {'form': form, 'total_earnings': total_earnings})


@role_required('reseller')
def my_payouts(request):
    payouts = Payout.objects.filter(reseller=request.user).order_by('-requested_at')
    return render(request, 'core/my_payouts.html', {'payouts': payouts})


# ===== ADMIN VIEWS =====
@role_required('admin')
def admin_users(request):
    role_filter = request.GET.get('role', '')
    verified_filter = request.GET.get('verified', '')
    users = User.objects.exclude(role='admin').order_by('-date_joined')
    if role_filter:
        users = users.filter(role=role_filter)
    if verified_filter == '0':
        users = users.filter(is_verified=False)
    elif verified_filter == '1':
        users = users.filter(is_verified=True)
    return render(request, 'core/admin_users.html', {'users': users})


@role_required('admin')
def verify_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_verified = True
    user.is_active = True
    user.save()
    messages.success(request, f'✅ {user.username} verified and activated!')
    return redirect('admin_users')


@role_required('admin')
def reject_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = False
    user.is_verified = False
    user.save()
    messages.warning(request, f'❌ {user.username} rejected and deactivated.')
    return redirect('admin_users')


@role_required('admin')
def restore_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.is_verified = True
    user.save()
    messages.success(request, f'↩️ {user.username} account restored.')
    return redirect('admin_users')


@role_required('admin')
def admin_products(request):
    status_filter = request.GET.get('status', '')
    products = Product.objects.all().order_by('-created_at')
    if status_filter:
        products = products.filter(status=status_filter)
    return render(request, 'core/admin_products.html', {'products': products})


@role_required('admin')
def approve_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.status = 'approved'
    product.save()
    messages.success(request, f'✅ Product "{product.name}" approved!')
    return redirect('admin_products')


@role_required('admin')
def reject_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.status = 'rejected'
    product.save()
    messages.warning(request, f'❌ Product "{product.name}" rejected.')
    return redirect('admin_products')


@role_required('admin')
def delete_product_admin(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    messages.success(request, f'🗑️ Product "{name}" deleted permanently.')
    return redirect('admin_products')


@role_required('admin')
def admin_orders(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.all().order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'core/admin_orders.html', {'orders': orders})


@role_required('admin')
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        tracking = request.POST.get('tracking_number', '')
        courier = request.POST.get('courier', '')
        order.status = status
        order.tracking_number = tracking
        order.courier = courier
        order.save()
        messages.success(request, f'Order #{pk} updated to {status}.')
    return redirect('admin_orders')


@role_required('admin')
def admin_payouts(request):
    payouts = Payout.objects.all().order_by('-requested_at')
    return render(request, 'core/admin_payouts.html', {'payouts': payouts})


@role_required('admin')
def mark_payout_paid(request, pk):
    payout = get_object_or_404(Payout, pk=pk)
    if request.method == 'POST':
        payout.status = 'paid'
        payout.transaction_id = request.POST.get('transaction_id', '')
        payout.paid_at = timezone.now()
        payout.save()
        messages.success(request, f'Payout #{pk} marked as paid.')
    return redirect('admin_payouts')
