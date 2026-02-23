from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CategoryForm, ItemForm
from .models import Category, Item, Profile

User = get_user_model()

CURRENCY_RATES = {
    'USD': Decimal('1.00'),
    'GBP': Decimal('0.79'),
    'EUR': Decimal('0.92'),
    'CAD': Decimal('1.35'),
    'AUD': Decimal('1.53'),
}

CURRENCY_SYMBOLS = {
    'USD': '$',
    'GBP': '£',
    'EUR': '€',
    'CAD': 'C$',
    'AUD': 'A$',
}

DEFAULT_CATEGORIES = [
    'Electronics',
    'Clothing',
    'Furniture',
    'Gaming',
    'Appliances',
    'Collectibles',
    'Other',
]


def convert_amount(amount, source_currency, target_currency):
    if amount is None:
        return None

    source_rate = CURRENCY_RATES.get(source_currency, Decimal('1.00'))
    target_rate = CURRENCY_RATES.get(target_currency, Decimal('1.00'))

    if source_rate == 0:
        return amount

    amount_in_usd = amount / source_rate
    return amount_in_usd * target_rate


def ensure_default_categories(user):
    for category_name in DEFAULT_CATEGORIES:
        if not Category.objects.filter(user=user, name__iexact=category_name).exists():
            Category.objects.create(user=user, name=category_name)

@login_required(login_url='/login/')
def home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    ensure_default_categories(request.user)

    query = request.GET.get('q', '').strip()
    selected_sort = request.GET.get('sort', 'newest').strip()

    items = Item.objects.filter(user=request.user).select_related('category')
    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if selected_sort == 'name_az':
        items = items.order_by('name', '-created_at')
    elif selected_sort == 'date_oldest':
        items = items.order_by('created_at')
    elif selected_sort == 'category_az':
        items = items.order_by('category__name', '-created_at')
    elif selected_sort == 'condition_az':
        items = items.order_by('condition', '-created_at')
    else:
        items = items.order_by('-created_at')

    categories = Category.objects.filter(user=request.user)

    selected_currency = profile.preferred_currency or 'USD'
    currency_rate = CURRENCY_RATES.get(selected_currency, Decimal('1.00'))
    currency_symbol = CURRENCY_SYMBOLS.get(selected_currency, '$')

    converted_total_purchase = Decimal('0')
    converted_total_estimated = Decimal('0')

    converted_items = []
    for item in items:
        purchase_converted = convert_amount(item.purchase_price or Decimal('0'), item.currency, selected_currency)
        estimated_converted = convert_amount(item.estimated_value, item.currency, selected_currency)
        gain_loss_converted = (estimated_converted - purchase_converted) if estimated_converted is not None else None

        converted_total_purchase += purchase_converted
        if estimated_converted is not None:
            converted_total_estimated += estimated_converted

        converted_items.append({
            'item': item,
            'purchase_converted': purchase_converted,
            'estimated_converted': estimated_converted,
            'gain_loss_converted': gain_loss_converted,
        })

    if selected_sort == 'purchase_high':
        converted_items.sort(key=lambda row: row['purchase_converted'], reverse=True)
    elif selected_sort == 'purchase_low':
        converted_items.sort(key=lambda row: row['purchase_converted'])
    elif selected_sort == 'loss_high':
        converted_items.sort(key=lambda row: row['gain_loss_converted'] if row['gain_loss_converted'] is not None else Decimal('999999'))

    converted_total_gain_loss = converted_total_estimated - converted_total_purchase
    converted_total_lost = (converted_total_purchase - converted_total_estimated) if converted_total_estimated < converted_total_purchase else Decimal('0')

    context = {
        'profile': profile,
        'items': converted_items,
        'item_count': items.count(),
        'category_count': categories.count(),
        'selected_sort': selected_sort,
        'search_query': query,
        'total_purchase': converted_total_purchase,
        'total_estimated': converted_total_estimated,
        'total_gain_loss': converted_total_gain_loss,
        'total_lost': converted_total_lost,
        'selected_currency': selected_currency,
        'currency_symbol': currency_symbol,
        'currency_choices': Profile.Currency.choices,
        'exchange_rate': currency_rate,
    }
    return render(request, 'tracker/home.html', context)


