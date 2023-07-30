from django.shortcuts import render, redirect
from .models import *
from .forms import NewUserForm, UserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required
from .forms import *
from .utils import cookieCart, cartData, guestOrder
from django.http import JsonResponse
import datetime
import json


# Create your views here.
def index(request):
    return render(request, 'guest.html')

@login_required(login_url='/login')
def home(request):
    return render(request,'root/dashboard.html')

@unauthenticated_user
def register_view(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("root:home")
    else:
        form = NewUserForm()
    return render (request=request, template_name="root/register.html", context={"register_form":form})


@unauthenticated_user    
def login_view(request):
    form = AuthenticationForm(request, data=request.POST)
    if request.method == "POST":
         if form.is_valid():
             username = form.cleaned_data.get('username')
             password = form.cleaned_data.get('password')
             user = authenticate(username=username, password=password)
             if user is not None:
                 login(request, user)
                 messages.info(request, f"You are now logged in as {username}.")
                 return redirect("root:home")
             else:
                 messages.error(request,"Invalid username or password.")
         else:
             messages.error(request,"Invalid username or password.")
             form = AuthenticationForm()
    return render(request = request, template_name="root/login.html", context={"login_form":form})

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    messages.info(request,"Logged out successfully!")
    return redirect('root:login')


def shop_list(request):
    shops = Shop.objects.all()
    context = {'shops':shops}
    return render(request, 'root/dealers.html', context)

def itemstore(request):
    data = cartData(request)
    cartItems = data['cartItems']
        
    products = Product.objects.all()
    context = {"products":products, 'cartItems':cartItems}
    return render(request, 'root/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
                    
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'root/cart.html', context)

 
def about(request):
    data  = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products":products, 'cartItems':cartItems} 
    return render(request, 'root/about.html')



def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context = {'items':items, 'order':order, 'cartItems':cartItems, 'shipping':False}
    return render(request, 'root/checkout.html', context)

def contacts(request): 
    return render(request, 'root/contacts.html')

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action :', action)
    print('Product :',productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    # below line attaches the order to the given customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # in the below line, we r using 'get_or_create' to change the values of orderItem, if it already exists
    # so, if it already exists, we don't want to create orderItem again, we just want to change the quantity of orderItem
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action =='add':
        # by clicking up arrow, increment orderItem by 1
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        # by clicking up arrow, decrement orderItem by 1
        orderItem.quantity = (orderItem.quantity - 1)

    # save quantity of products, for an order
    orderItem.save()

    if orderItem.quantity <= 0:
        # remove the orderItem from cart, when quantity reaches 0, or below it
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

#from django.views.decorators.csrf import csrf_exempt

#@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
       
    else:
        # guestOrder function is present in utils.py
        customer, order = guestOrder(request, data)
        
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
            )

    return JsonResponse("Payment submitted...",safe=False)

  
def success(request):
    return HttpResponse('successfully uploaded')
