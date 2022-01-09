from django.urls import path
from .views import BrandCategory, EditProfile, ItemCategory, allItems, cart, home, itemDetail, loginPage, logoutUser, userProfile, signup, VerificationView


urlpatterns = [
    path('', home, name='home'),
    path('<int:id>/<slug:slug>', itemDetail, name='itemDetail'),
    path('all-items/', allItems, name='allItems'),
    path('cart/', cart, name='cart'),
    path('search/', allItems, name='search'),
    path('brand-items/', BrandCategory.as_view(), name='brandItems'),
    path('category-items/', ItemCategory.as_view(), name='itemCategory'),
    path('search/', allItems, name='search'),
    path('profile/', userProfile, name='profile'),
    path('edit-profile/', EditProfile.as_view(), name='editProfile'),
    path('signup/', signup, name='signup'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name="logout"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),
]
