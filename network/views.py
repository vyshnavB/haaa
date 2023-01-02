from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .models import *




def index(request):
    all_posts = Post.objects.all().order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
    return render(request, "network/index.html", {
        "posts": posts,
        "suggestions": suggestions,      
        "page": "all_posts",
        'profile': False
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
       
        cover = request.FILES.get('cover')
       

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try: 
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            if profile is not None:
                user.profile_pic = profile
            else:
                user.profile_pic = "profile_pic/no_pic.png"
            user.cover = cover           
            user.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")



def profile(request, username):
    user = User.objects.get(username=username)
    all_posts = Post.objects.filter(creater=user).order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    follower = False
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]

        if request.user in Follower.objects.get(user=user).followers.all():
            follower = True
    
    follower_count = Follower.objects.get(user=user).followers.all().count()
    following_count = Follower.objects.filter(followers=user).count()
    return render(request, 'network/profile.html', {
        "username": user,
        "posts": posts,
        "posts_count": all_posts.count(),
        "suggestions": suggestions,
        "page": "profile",
        "is_follower": follower,
        "follower_count": follower_count,
        "following_count": following_count
    })



def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values('user')
        all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "following"
        })
    else:
        return HttpResponseRedirect(reverse('login'))


def saved(request):
    if request.user.is_authenticated:
        all_posts = Post.objects.filter(savers=request.user).order_by('-date_created')

        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)

        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "saved"
        })
    else:
        return HttpResponseRedirect(reverse('login'))
        


@login_required
def user_create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        status=request.POST.get('status')
        Product_Price=request.POST.get('Product_Price')
        if Product_Price=="":
            Product_Price=None

        try:
            post = Post.objects.create(creater=request.user, content_text=text, content_image=pic,status=status,Product_Price=Product_Price,posts_type="user_post")
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'")

@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        img_chg = request.POST.get('img_change')
        post_id = request.POST.get('id')
        post = Post.objects.get(id=post_id)
        try:
            post.content_text = text
            if img_chg != 'false':
                post.content_image = pic
            post.save()
            
            if(post.content_text):
                post_text = post.content_text
            else:
                post_text = False
            if(post.content_image):
                post_image = post.img_url()
            else:
                post_image = False
            
            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image
            })
        except Exception as e:
    
            return JsonResponse({
                "success": False
            })
    else:
            return HttpResponse("Method must be 'POST'")

