from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Items, Order,User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import CustomerProfile,PhoneNumbers,Addresses


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        mail = request.POST.get('email')
        passwd = request.POST.get('password')

        try:
            user = User.objects.get(email = mail)
        except:
            messages.error(request, "Invalid user!")

        user = authenticate(request,email = mail, password = passwd)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, "Incorrect username or password")


    return render(request, "base/login_register.html")

def logoutUser(request):
    logout(request)
    return redirect('home')


def registerCustomer(request):
    form = CustomerSignupForm()
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        pref = request.POST.get("selected_pref")
        num = request.POST.get("phonenumber")
        address = request.POST.get("address")
        area = request.POST.get("area")
        if form.is_valid():
            user = form.save(commit=False)
            user.name = user.name.lower()
            user.save()
            c = CustomerProfile.objects.get(user = user)
            c.preference = CustomerProfile.Preferences.VEG if pref=='veg' else CustomerProfile.Preferences.NONVEG
            c.save()
            Addresses.objects.create(user = user,address = address, area = area)
            PhoneNumbers.objects.create(user = user, phone_number = num)
            print(user.role)
            print(user.phonenumbers_set)
            print(user.addresses_set)
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"An error occured!")
    return render(request,'base/register_customer.html',{'form':form})

def registerOwner(request):
    form = OwnerSignupForm()
    res_form = RestaurantCreationForm()
    if request.method == 'POST':
        num = request.POST.get("phonenumber")
        address = request.POST.get("address")
        area = request.POST.get("area")
        form = OwnerSignupForm(request.POST)
        res_form = RestaurantCreationForm(request.POST,request.FILES)
        if form.is_valid() and res_form.is_valid():
            user = form.save(commit=False)
            user.name = user.name.lower()
            user.save()
            res = res_form.save(commit=False)
            res.owner = user
            res.save()
            Addresses.objects.create(user = user,address = address, area = area)
            PhoneNumbers.objects.create(user = user, phone_number = num)
            print(user.role)
            print(user.phonenumbers_set)
            print(user.addresses_set)
            print(user.role)
            print(res.name1)
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"An error occured!")
    return render(request,'base/register_owner.html',{'form':form, 'res' : res_form})


def registerDeliverer(request):
    form = DelivererSignupForm()
    if request.method == 'POST':
        form = DelivererSignupForm(request.POST)
        area = request.POST.get("area")
        if form.is_valid():
            user = form.save(commit=False)
            user.name = user.name.lower()
            user.save()
            Addresses.objects.create(user = user,address = "", area = area)
            print(user.role)
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"An error occured!")
    return render(request,'base/register_deliverer.html',{'form':form})


def home(request):
    return render(request, "base/home.html")


@login_required(login_url='login')
def order(request,pk):
    items = Items.objects.all().filter(restaurant_id = pk, quantity__gt = 0)
    context = {"items": items}

    if request.method == "POST":
        item_list = request.POST.getlist("item_list")
        qty_list = request.POST.getlist("quantity_list")
        print("Items :", item_list)
        qty_list = [x for x in qty_list if x != "" and x != "0"]
        print(qty_list)
        amt = 0
        # bill=[
        #     {'name': 0, 'price':0}, ...
        # ]
        if len(item_list) != len(qty_list):
            messages.error(request, "Invalid selection. Enter again")
            return render(request, "base/order.html", context=context)

        bill = []
        loop = 0
        for key in item_list:
            if int(qty_list[loop])<0:
                messages.error(request,"Negative values not permitted")
                return render(request,"base/order.html",context)
            record = Items.objects.get(id=key)
            bill_item = dict()
            print(record.name, record.price, qty_list[loop])
            bill_item['id'] = key
            bill_item["name"] = record.name
            bill_item["price"] = int(record.price)
            bill_item["qty"] = int(qty_list[loop])
            bill_item['rec'] = record
            bill.append(bill_item)
            print(bill_item)
            amt += ( record.price * int(qty_list[loop]) )
            loop += 1

        if amt == 0:
            messages.error(request, "No items have been chosen. Try again!")
            return render(request, "base/order.html", context=context)

        for entity in bill:
            # i = Items.objects.get(id  = entity['id'])
            if entity['rec'].quantity < entity['qty']:
                messages.error(request, "Choose "+ str( - entity['rec'].quantity + entity['qty']) + " less of " + entity['name'] +" and try again!")
                return render(request, "base/order.html", context=context)
            else:
                entity['rec'].quantity -= entity['qty']
                entity['rec'].save()


        order = Order.objects.create( customer = request.user,amount=amt)
        for i in bill:
                OrderItem.objects.create(order = order, items = i['rec'], quantity =i['qty'] )

        print(bill)
        return render(request, "base/order_confirm.html", {"bill": bill, "amount": amt, 'order' : order,'temp': bill[0]['rec'].restaurant_id})

    return render(request, "base/order.html", context=context)


def selectRole(request):
    if request.method == 'POST':
        selected_role = request.POST.get('selected_role')
        print(selected_role)
        if selected_role=='customer':
            return redirect('register_customer')
            #return registerCustomer(request)
        elif selected_role == 'owner':
            return redirect('register_owner')
            #return registerOwner(request)
        elif selected_role == 'deliverer':
            return redirect('register_deliverer')
            #return registerCustomer(request)
        else:
            messages.error(request, "Please select a role")
            return render(request, 'base/role_selection.html')
    return render(request,"base/role_selection.html")


def displayRestaurants(request):
    print(request.user.__dir__())
    r = Restaurant.objects.all().filter(owner__addresses__area= request.user.addresses.area)

    return render(request, 'base/restaurants.html', {'restaurant' : r})


# def customerHome(request):
#     context = {}
#     return render(request, "base/customer_home.html", context=context)

# def ownerHome(request):
#     context = {}
#     return render(request, "base/owner_home.html", context=context)

# def delivererHome(request):
#     context = {}
#     return render(request, "base/deliverer_home.html", context=context)

def stats(request):
    return HttpResponse("STATISTICS for " + request.user.name)

def createItem(request):
    form = ItemForm()

    if request.method == 'POST':
        form = ItemForm(request.POST,request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            print(request.__dir__())
            item.restaurant = request.user.restaurant
            item.save()
            return redirect('home')
    return render(request, "base/item_create.html",{'form': form})

def deleteOrder(request,pk):

    orderitem = OrderItem.objects.all().filter(order_id = pk).select_related('items')
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        for x in orderitem:
            i = Items.objects.get(id = x.items_id)
            i.quantity += x.quantity
            print(x.quantity)
            print(i, i.quantity)
            i.save()
        order.delete()

        return redirect('restaurant-list')
    return render(request,'base/delete_order.html',{"obj" : order,"rel" : orderitem})
