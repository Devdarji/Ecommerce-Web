from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from shop.forms import CreateUserForm, ProfileForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from shop.models import Brand, Category, Item, Profile
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from landmark import settings
import threading
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user
from django.views import View
from django.views.generic import ListView, FormView
from django.contrib.auth.decorators import login_required
# Create your views here.

# ---------------------   Sending Email  ------------#


class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


# ---------------------------- SignUp ---------------------------
@unauthenticated_user
def signup(request):
    form = CreateUserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')

        current_site = get_current_site(request)
        email_subject = 'Activate your Account'
        message = render_to_string('account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        })
        email_message = EmailMessage(
            email_subject, message, settings.EMAIL_HOST_USER, [email])
        EmailThread(email_message).start()
        messages.add_message(request, messages.SUCCESS,
                             'Hey ' + username + ' Check your Email and Activate your MyShop Account ')
        return redirect('login')
    else:
        form = CreateUserForm()

    context = {
        'form': form
    }
    return render(request, 'signup.html', context)

# ------------------------ User Verification -----------------------


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Account Activated successfully')
            return redirect('login')
        return render(request, 'activate_failed.html', status=401)

# -----------------------------  Login ------------------------------------


@unauthenticated_user
def loginPage(request):
    next = None
    if request.method == "POST":
        loginPage.next = request.GET.get("next")
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if loginPage.next:
                return HttpResponseRedirect(loginPage.next)
            else:
                loginPage.next = None
                return redirect('profile')
        else:
            messages.info(request, 'Username or Password in incorrect')
    return render(request, 'login.html')

# ----------------------- logout -------------------------------


def logoutUser(request):
    logout(request)
    return redirect('login')


# ---------------------------- User Profile  ----------------------------
@login_required(login_url="login")
def userProfile(request):
    p = request.user.profile
    print(p)
    you = p.user
    address = p.address.all()[0]
    context = {
        'p': p,
        'you': you,
        'address': address
    }
    return render(request, 'profile.html', context)

# ---------------------------- Edit Profile   --------------------------------


class EditProfile(FormView):
    template_name = 'edit_profile.html'
    form_class = ProfileForm

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        profile = Profile.objects.get(user_id=request.user)
        address = profile.address.all()[0]
        context['profile'] = profile
        context['address'] = address
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user_id=user)
        address = profile.address.all()[0]

        # user Detail
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.save()

        # User address
        address.address_line1 = request.POST.get("address_line1")
        address.address_line2 = request.POST.get("address_line2")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.zipcode = request.POST.get("zipcode")
        address.country = request.POST.get("country")
        address.save()

        profile.mobile_no = request.POST.get("mobile_no")
        profile.alternate_mobile_no = request.POST.get("alternate_mobile_no")

        try:
            profile.save()
        except:
            return HttpResponse("Mobile no. should be unique")

        return redirect('profile')



# --------------------- Add Item In Cart Function ---------------------

def addToCart(request):
    # request.session.get('cart').clear()
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    if request.method == "POST":
        item = request.POST.get('item')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')

        if cart:
            quantity = cart.get(item)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(item)
                    else:
                        cart[item] = quantity - 1
                else:
                    cart[item] = quantity + 1
            else:
                cart[item] = 1
        else:
            cart = {}
            cart[item] = 1

        request.session['cart'] = cart
        if None in request.session['cart']:
            print(True)
            del request.session['cart'][None]
        if 'null' in request.session['cart']:
            print(True)
            del request.session['cart']['null']
        print(request.session['cart'])
        return redirect("home")
# ----------------------- home Page --------------------------------


def home(request):
    items = Item.objects.all().order_by('-stock')
    addToCart(request)
    context = {
        'items': items
    }
    return render(request, 'index.html', context)

# ----------------------------  All Items   -----------------------


def allItems(request):
    items = Item.objects.all()
    addToCart(request)
    params = {}
    sort = ''

    # search
    if request.GET.get("q"):
        search = request.GET.get("q")
        items1 = Item.objects.filter(title__icontains=search)
        items2 = Item.objects.filter(brand__title__icontains=search)
        items = items1 | items2

    # Sort and Order
    if request.GET.get("sort"):
        sort = request.GET.get("sort")
        params['sort'] = sort
        if sort == 'a-z':
            items = items.order_by("title")
        elif sort == 'z-a':
            items = items.order_by("-title")
        elif sort == "high-low":
            items = items.order_by("-price")
        else:
            items = items.order_by("price")

    context = {
        'items': items,
        'sort': sort
    }
    return render(request, 'all_items.html', context)

