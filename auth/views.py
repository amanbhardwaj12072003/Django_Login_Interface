from email import message
from lib2to3.pgen2.tokenize import generate_tokens
from locale import currency
from pyexpat.errors import messages
from urllib.parse import uses_relative
from django.shortcuts import redirect, render , HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from LoginInterface import settings
from django.core.mail import send_mail , EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes , force_str
from . tokens import generate_token
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def index(request):
    # return HttpResponse("This is my home page...")
    print("This is Index Front")
    return render(request , 'auth/index.html')
@csrf_exempt
def signup(request):
    # return HttpResponse("This is my signup page...")

    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request,"This username already exist...Please try some other username...")
            return redirect('index')
        
        if User.objects.filter(email=email):
            messages.error(request,"Someone already registered with this mail account...")
            return redirect('index')
        
        if len(username)>10:
            messages.error(request,"Username is too long...")
            return redirect('index')
        
        if pass1 != pass2:
            messages.error(request,"Passwords did not matched...")
            return redirect('index')
        
        if not username.isalnum():
            messages.error(request,"Username should be Alpha-Numeric")
            return redirect('index')


        myuser = User.objects.create_user(username , email , pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        messages.success(request , "Your account has been successfully created...We have sent you an confirmation email, Kindly confirm your account to complete the registration process...")

        # Code for sending welcome Email

        subject = "Welcome to my Web-Portal..."

        message = "Hello "+myuser.first_name+"!! \n"+"Welcome to my Web-Portal and thanks for visiting my portfolio ,We had sent you a confirmation link on your registered email account , kindly confirm your account to complete the registration... \n\n Thanking You \n Aman Bhardwaj"

        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)


        # Code for sending confirmation link

        current_site = get_current_site(request)
        email_subject = "Confirmation mail to complete registration process at My-Portal"
        message2 = render_to_string("email_confirmation.html" , {
            'name' : myuser.first_name,
            'domain' : current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generate_token.make_token(myuser)

        })

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email]
        )

        email.fail_silently = True
        email.send()
        # send_mail(email_subject,message2,from_email,to_list,fail_silently=True)


        return redirect('signin')
    return render(request , 'auth/signup.html')

@csrf_exempt
def signin(request):
    # return HttpResponse("This is my signin page...")

    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username , password = pass1)
        if user is not None:
            login(request , user)
            fname = user.first_name
            return render(request , "auth/index.html" , {'fname':fname})
        else:
            messages.error(request , "You entered the invalid credentials ")
            return redirect('index')

    return render(request , 'auth/signin.html')
@csrf_exempt
def signout(request):
    logout(request)
    messages.success(request , "Logged out successfully...")
    return redirect('index')
@csrf_exempt
def activate(request , uidb64 , token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError , ValueError , OverflowError , User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_token.check_token(myuser , token):
        myuser.is_active = True
        myuser.save()
        login(request , myuser)
        return redirect('index')
    
    else:
        return render(request , 'activation_failed.html')

    
    
    


