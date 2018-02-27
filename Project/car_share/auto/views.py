from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
#from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.contrib.auth.decorators import * 
from .forms import RegistrationForm

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import *
from django.utils.encoding import *
from django.utils.http import *
from django.template.loader import render_to_string
from .tokens import account_activation_token

from django.core.mail import send_mail

from .bookingform import *
from .models import *
from .managers import *
from django.contrib.auth.hashers import *
EMAIL_HOST_USER = 'whipvic@gmail.com'


def is_user(request, customer_id):
    current_customer = Customer.objects.get(id=customer_id)
    if not request.user == current_customer:
        return http.HttpResponse(404)

@login_required
def index(request):
    customer_list = Customer.objects.order_by('last_name')
    booking_list = Booking.objects.bookings();
    # output = ', '.join([str(customer) for customer in customer_list])
    return render(
        request,
        'index.html',
        context={'customer_list': customer_list, 'booking_list': booking_list},
    )

@login_required
def detail(request, customer_id):
    return HttpResponse("You're viewing customer %s" % customer_id)

@login_required
def bookings(request, customer_id):
    is_user(request, customer_id)
    booking_list = Booking.objects.bookings(Customer.objects.get(id=customer_id))
    return render(
        request,
        'bookings.html',
        context={'booking_list': booking_list},
    )

@login_required
def profile(request, customer_id):
    is_user(request, customer_id)
    current_customer = Booking.objects.bookings(Customer.objects.get(id=customer_id))
    return render(
        request,
        'profile.html',
        context={'current_customer': current_customer},
    )

@login_required
@csrf_exempt
def create_booking(request, customer_id):
    is_user(request, customer_id)
    if request.method == 'POST':
        form = CreateBookingForm(request.POST)
        if form.is_valid():

            customer = request.user
            customer.save()

            depot = form.cleaned_data['depot']
            vehicle_type = form.cleaned_data['vehicle_type']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            #return depot

            d = Depot.objects.depots(depot)
            vehicle = Vehicle.objects.vehicles(d[0], vehicle_type)

            
            v = 0            
            for item in vehicle:
                bookings = Booking.objects.bookings(depot=d[0], vehicle=item)
                if not bookings:
                    v = item
                    break
                
                for booking in bookings:
                    b_start = booking.start_time - datetime.timedelta(days=2)
                    b_end = booking.end_time + datetime.timedelta(days=2)
                    
                    if start_time > b_end or end_time < b_start:
                        v = item
                        break
                if v:
                    break

            if not v:
                return -5

            b = Booking.objects.create_booking(customer, v, d[0], start_time, end_time)
            b.save()
            print(b)
            return render(request, 'booking_created.html')

    else:
        form = CreateBookingForm()
        return render(request, 'create_booking.html', {'form':form})


@login_required
def booking_created(request, customer_id):
    is_user(request, customer_id)
    return render(
        request,
        'booking_created.html',
        context={'customer_id': customer_id},
    )

@login_required
def my_bookings(request, customer_id):
    is_user(request, customer_id)
    customer=Customer.objects.get(id=customer_id)
    booking_list = Booking.objects.bookings(Customer.objects.get(id=customer_id))
    return render(
        request,
        'my_bookings.html',
        context={'booking_list': booking_list,'customer_id':customer},
    )

@login_required
def delete_bookings(request, customer_id):
    is_user(request, customer_id)
    if request.method == 'POST':
        form = DeleteBooking(request.POST, customer=customer_id)
        if form.is_valid():
            booking = form.cleaned_data['booking']
            b = str(booking)
            customer = request.user
            b.split('\n')

            book = Booking.objects.bookings(customer, b[3])

            Booking.objects.delete_booking(customer, book[0])
            return render(
                request,
                'booking_deleted.html',
            )
    else:
        booking_list = Booking.objects.bookings(Customer.objects.get(id=customer_id))
        form = DeleteBooking(initial={'booking_list': booking_list}, customer=customer_id)
        return render(request, 'delete_booking.html', {'form': form})


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():

            password = form.cleaned_data['password1']
            hashed_password = make_password(password, None, 'md5')
            user = Customer.objects.create_customer(form.cleaned_data['email'], form.cleaned_data['first_name'], form.cleaned_data['last_name'], form.cleaned_data['email'], hashed_password)
            user.save()
            user.is_active = False

            current_site = get_current_site(request)
            subject = 'Activate Your CarShare Account'
            raw_password = form.cleaned_data.get('password1')
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            from_email = EMAIL_HOST_USER
            to_list = [user.email,EMAIL_HOST_USER]
            send_mail(subject, message,from_email,to_list,fail_silently=False, )
            
            return render(request, 'account_activation_sent.html')

    else:
            form = RegistrationForm()
    return render(request, 'registration_form.html', {'form': form})






def account_activation_sent(request):
    return render(request, 'account_activation_sent.html')




@csrf_exempt
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'account_activated.html')

    else:
        return  HttpResponse('Activation link is invalid!')

