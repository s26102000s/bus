from django.shortcuts import render
from decimal import Decimal
from . import Checksum
# Create your views here.
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Bus, Book
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .forms import AddBus
import datetime
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.views.decorators.cache import never_cache,cache_control
from django.contrib import auth
from django.urls import reverse
MERCHANT_KEY='1Dq%JYWUtiKwzb0M'

def home(request):
    if request.user.is_authenticated:
        return render(request, 'myapp/home.html')
    else:
        return render(request, 'myapp/signin.html')





def bus_registration(request,new={}):
    context = {}
    
    bus_list = Bus.objects.filter()
  
    if bus_list:
        return render(request, 'myapp/bus_registration.html', locals())
    else:
        context["error"] = "Sorry no buses"
        return render(request, 'myapp/bus_edit.html', context)


def bus_detail(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    return render(request, 'myapp/bus_detail.html', {'post': bus})
    
def bus_new(request):
    if request.method == "POST":
        form = AddBus(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            
            return redirect('bus_detail', pk=post.pk)
    else:
        form = AddBus()
    return render(request, 'myapp/bus_edit.html', {'form': form})
def bus_edit(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    if request.method == "POST":
        form = AddBus(request.POST, instance=bus)
        if form.is_valid():
            bus = form.save(commit=False)
            bus.save()
            return redirect('bus_detail', pk=bus.pk)
    else:
        form = AddBus(instance=bus)
    return render(request, 'myapp/bus_edit.html', {'form': form})


@login_required(login_url='signin')
def cancellings(request,pk):
    book=get_object_or_404(Book,pk=pk)
    context = {}
    id_r = book.pk
    

    try:
        book = Book.objects.get(id=id_r)
        bus = Bus.objects.get(id=book.busid)
        rem_r = bus.rem + book.nos
        
        Bus.objects.filter(id=book.busid).update(rem=rem_r)
        Book.objects.filter(id=id_r).update(status='CANCELLED')
        # a=Book.objects.filter(id=id_r)
        
        subject="Booking canceled"
        for a in Book.objects.filter(id=id_r):
            messages=f"your booking has been confirmed sucessfully with this details below email account:- {a.email} source:{a.source} destination:{a.dest} no. of seats :{a.nos} date and time of journey:{a.date} & {a.time}"
        email_from=settings.EMAIL_HOST_USER
        recipent_list=[book.email]
        send_mail(subject, messages,email_from, recipent_list)
        return redirect(seebookings)
    except Book.DoesNotExist:
        context["error"] = "Sorry You have not booked that bus"
        return render(request, 'myapp/error.html', context)

@login_required(login_url='signin')
def payment(request,pk):
    book=get_object_or_404(Book,pk=pk)
    context = {}
    id_r = book.pk
    book = Book.objects.get(id=id_r)
    bus = Bus.objects.get(id=book.busid)     
    # a=Book.objects.filter(id=id_r)
    param_dict = {

                        'MID': 'kLuwJY01618101413911',
                        'ORDER_ID': str(book.id),
                        'TXN_AMOUNT': str(book.price),
                        'CUST_ID': book.email,
                        'INDUSTRY_TYPE_ID': 'Retail',
                        'WEBSITE': 'WEBSTAGING',
                        'CHANNEL_ID': 'WEB',
                        'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest',

                }
            
    param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
    return render(request, 'myapp/paytm.html', {'param_dict': param_dict})


@login_required(login_url='signin')
def bus_bookings1(request):
    b_list = Bus.objects.filter()
    return render(request,'myapp/bus_bookings.html',locals())

@login_required(login_url='signin')
def bus_bookings(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        date_r = request.POST.get('date')

        book_list = Book.objects.filter(date=date_r,bus_name=name_r,status="BOOKED")
        book_list1 = Book.objects.filter(date=date_r,bus_name=name_r,status='RESERVED')
        if book_list:
            return render(request, 'myapp/booklist1.html', locals())
        else:
            b_list = Bus.objects.filter()
            error = "Sorry no bookings availiable on that day"
            return render(request, 'myapp/bus_bookings.html', locals())
    else:
        return render(request, 'myapp/bus_bookings.html')

@login_required(login_url='signin')
def findbus(request):
    context = {}
    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')
        bus_list = Bus.objects.filter(source=source_r, dest=dest_r, date=date_r)
        if bus_list:
            return render(request, 'myapp/list.html', locals())
        else:
            context["error"] = "Sorry no buses availiable"
            return render(request, 'myapp/findbus.html', context)
    else:
        return render(request, 'myapp/findbus.html')



@login_required(login_url='signin')
def bookings(request,pk):
    context = {}
    book=get_object_or_404(Bus,pk=pk)

    if request.method == 'POST':
        seats_r = int(request.POST.get('seats'))
        bus = Bus.objects.get(id=book.pk)
        if bus:
            if bus.rem > seats_r:
                name_r = bus.bus_name
                cost = seats_r * bus.price
                source_r = bus.source
                dest_r = bus.dest
                nos_r = Decimal(bus.nos)
                price_r = bus.price
                date_r = bus.date
                time_r = bus.time
                username_r = request.user.username
                email_r = request.user.email
                userid_r = request.user.id
                rem_r = bus.rem - seats_r
                Bus.objects.filter(id=book.pk).update(rem=rem_r)
                book = Book.objects.create(name=username_r, email=email_r, userid=userid_r, bus_name=name_r,
                                            source=source_r, busid=book.pk,
                                            dest=dest_r, price=price_r, nos=seats_r, date=date_r, time=time_r,
                                            status='RESERVED')
                print('------------book id-----------', book.id)
                # book.save()
                        # Request paytm to transfer the amount to your account after payment by user
                param_dict = {

                            'MID': 'kLuwJY01618101413911',
                            'ORDER_ID': str(book.id),
                            'TXN_AMOUNT': str(cost),
                            'CUST_ID': email_r,
                            'INDUSTRY_TYPE_ID': 'Retail',
                            'WEBSITE': 'WEBSTAGING',
                            'CHANNEL_ID': 'WEB',
                            'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest',

                    }
                
                param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
                subject="booking confirmed"
                messages=(f"your booking has been reserved please make payment with this details below email account:- {email_r}\n source:{source_r}\n destination:{dest_r}\n no. of seats :{seats_r}\n date and time of journey:{date_r} & {time_r}")
                email_from=settings.EMAIL_HOST_USER
                recipent_list=[email_r]
                send_mail(subject, messages,email_from, recipent_list)
                return render(request, 'myapp/paytm.html', {'param_dict': param_dict})
            else:
                context["error"] = "Sorry select fewer number of seats"
                return render(request, 'myapp/findbus.html', context)

    else:
        context["error"] = "Sorry this bus is not booked"
        return render(request, 'myapp/findbus.html',context)
@login_required(login_url='signin')
def printticket(request,pk):
    books=Book.objects.filter(id=pk)
    return render(request, 'myapp/ticket.html', locals())

@csrf_exempt
def handlerequest(request):
     # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            Book.objects.filter(id=response_dict['ORDERID']).update(status='BOOKED')
            books=Book.objects.filter(id=response_dict['ORDERID'])
            for book in books:
                email_r=book.email
                source_r=book.source
                date_r=book.date
                time_r=book.time
                dest_r=book.dest
                seats_r=book.nos
                subject="booking confirmed"
                messages=(f"your booking has been confirmed sucessfully with this details below email account:-  {email_r} source:{source_r} destination:{dest_r} no. of seats :{seats_r} date and time of journey:{date_r} & {time_r}")
                email_from=settings.EMAIL_HOST_USER
                recipent_list=[book.email]
                send_mail(subject, messages,email_from, recipent_list)
            print('order successful')
            return render(request, 'myapp/bookings.html', locals())
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
        return render(request, 'myapp/paymentstatus.html', {'response': response_dict})
    return render(request, 'myapp/paymentstatus.html', {'response': response_dict})
    # return render(request, 'myapp/bookings.html',{'book': book})

@login_required(login_url='signin')
def seebookings(request,new={}):
    context = {}
    id_r = request.user.id
    today = datetime.date.today()
    book_list = Book.objects.filter(userid=id_r,date__range=[today,"2022-01-01"])
    if book_list:
        return render(request, 'myapp/booklist.html', locals())
    else:
        context["error"] = "Sorry no buses booked"
        context['today'] = datetime.date.today()
        return render(request, 'myapp/findbus.html', context)

@login_required(login_url='signin')
def seeallbookings(request,new={}):
    context = {}
    # id_r = request.user.id
    today = datetime.date.today()
    book_list = Book.objects.filter(date__range=[today,"2022-01-01"])
    # book_list = Book.objects.filter(userid=id_r)
    if book_list:
        if request.user.is_superuser:
            return render(request, 'myapp/booklist.html', locals())
        else:
            context["error"] = "wrong path please try with diffrent one"
            return render(request, 'myapp/findbus.html', context)
    else:
        context["error"] = "Sorry no buses booked"
        context['today'] = datetime.date.today()
        return render(request, 'myapp/findbus.html', context)

@login_required(login_url='signin')
def seeoldbookings(request,new={}):
    context = {}
    # id_r = request.user.id
    today = datetime.date.today()
    book_list = Book.objects.filter(userid=request.user.id,date__range=["2021-01-01", today])
    # book_list = Book.objects.filter(userid=id_r)
    if book_list:
        return render(request, 'myapp/oldbooklist.html', locals())
    else:
        context["error"] = "Sorry no buses booked"
        return render(request, 'myapp/findbus.html', context)

@login_required(login_url='signin')
def seealloldbookings(request,new={}):
    context = {}
    # id_r = request.user.id
    today = datetime.date.today()
    book_list = Book.objects.filter(date__range=["2021-01-01", today])
    # book_list = Book.objects.filter(userid=id_r)
    if book_list:
        if request.user.is_superuser:
            return render(request, 'myapp/oldbooklist.html', locals())
        else:
            context["error"] = "wrong path please try with diffrent one"
            return render(request, 'myapp/findbus.html', context)
    else:
        context["error"] = "Sorry no buses booked"
        return render(request, 'myapp/findbus.html', context)
@never_cache
def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('success'))
    try:
        context = {}
        if request.method == 'POST':
            name_r = request.POST.get('name')
            email_r = request.POST.get('email')
            password_r = request.POST.get('password')
            subject="Welcome"
            messages=(f"your account has been created sucessfully with this email account:- {email_r}")
            email_from=settings.EMAIL_HOST_USER
            recipent_list=[email_r]
            # send_mail(subject, messages,email_from, [email_r])

            # messages.sucess(request,f'Your account created')
            
            user = User.objects.create_user(name_r, email_r, password_r, )
            if user:
                login(request, user)
                send_mail(subject, messages,email_from, recipent_list)
                return render(request, 'myapp/thank.html')
            else:
                context["error"] = "Provide valid credentials"
                return render(request, 'myapp/signup.html', context)
        else:
            return render(request, 'myapp/signup.html', context)
    except Exception:
        context["error"]='Email or Username Already Exist in System Try With Different Details'
        return render(request, 'myapp/signup.html', context)

def user_detail(request):
    return render(request, 'myapp/user_detail.html', {})


@never_cache
def signin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('success'))
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        user = authenticate(request, username=name_r, password=password_r)
        if user:
            login(request, user)
            # username = request.session['username']
            context["user"] = name_r
            context["id"] = request.user.id
            # return render(request, 'myapp/success.html', context)
            return success(request)
            # return HttpResponseRedirect('success')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signin.html', context)
    else:
        context["error"] = "You are not logged in"
        return render(request, 'myapp/signin.html', context)


@never_cache
def signout(request):
    context = {}
    logout(request)
    context['error'] = "You have been logged out"
    return render(request, 'myapp/signin.html', context)

@never_cache
def success(request):
    context = {}
    context['user'] = request.user
    return render(request, 'myapp/success.html', context)

def basic_bus_layout(request):
    return render(request,'myapp/basic_bus_layout.html')