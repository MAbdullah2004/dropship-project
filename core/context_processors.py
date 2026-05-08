from .models import User, Order, Product, Payout


def admin_context(request):
    """Inject admin notification counts into every template."""
    if not request.user.is_authenticated or not hasattr(request.user, 'role'):
        return {}
    if request.user.role != 'admin':
        return {}
    return {
        'pending_users': User.objects.filter(is_verified=False).exclude(role='admin').count(),
        'pending_products': Product.objects.filter(status='pending').count(),
        'pending_payouts': Payout.objects.filter(status='pending').count(),
    }