@csrf_exempt
def like_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unlike_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def save_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unsave_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def follow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
          
            try:
                (follower, create) = Follower.objects.get_or_create(user=user)
                follower.followers.add(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unfollow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
        
            try:
                follower = Follower.objects.get(user=user)
                follower.followers.remove(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            comment = data.get('comment_text')
            post = Post.objects.get(id=post_id)
            try:
                newcomment = Comment.objects.create(post=post,commenter=request.user,comment_content=comment)
                post.comment_count += 1
                post.save()
                print(newcomment.serialize())
                return JsonResponse([newcomment.serialize()], safe=False, status=201)
            except Exception as e:
                return HttpResponse(e)
    
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)
        comments = comments.order_by('-comment_time').all()
        return JsonResponse([comment.serialize() for comment in comments], safe=False)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(id=post_id)
            if request.user == post.creater:
                try:
                    delet = post.delete()
                    return HttpResponse(status=201)
                except Exception as e:
                    return HttpResponse(e)
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


def test(request):
    return render(request,"test.html")

#page


def pageindex(request):
    all_posts = pageposts.objects.all().order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    pagepost = paginator.get_page(page_number)
    followings = []
    suggestions = []
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
    return render(request, "pageindex.html", {
        "posts": pagepost,
        "suggestions": suggestions, 
        "page": "all_posts",
        'profile': False
    })

def pag(request,pk):

    pag=page.objects.all()
    return render(request,"page.html",{"pag":pag,}) 



def mypage(request,pk):
    
    pag=page.objects.all()
    return render(request,"mypage.html",{"pag":pag,})  




def page_registration(request,pk):
    rgs=User.objects.get(id=pk)
    return render(request,"page_registration.html",{"rgs":rgs})

    
        

def page_creation(request):
    if request.method == 'POST':
        pagename = request.POST.get('pagename')
        website = request.FILES.get('website')
        username=request.POST.get('username')
        category= request.POST.get('category')
        emial=request.POST.get('emial')
        image=request.FILES.get('image')

        try:
            pag = page.objects.create(creater=request.user, pagename=pagename, website=website,emial=emial,category=category,image=image,username=username
           )
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'")


def pageprofile(request,pageid):
    pro=page.objects.get(id=pageid)
    posts = Post.objects.filter(page_id=pageid).order_by('-date_created')
   

    return render(request,"pageprofile.html",{"pro":pro,"posts":posts,"pag":pag,
    "posts_count": posts.count(),
    })  

def pagepost(request,pk):
    pg = page.objects.get(id=pk)
    return render(request,"pagepost.html",{"pg":pg})   

def create_pagepost(request,pageid):
    pag = page.objects.get(id=pageid)
    if request.method == 'POST':
        content_text = request.POST.get('content_text')
        content_image = request.FILES.get('content_image')
        status=request.POST.get('status')
        Product_Price=request.POST.get('Product_Price')
        page_name=request.POST.get("page_name")
        if Product_Price=="":
            Product_Price=None
        
        try:
            post = Post.objects.create(creater=request.user,page_id=pag,content_text=content_text, content_image=content_image,page_name=page_name,status=status,Product_Price=Product_Price,posts_type="page_post")
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'")        



        

def cart(request):
    return render(request,"cart.html")



def checkout(request):
    return render(request,"checkout.html")



@login_required(login_url='signin')
def category(request,id):
    category = Category.objects.get(id=id)
    product = Product.objects.filter(Category_Name=category)

    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()

    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 


    grand_total =  sub_total + shipping
 
    category = Category.objects.all()
    context = {
        'pro'  : product, 
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'category' : category,
        
        
    }
    return render(request,'shop-full.html',context)



@login_required(login_url='signin')
def show_all(request):
   
    product = Product.objects.all()
    category = Category.objects.all()
    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()

    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 


    grand_total =  sub_total + shipping
 

    context = {
        'pro'  : product, 
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'category' : category,
               
    }
    return render(request,'shop-full.html',context)


def product_detail(request,id):
    product=Post.objects.filter(id=id)
    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()

    sub_total= 0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 

    grand_total =  sub_total + shipping
    context = {
        'pro'  : product, 
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
    }

    return render(request,'product-detail.html',context) 



def add_cart(request,id):
    if request.method=='POST':
        user=User.objects.get(id=request.user.id)
        product=Post.objects.get(id=id)

        qty=request.POST['qty']

        ct=Cart(user=user,product=product,product_qty=qty)
        ct.save()
        return redirect('cart')


@login_required(login_url='signin')
def cart(request):
    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()

    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 


    grand_total =  sub_total + shipping

    context = {
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        
    }


    return render(request,'cart.html',context)    

def zip(request):
    if request.method=='POST':
        zipcode=request.POST['zip']
        if Zip.objects.filter(zip_code=zipcode).exists():
            messages.info(request, 'Delery avilable')
            return redirect('cart') 
        else:
            messages.info(request, 'Delery is not avilable')
            return redirect('cart')


def remove_cart(request,id):
    crt=Cart.objects.get(id=id)
    crt.delete()
    return redirect('cart')

def remove_cart_all(request):
    crt=Cart.objects.filter(user=request.user)
    crt.delete()
    return redirect('cart')
    

@login_required(login_url='signin')
def checkout(request):
    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()
    ship = Shipping_address.objects.filter(user=request.user)

    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 


    grand_total =  sub_total + shipping
 
    orderitem = Order_Item.objects.filter(user=request.user)
    shipadd = ""
    for i in ship:
        shipadd = str(i.Full_name)+" , " + str(i.House)+" , "  + str(i.Area)+" , "+ str(i.Landmark)+" , " + str(i.Town)+" , " + str(i.State)+" , " + str(i.Zip)+" , " + str(i.Phone)



    context = {
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'ship'    :   ship,
        'orderitem'  : orderitem,
        'shipadd'  : shipadd,
        
    }

    return render(request,'checkout.html',context)   


@login_required(login_url='signin')
def shipping_address(request):
    if request.method=='POST':
        user=User.objects.get(id=request.user.id)
        if Shipping_address.objects.filter(user=request.user).exists():
            ship1 =Shipping_address.objects.get(user=request.user)
            ship1.user=user
            ship1.Full_name = request.POST['fullname']
            ship1.Phone = request.POST['phone']
            ship1.House = request.POST['house']
            ship1.Area = request.POST['area']
            ship1.Landmark = request.POST['landmark']
            ship1.Town = request.POST['town']
            ship1.State = request.POST['state']
            ship1.Zip = request.POST['zip']
            ship1.save()
            return redirect('checkout')
        else:
            ship=Shipping_address()
            ship.user=user
            ship.Full_name = request.POST['fullname']
            ship.Phone = request.POST['phone']
            ship.House = request.POST['house']
            ship.Area = request.POST['area']
            ship.Landmark = request.POST['landmark']
            ship.Town = request.POST['town']
            ship.State = request.POST['state']
            ship.Zip = request.POST['zip']
            ship.save()
            return redirect('checkout')
        


def place_order(request,id):
    if request.method=='POST':
        user=User.objects.get(id=request.user.id)

        ship=Shipping_address.objects.get(id=id)
        
        neworder= Order()

        neworder.user = user
        neworder.shipping_address = ship

        neworder.payment_mode = request.POST['payment']

        cart = Cart.objects.filter(user=request.user)
        crt_total_price = 0

        for i in cart:
            crt_total_price = crt_total_price +  i.product_qty * i.product.Product_Price 


        neworder.total_price = crt_total_price

        trackno = 'ananthu'+str(random.randint(1111111,9999999))

        while Order.objects.filter(tracking_no=trackno ) is None:
            trackno = 'ananthu'+str(random.randint(1111111,9999999))

        neworder.tracking_no = trackno
        neworder.save()
        neworderitems = Cart.objects.filter(user=request.user)
        for item in neworderitems:
            Order_Item.objects.create(
                user = request.user,
                order = neworder,
                product = item.product,
                price  = item.product.Product_Price,
                quanty = item.product_qty

            )
        Cart.objects.filter(user=request.user).delete()

        messages.success(request,"Your order has been placed successfully")

        return redirect ('my_order')
               
    

@login_required(login_url='signin')
def dashboard(request):
    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()
    ship = Shipping_address.objects.filter(user=request.user)

    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 


    grand_total =  sub_total + shipping
 
    orderitem = Order_Item.objects.filter(user=request.user)
    order_count = orderitem.count()
    shipadd = ""
    for i in ship:
        shipadd = str(i.Full_name)+" , " + str(i.House)+" , "  + str(i.Area)+" , "+ str(i.Landmark)+" , " + str(i.Town)+" , " + str(i.State)+" , " + str(i.Zip)+" , " + str(i.Phone)



    context = {
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'ship'    :   ship,
        'orderitem'  : orderitem,
        'shipadd'  : shipadd,
        'order_count' : order_count,
    }
    return render(request,'dashboard.html',context)

@login_required(login_url='signin')
def dashboard_profile(request): 
    phone=Member.objects.get(user=request.user) 
    ph=phone.phone
    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()

    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 


    grand_total =  sub_total + shipping
    orderitem = Order_Item.objects.filter(user=request.user)
    order_count = orderitem.count()
    category = Category.objects.all()
    context = {
        'pro'  : product, 
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'category' : category,
        'phone':ph,
        'order_count':order_count,
    }

    return render(request,'dash-my-profile.html',context)


@login_required(login_url='signin')
def dash_edit_profile(request):
    
    phone=Member.objects.get(user=request.user) 
    ph=phone.phone
    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()

    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 


    grand_total =  sub_total + shipping
    orderitem = Order_Item.objects.filter(user=request.user)
    order_count = orderitem.count()
    category = Category.objects.all()
    context = {
        'pro'  : product, 
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'category' : category,
        'phone':ph,
        'order_count':order_count,
    }


    return render(request,'dash-edit-profile.html',context)


@login_required(login_url='signin')
def edit(request):
    if request.method=='POST':
        user=User.objects.get(id=request.user.id)
        user.first_name=request.POST['fname']
        user.last_name=request.POST['lname']
        user.email=request.POST['email']
        pho=Member.objects.get(user=request.user)
        pho.phone=request.POST['phone']
        user.save()
        pho.save()
        return redirect('dash_edit_profile')     

@login_required(login_url='signin')
def dash_address_book(request):
    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()
    phone=Member.objects.get(user=request.user) 
    ph=phone.phone
    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 

    ship = Shipping_address.objects.filter(user=request.user)
    address = ""
    reg = ""
    for i in ship:
        address = str(i.House)+" , "  + str(i.Area)+" , "+ str(i.Landmark)+" , " + str(i.Town)+" , " + str(i.State) +" , " + str(i.Zip)
        reg = str(i.Town)+" , " + str(i.State) 

    grand_total =  sub_total + shipping
    orderitem = Order_Item.objects.filter(user=request.user)
    order_count = orderitem.count()
    category = Category.objects.all()
    context = {
        'pro'  : product, 
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'category' : category,
        'address':address,
        'reg':reg,
        'ph' :ph,

       
        'order_count':order_count,
    }
    return render(request,'dash-address-book.html',context)

@login_required(login_url='signin')
def track_order(request):

    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()

    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 


    grand_total =  sub_total + shipping
    orderitem = Order_Item.objects.filter(user=request.user)
    order_count = orderitem.count()


    context = {
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'order_count' :order_count,
        
    }
    return render(request,'dash-track-order.html',context)


def my_order(request):

    sub_total=0 
    grand_total = 0
    shipping =50
    

    grand_total =  sub_total + shipping
    orderitem = Order_Item.objects.filter(user=request.user)
    order_count = orderitem.count()
    category = Category.objects.all()
    context = {
        'pro'  : product, 
      
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'category' : category,
      
        'order_count':order_count,
        'orderitem' :orderitem,
    }
    return render(request,'dash-my-order.html',context) 




def manage_order(request,id):  
    phone=Member.objects.get(user=request.user) 
    ph=phone.phone
    crt=Cart.objects.filter(user=request.user)
    crt_count = crt.count()

    sub_total=0 
    grand_total = 0
    shipping =50
    for i in crt:
      sub_total =  sub_total + i.product_qty * i.product.Product_Price 


    grand_total =  sub_total + shipping
    orderitem = Order_Item.objects.filter(user=request.user)
    ship = Shipping_address.objects.filter(user=request.user)
    shipadd = ""
    for i in ship:
        shipadd = str(i.Full_name)+" , " + str(i.House)+" , "  + str(i.Area)+" , "+ str(i.Landmark)+" , " + str(i.Town)+" , " + str(i.State)+" , " + str(i.Zip)+" , " + str(i.Phone)
        fullname =str(i.Full_name)
    
    order_count = orderitem.count()
    category = Category.objects.all()
    manageorder = Order_Item.objects.get(id=id)
    total=0
    total=(manageorder.price *manageorder.quanty) + shipping
    context = {
        'pro'  : product, 
        'crt' : crt,
        'crt_count' : crt_count,
        'sub_total' : sub_total,
        'shipping'  : shipping,
        'grand_total' : grand_total,
        'category' : category,
        'phone':ph,
        'order_count':order_count,
        'orderitem' :orderitem,
        'manageorder' :manageorder,
        'total' :total,
        'shipadd' :shipadd,
        'fullname' : fullname,
    }
    return render(request,'dash-manage-order.html',context) 



@login_required(login_url='signin')
def admin_dash(request):
    if not request.user.is_staff:
        return redirect('signin')
    return render(request,'administrator/index.html') 

@login_required(login_url='signin')
def dash_category(request):
    category=Category.objects.all()
    context={
        'category':category,

    }
    return render(request,'administrator/category.html',context)

@login_required(login_url='signin')
def add_category(request):
    if request.method=='POST':
        cat=Category()
        cat.Category_Name = request.POST['category']
        cat.save()
        return redirect('dash_category')

@login_required(login_url='signin')
def del_category(request,id):
    cat=Category.objects.get(id=id)
    cat.delete()
    return redirect('dash_category')




@login_required(login_url='signin')
def dash_product(request):
    cat=Category.objects.all()
    context ={
        'cat' :cat,

         }

    return render(request,'administrator/products.html',context)




def edit_product(request,id):
    
    cat=Category.objects.all()
    product=Product.objects.get(id=id)
    context ={
        'cat' :cat,
        'product' :product,
         }
        
    return render(request,'administrator/edit_product.html',context)

@login_required(login_url='signin')
def edit_pro(request,id):

    if request.method=='POST':
        c = request.POST['cat']
        cat=Category.objects.get(id=c)
        pro=Product.objects.get(id=id)
       
        pro.Category_Name = cat
        
        pro.Product_Name = request.POST['pname']
        pro.Product_Description = request.POST['desp']
        pro.Product_Price = request.POST['price']
        pro.Product_Delprice = request.POST['delprice']
        if len(request.FILES) != 0:
            if len(pro.Product_Image) > 0  :
                os.remove(pro.Product_Image.path)
            pro.Product_Image = request.FILES['file']
            
        pro.save()
        return redirect('show_product')



@login_required(login_url='signin')
def show_product(request):

    product=Product.objects.all()
    context= {
        'product' : product,

    }

    return render(request,'administrator/show_product.html',context)

@login_required(login_url='signin')
def show_order(request):
    order = Order.objects.all()
    context = {
        'order' :order,
    }
    return render(request,'administrator/show_order.html',context)

@login_required(login_url='signin')
def status(request,id):
    if request.method=='POST':
        order = Order.objects.get(id=id)
        print(order)
        order.status = request.POST['st']
        order.save()
        return redirect('show_order')
          



@login_required(login_url='signin')
def show_order_product(request,id):
    items=Order_Item.objects.filter(order=id)
    order =Order.objects.get(id=id)
    context={
       'items' : items,
       'order' :order,
    }
    return render(request,'administrator/show_order_product.html',context)   



# def show_user(request):

#     users = User.objects.all()
#     return render(request,'administrator/show_users.html',{'users':users})   


def user_carts(request,id):
    us = User.objects.get(id=id)
    
    carts=Cart.objects.filter(user=us)
    context = {
        'carts' : carts,
    }
    

    return render(request,'administrator/view_carts.html',context)  


# def logout(request):
#     request.session["uid"] = ""
#     auth.logout(request)
#     return redirect('index')


def add_product(request):
     if request.method == 'POST':
        Product_Name = request.POST.get('Product_Name')
        Product_Image = request.FILES.get('Product_Image')
        Product_Price= request.POST.get('Product_Price')
        Product_Description=request.POST.get('Product_Description')
        date_created=request.POST.get('date_created')
        try:
            sel = Product.objects.create(creater=request.user, Product_Name=Product_Name, Product_Image=Product_Image,Product_Price=Product_Price,Product_Description=Product_Description,
            date_created=date_created)
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(e)
     else:
        return HttpResponse("Method must be 'POST'")


def dash(request):
    return render(request,"")    


def edit_profile(request,pk):
    profile=User.objects.get(id=pk)
    return render(request,"edit_profile.html",{"profile":profile})


def edit_pr(request,pk):
    if request.method=='POST':
        profile=User.objects.get(id=pk)
        profile.first_name=request.POST['first_name']
        profile.last_name=request.POST['last_name']
        profile.username=request.POST['username']
        profile.email=request.POST['email']
        profile.profile_pic=request.FILES.get("profile")
        profile.cover=request.FILES.get('cover')

        profile.save()
        return redirect('/')   




def edit_page(request,pk):
    profile=page.objects.get(id=pk)
    return render(request,"edit_page.html",{"profile":profile})      



def edit_pages(request,pk):
    if request.method=='POST':
        profile=page.objects.get(id=pk)
        profile.pagename=request.POST['pagename']
        profile.category=request.POST['category']
        profile.emial=request.POST['emial']
        profile.image=request.FILES.get("image")
       

        profile.save()
        return redirect('/')      

