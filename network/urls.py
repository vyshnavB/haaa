
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("pageindex", views.pageindex, name="pageindex"),
    path("n/login", views.login_view, name="login"),
    path("n/logout", views.logout_view, name="logout"),
    path("n/register", views.register, name="register"),
    path("<str:username>", views.profile, name='profile'),
    path("n/following", views.following, name='following'),
    path("n/saved", views.saved, name="saved"),
    path("n/user_create_post", views.user_create_post, name="user_create_post"),
    path("n/create_pagepost/<int:pageid>", views.create_pagepost, name="create_pagepost"),
    path("n/post/<int:id>/like", views.like_post, name="likepost"),
    path("n/post/<int:id>/unlike", views.unlike_post, name="unlikepost"),
    path("n/post/<int:id>/save", views.save_post, name="savepost"),
    path("n/post/<int:id>/unsave", views.unsave_post, name="unsavepost"),
    path("n/post/<int:post_id>/comments", views.comment, name="comments"),
    path("n/post/<int:post_id>/write_comment",views.comment, name="writecomment"),
    path("n/post/<int:post_id>/delete", views.delete_post, name="deletepost"),
    path("<str:username>/follow", views.follow, name="followuser"),
    path("<str:username>/unfollow", views.unfollow, name="unfollowuser"),
    path("n/post/<int:post_id>/edit", views.edit_post, name="editpost"),
    path('n/test',views.test,name="test"),
    path('n/page_registration/<int:pk>',views.page_registration,name="page_registration"),
    path('n/page_creation',views.page_creation,name="page_creation"),
    path('n/pag/<int:pk>',views.pag,name="pag"),
    path('pageprofile/<int:pageid>',views.pageprofile,name="pageprofile"),
    path('n/cart',views.cart,name="cart"),
    path('n/checkout',views.checkout,name="checkout"),
    path('n/product_detail/<int:id>',views.product_detail,name="product_detail"),
    path('n/add_product',views.add_product,name="add_product"),
    
    path('add_cart/<int:id>',views.add_cart,name='add_cart'),

    path('zip',views.zip,name='zip'),

    path('remove_cart/<int:id>',views.remove_cart,name='remove_cart'),

    path('remove_cart_all',views.remove_cart_all,name='remove_cart_all'),

    
    path('shipping_address',views.shipping_address,name='shipping_address'),
    

    path('place_order/<int:id>',views.place_order,name='place_order'),

    path('n/dashboard',views.dashboard,name='dashboard'),

    path('dashboard_profile',views.dashboard_profile,name='dashboard_profile'),

    path('dash_edit_profile',views.dash_edit_profile,name='dash_edit_profile'),

    path('edit',views.edit,name='edit'),

    path('dash_address_book',views.dash_address_book,name='dash_address_book'),

    path('track_order',views.track_order,name='track_order'),

    path('n/my_order',views.my_order,name='my_order'),

    path('manage_order/<int:id>',views.manage_order,name='manage_order'),
    path('n/pagepost/<int:pk>',views.pagepost,name='pagepost'),
    path('n/mypage/<int:pk>',views.mypage,name='mypage'),
  
    path('n/edit_profile/<int:pk>',views.edit_profile,name='edit_profile'),
    path('n/edit_pr/<int:pk>',views.edit_pr,name='edit_pr'),
    path('n/edit_page/<int:pk>',views.edit_page,name='edit_page'),
    path('n/edit_pages/<int:pk>',views.edit_pages,name='edit_pages'),
    path('search/', views.search, name='search'),





]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

