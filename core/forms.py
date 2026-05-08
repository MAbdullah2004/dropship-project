from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Order, Payout


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ('reseller', 'Reseller - I want to sell products'),
        ('wholesaler', 'Wholesaler - I want to supply products'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    phone = forms.CharField(max_length=20)
    city = forms.CharField(max_length=100)
    business_name = forms.CharField(max_length=200)
    cnic = forms.CharField(max_length=20, label='CNIC')
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'city', 'business_name', 'cnic', 'role', 'password1', 'password2']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'wholesale_price', 'suggested_retail_price', 'stock', 'image', 'image2', 'image3', 'weight']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'quantity', 'reseller_price', 'customer_name', 'customer_phone', 'customer_city', 'customer_address', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(status='approved')


class PayoutRequestForm(forms.ModelForm):
    class Meta:
        model = Payout
        fields = ['amount', 'payment_method', 'notes']