# --------------------------------  Show Item By Brand ---------------------


class BrandCategory(ListView):
    model = Brand
    template_name = "brand_category.html"

    def get_context_data(self, *args, **kwargs):
        queryset = kwargs.pop("object_list", None)
        if queryset is None:
            self.object_list = self.get_queryset(*args, **kwargs)
        return super().get_context_data(**kwargs)

    # Brand Name and total item
    def get_queryset(self, *args, **kwargs):
        qs = super(BrandCategory, self).get_queryset(*args, **kwargs)
        qs = qs.order_by("title")
        context = []
        for q in qs:
            total_brand_items = q.item_set.all().count()
            context.append(
                {
                    "brand": q,
                    "items": total_brand_items,
                }
            )
        return context

    # Order and Sort
    def post(self, request, *args, **kwargs):
        addToCart(request)
        context = self.get_context_data(*args, **kwargs)
        brand_id = request.POST.get("brand_id")
        if request.POST.get("sort"):
            sort = request.POST.get("sort")
            context["sort"] = sort
            if sort == "a-z":
                items = Item.objects.filter(
                    brand_id=brand_id).order_by("title")
            elif sort == "z-a":
                items = Item.objects.filter(
                    brand_id=brand_id).order_by("-title")
            elif sort == "high-low":
                items = Item.objects.filter(
                    brand_id=brand_id).order_by("-price")
            else:
                items = Item.objects.filter(
                    brand_id=brand_id).order_by("price")
        else:
            items = Item.objects.filter(brand_id=brand_id)
        context["items"] = items
        return self.render_to_response(context)

# ------------------------------ All Item By Category -----------------


class ItemCategory(ListView):
    model = Category
    template_name = "item_category.html"
    def get_context_data(self, *args, **kwargs):
        queryset = kwargs.pop("object_list", None)
        if queryset is None:
            self.object_list = self.get_queryset(*args, **kwargs)
        return super().get_context_data(**kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super(ItemCategory, self).get_queryset(*args, **kwargs)
        qs = qs.order_by("title")
        context = []
        for q in qs:
            total_category_items = q.item_set.all().count()
            context.append(
                {
                    "category": q,
                    "total_category_items": total_category_items,
                }
            )
        return context

    # Order and Sort
    def post(self, request, *args, **kwargs):
        addToCart(request)
        context = self.get_context_data(*args, **kwargs)
        category_id = request.POST.get("category_id")
        if request.POST.get("sort"):
            sort = request.POST.get("sort")
            context["sort"] = sort
            if sort == "a-z":
                items = Item.objects.filter(category_id=category_id).order_by(
                    "title"
                )
            elif sort == "z-a":
                items = Item.objects.filter(category_id=category_id).order_by(
                    "-title"
                )
            elif sort == "high-low":
                items = Item.objects.filter(category_id=category_id).order_by(
                    "-price"
                )
            else:
                items = Item.objects.filter(category_id=category_id).order_by(
                    "price"
                )
        else:
            items = Item.objects.filter(category_id=category_id)
        context["items"] = items
        return self.render_to_response(context)

# ------------------------------ Item Detail Page    -------------------------


def itemDetail(request, id, slug):
    try:
        item = Item.objects.get(pk=id, slug=slug)

        # This text for stock available or not
        if int(item.stock) >= 1:
            text = 'In stock'
        else:
            text = 'Out of Stock'

        # Similar Item
        similar_item1 = Item.objects.filter(brand=item.id)[:4]
        similar_item2 = Item.objects.filter(category=item.category)[:5]
        similar_items = similar_item1 | similar_item2
        print(similar_items)
    except:
        raise Http404('Something Went Wrong')

    context = {
        'item': item,
        'text': text,
        'similar_items': similar_items
    }
    return render(request, 'itemDetail.html', context)


@login_required(login_url="login")
def cart(request):
    ids = list(request.session.get('cart').keys())
    items = Item.get_items_by_id(ids)
    print(items)
    context = {
        'items':items
    }
    return render (request, 'cart.html', context)