@login_required(login_url='/login/')
def item_detail_view(request, item_id):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    item = get_object_or_404(Item.objects.select_related('category'), pk=item_id, user=request.user)

    selected_currency = profile.preferred_currency or 'USD'
    currency_symbol = CURRENCY_SYMBOLS.get(selected_currency, '$')

    purchase_converted = convert_amount(item.purchase_price or Decimal('0'), item.currency, selected_currency)
    estimated_converted = convert_amount(item.estimated_value, item.currency, selected_currency)
    gain_loss_converted = (estimated_converted - purchase_converted) if estimated_converted is not None else None

    context = {
        'profile': profile,
        'item': item,
        'currency_symbol': currency_symbol,
        'selected_currency': selected_currency,
        'purchase_converted': purchase_converted,
        'estimated_converted': estimated_converted,
        'gain_loss_converted': gain_loss_converted,
    }
    return render(request, 'tracker/item_detail.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('tracker:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return render(request, 'tracker/register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'tracker/register.html', {
                'username_value': username,
                'email_value': email,
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'tracker/register.html', {
                'username_value': username,
                'email_value': email,
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
            return render(request, 'tracker/register.html', {
                'username_value': username,
                'email_value': email,
            })

        try:
            validate_password(password)
        except ValidationError as error:
            for error_message in error.messages:
                messages.error(request, error_message)
            return render(request, 'tracker/register.html', {
                'username_value': username,
                'email_value': email,
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Account created successfully. Welcome!')
        return redirect('tracker:home')

    return render(request, 'tracker/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('tracker:home')

    if request.method == 'POST':
        login_input = request.POST.get('login', '').strip()
        password = request.POST.get('password', '')

        username = login_input
        if '@' in login_input:
            matched_user = User.objects.filter(email__iexact=login_input).first()
            if matched_user:
                username = matched_user.username

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('tracker:home')

        messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'tracker/login.html', {'login_value': request.POST.get('login', '')})

def logout_view(request):
    logout(request)
    return redirect('tracker:login')


@login_required(login_url='/login/')
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        display_name = request.POST.get('display_name', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        bio = request.POST.get('bio', '').strip()
        photo = request.FILES.get('photo')

        if email and User.objects.exclude(pk=request.user.pk).filter(email=email).exists():
            messages.error(request, 'That email is already used by another account.')
            return render(request, 'tracker/profile.html', {'profile': profile})

        request.user.first_name = first_name
        request.user.last_name = last_name
        if email:
            request.user.email = email
        request.user.save(update_fields=['first_name', 'last_name', 'email'])

        profile.display_name = display_name
        profile.bio = bio
        if photo:
            profile.photo = photo
        profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('tracker:profile')

    return render(request, 'tracker/profile.html', {'profile': profile})


@login_required(login_url='/login/')
def category_create_view(request):
    ensure_default_categories(request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            if Category.objects.filter(user=request.user, name__iexact=category.name).exists():
                messages.error(request, 'You already have a category with that name.')
            else:
                category.save()
                messages.success(request, 'Category created.')
                return redirect('tracker:home')
    else:
        form = CategoryForm()

    return render(request, 'tracker/category_form.html', {'form': form})


@login_required(login_url='/login/')
def item_create_view(request):
    ensure_default_categories(request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.currency = profile.preferred_currency
            item.save()
            messages.success(request, 'Item added successfully.')
            return redirect('tracker:home')
    else:
        form = ItemForm(user=request.user)

    return render(request, 'tracker/item_form.html', {
        'form': form,
        'is_edit': False,
        'active_currency': profile.preferred_currency,
    })


@login_required(login_url='/login/')
def item_edit_view(request, item_id):
    ensure_default_categories(request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    item = get_object_or_404(Item, pk=item_id, user=request.user)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully.')
            return redirect('tracker:home')
    else:
        form = ItemForm(instance=item, user=request.user)

    return render(request, 'tracker/item_form.html', {
        'form': form,
        'item': item,
        'is_edit': True,
        'active_currency': profile.preferred_currency,
    })


@login_required(login_url='/login/')
def item_delete_view(request, item_id):
    item = get_object_or_404(Item, pk=item_id, user=request.user)

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted.')
        return redirect('tracker:home')

    return render(request, 'tracker/item_confirm_delete.html', {'item': item})


@login_required(login_url='/login/')
def currency_update_view(request):
    if request.method != 'POST':
        return redirect('tracker:home')

    profile, _ = Profile.objects.get_or_create(user=request.user)
    currency_code = request.POST.get('currency', 'USD').upper()

    valid_codes = {choice[0] for choice in Profile.Currency.choices}
    if currency_code not in valid_codes:
        messages.error(request, 'Invalid currency selected.')
        return redirect('tracker:home')

    profile.preferred_currency = currency_code
    profile.save(update_fields=['preferred_currency'])
    messages.success(request, f'Currency updated to {currency_code}.')
    return redirect('tracker:home')


@login_required(login_url='/login/')
def settings_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    context = {
        'profile': profile,
        'selected_currency': profile.preferred_currency,
        'currency_choices': Profile.Currency.choices,
    }
    return render(request, 'tracker/settings.html', context)