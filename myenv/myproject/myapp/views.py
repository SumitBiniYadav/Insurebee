from django.shortcuts import render,redirect
from .models import *
from django.views.decorators.csrf import csrf_exempt
import random
from django.core.mail import send_mail 
from django.conf import settings
from .forms import DocumentUploadForm
import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from django.db.models import Count
from django.db.models import Sum

# Create your views for RazorPay here.
import requests
from django.http import JsonResponse,HttpResponse
import json
import razorpay
import pkg_resources

# Create views for PDF generation
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus.flowables import HRFlowable
from django.shortcuts import get_object_or_404

# Importing UTILS 
from .utils import *


#handles index function
def index(request):
    try: #try block to catch and handle exceptions 
        if request.method == 'POST':  #checks if the request is a POST request (form submission)
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            service = request.POST.get('service')
            message = request.POST.get('message')
            #create a new record in the database for quote 
            Quote.objects.create( 
                name=name,
                email=email,
                mobile=mobile,
                service=service,
                message=message,
                )
            return redirect('index')#redirect the user back to index, sort of refreshing the page after the entry is stored to database
        else:
            return render(request, 'index.html') #for get method, if the request if get in default, therefore it shows the information as default
        
    except Exception as e: #exception block to handle any kind of error
        return render(request, 'index.html')

#view function to handle signup page
@csrf_exempt
def signup(request):
    if request.method == 'POST':#checks if the request is a POST request(form submission)
        try: #try block to handle and catch exception
            user = User.objects.get(email=request.POST['email']) 
            error = "Email already exists ! Please try another one."
            return render(request, 'signup.html', {'error': error})
        except Exception as e:#exception block if the user is new and does not already exists
            if request.POST['password'] == request.POST['cpassword']: #checks if the password matches or not
                User.objects.create(#creates the object for user where it fetches the field from the form using get method and stores it to the database(mysql)
                    name=request.POST['name'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    password=request.POST['password'],
                    profile=request.FILES['profile'],
                    user_type = request.POST['usertype'],
                )
                error = "User created Successfully !" #when stores returns msg to the user/displays msg to the user 
                return render(request, 'signup.html', {'error': error})
            else:  #if the password does not match returns msg and redirects back to signup page with an empty form
                error = "Password and Confirm Password does not match !"
                return render(request, 'signup.html', {'error': error})
    else: # displays the signup page if the method is get as default
        return render(request, 'signup.html')

#view function to handle login page
def login(request):
    if request.method == 'POST':# checks the form method is POST
        try:# try block to handle errors
            user = User.objects.get(email = request.POST['email'])#fetches the email and generates the session
            if user.password == request.POST['password']:#checks the password matches the password in the database
                #generates OTP for every attempt made for login
                otp = random.randint(1001, 9999)
                #returns mail with otp to the registered email address
                subject = 'OTP for Inbee'
                message = f"""
                            Dear {user.name},

                            Your OTP for Inbee is {otp}.
                            Please enter this OTP to verify your account.
                            Regards,
                            Inbee Team
                            """
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email]

                send_mail(subject, message, email_from, recipient_list)
                request.session['otp'] = otp #generates session of otp
                request.session['email'] = user.email #generates session for email
                return render(request, 'otp.html')
            else: #if the password does not match
                error = "Invalid Password !"
                return render(request, 'login.html', {'error': error})
            
        except Exception as e: #any kind of unkown error to be displayed at the moment
            print(e)
            error = "Invalid Email !"
            return render(request, 'login.html', {'error': error})
    else:
        return render(request, 'login.html')

# Modify your otp view to ensure both values are treated as integers or strings:

def otp(request):
    if request.method == 'POST':
        try:
            # Get OTP from session and form input, ensure both are integers
            otp = int(request.session.get('otp'))  # OTP from session
            uotp = int(request.POST['uotp'])   # OTP entered by the user
            print(otp, uotp)

            if uotp == otp:
                # Correct OTP, delete OTP from session
                user = User.objects.get(email=request.session['email'])
                del request.session['otp']
                user = User.objects.get(email=request.session['email'])
                request.session['profile'] = user.profile.url
                if user.user_type == 'admin':
                    return redirect('lindex')
                else:
                    return redirect('index')
            else:
                # Incorrect OTP
                error = "Invalid OTP!"
                return render(request, 'otp.html', {'error': error})
            
        except Exception as e: #exception handling for any kind of errors
            print(e)
            error = "An error occurred. Please try again."
            return render(request, 'otp.html', {'error': error})
    else:
        return render(request, 'otp.html')


#view function to handle about page
def about(request):
    return render(request, 'about.html')    

#view function to handle logout page
def logout(request):
    del request.session['profile'] #when logout deletes the session of profile
    del request.session['email'] #when logout deletes the session of email
    return redirect('index')

#view functiion to handle appointment page
def appointment(request):
    try: #try block to handle errors
        if request.method == 'POST': #if the form method is POST 
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            service = request.POST.get('service')
            message = request.POST.get('message')

            Quote.objects.create( #create a quote object
                name=name,
                email=email,
                mobile=mobile,
                service=service,
                message=message,
            )
            # Send email to user with details of appointment
            send_mail(
                'Appointment Details',
                f'Dear {name},\n\n'
                f'You have booked an appointment for {service}.\n'
                f'Your email is {email} and your mobile number is {mobile}.\n\n'
                'Thank you for choosing us!',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return render(request, 'appointment.html', {'success': 'Appointment booked successfully!'})
        else:
            # If not a POST request, just render the appointment page
            return render(request, 'appointment.html')
    except Exception as e:
        print(e)
        return render(request, 'appointment.html', {'error': 'An error occurred while booking the appointment.'})


# view function to handle life insurnace page 
def life(request):
    try: #try block for handling error
        policies = Policy.objects.filter(policy_type='life').prefetch_related('features') #fetches policy filtered only for policy_type = 'life'
        return render(request, 'life.html', {'policies': policies}) #returns the policy so it can be displayed
    except Exception as e: #exception to print errors and debug
        print(e)
        return redirect('login')


#view function to handle health insurance page
def health(request):
    try: #try block to handle error
        policies = Policy.objects.filter(policy_type='health').prefetch_related('features') #fetches policy from the database only for policy_type = 'health'
        return render(request,'health.html', {'policies': policies}) #returns the policy so it can be displayed
    except Exception as e: #exception to print errors and debug
        print(e)
        return render(request, 'health.html') 


#view function to handle auto insurance page
def auto(request):
    if 'email' not in request.session: #returns the different page where it asks for your vehical information for future sales purpoeses
        if request.method == 'POST': 
            car_type = request.POST.get('car_type')
            car_model = request.POST.get('model')
            car_year = request.POST.get('year')
            email = request.POST.get('email')

            #creates the object and stores the datas of vehicles in the database
            CarInsurance.objects.create(
                car_type=car_type,
                car_model=car_model,
                car_year=car_year,
                email=email,
            )
            #send email to user with details of car insurance
            subject = 'Car Insurance Inquiry'
            message = f"""
            Dear User,\n
            We have received your car insurance inquiry. We will get back to you soon.\n

            Car Type: {car_type}
            Car Model: {car_model}
            Car Year: {car_year}

            Regards,
            InsureBee Company
            """
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email, ]
            send_mail(subject, message, email_from, recipient_list)
            #rrturns loading page which then returns the auto ins page which is present in js of loading
            return redirect('loading')
        
        else:
            return render(request, 'auto.html') #if the request is not POST, it returns the auto page where it asks for your vehical information for future sales purpoeses

    else: # if the user exists and have already logined it returns the auto ins page
        user = User.objects.get(email=request.session['email']) #fetches the session of login via email
        policies = Policy.objects.filter(policy_type='auto').prefetch_related('features') #fetches policy filtered on the basis of policy_type = 'auto'
        return render(request, 'autoins.html', {'policies': policies, 'user': user}) #displays the auto ins to the user with the policy in it




def loading(request):
    return render(request, 'loading.html')



def autoins(request):
    try: 
        policies = Policy.objects.filter(policy_type='auto').prefetch_related('features')
        return render(request, 'autoins.html', {'policies': policies})
    except Exception as e:
        print(e)
        return redirect('login')



def home(request):
    try:
        policies = Policy.objects.filter(policy_type='home').prefetch_related('features')
        return render(request, 'home.html', {'policies': policies})
    except Exception as e:
        print(e)
        return redirect('login')

def business(request):
    try:
        policies = Policy.objects.filter(policy_type='business').prefetch_related('features')
        return render(request, 'business.html', {'policies': policies})
    except Exception as e:
        print(e)
        return redirect('login')

def contact(request):
    return render(request, 'contact.html')

def query(request):
    return render(request, 'query.html')


def details(request,pk):
    try:
        user = User.objects.get(email=request.session['email'])
        policy = Policy.objects.prefetch_related('features').get(pk=pk)
        related_policy = Policy.objects.prefetch_related('features').exclude(pk=pk)[:3]
        return render(request, 'details.html', {'user' : user , 'policy' : policy , 'related_policy' : related_policy})
    except Exception as e:
        print(e)
        return redirect('login')
    
def lifedetails(request,pk):
    try:
        user = User.objects.get(email=request.session['email'])
        policy = Policy.objects.prefetch_related('features').get(pk=pk)
        related_policy = Policy.objects.prefetch_related('features').exclude(pk=pk)[:3]
        return render(request, 'lifedetails.html', {'user' : user , 'policy' : policy , 'related_policy' : related_policy})
    except Exception as e:
        print(e)
        return redirect('login')



def quote(request,pk):
    try:
        user = User.objects.get(email=request.session['email'])
        policy = Policy.objects.get(pk=pk)
        return render(request, 'quote.html', {'user': user, 'policy': policy})
    
    except Exception as e:
        print(e)
        return redirect('login')
    
def lifequote(request,pk):
    try:
        user = User.objects.get(email=request.session['email'])
        policy = Policy.objects.get(pk=pk)
        return render(request, 'lifequote.html', {'user': user, 'policy': policy})
    
    except Exception as e:
        print(e)
        return redirect('login')


def call(request, pk):
    email = request.session.get('email')
    if not email:
        print("No email in session")
        return redirect('login')
    
    try:
        user = User.objects.get(email=email)
        policy = Policy.objects.get(pk=pk)

        if request.method == 'POST':
            print("POST received")
            print("Form data:", request.POST)

            selected_topics = request.POST.getlist('topics')
            topics_str = ', '.join(selected_topics)
            Call.objects.create(
                user=user,
                policy=policy,
                call_method = request.POST.get('contactMethod'),
                call_date = request.POST.get('preferredDate'),
                call_time = request.POST.get('preferredTime'),
                alt_call_date = request.POST.get('alternateDate'),
                topics=topics_str,
                question = request.POST.get('questions'),
            )
            print("Call created successfully. Redirecting...")
            return redirect('msg')
        print("Request method:", request.method)
        return render(request, 'call.html', {'user': user, 'policy': policy})
    
    except Exception as e:
        print("Error in call view:", e)
        return redirect('login')



def msg(request):
    try:
        user = User.objects.get(email=request.session['email'])
        return render(request, 'msg.html', {'user' : user})
    except Exception as e:
        print(e)
        return redirect('login')


def upload(request,pk):
    user = User.objects.get(email=request.session['email'])
    policy = Policy.objects.get(pk=pk)

    if request.method == 'POST':
        print("POST received")
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = user
            document.policy = policy 
            document.save()
            return redirect('upmsg', pk=pk)

    else:
        form = DocumentUploadForm()


    return render(request, 'upload.html', {'form': form, 'user': user, 'policy': policy})


def upmsg(request,pk):
    user = User.objects.get(email=request.session['email'])
    policy = Policy.objects.get(pk=pk)
    documents = Document.objects.filter(policy=policy, user=user)
    if documents.exists():
        return render(request, 'upmsg.html', {'user': user, 'policy': policy, 'documents': documents})
    else:
        return redirect('upload',pk=pk)
  



def summary(request, pk):
    if 'email' not in request.session:
        return redirect('login')

    try:
        user = User.objects.get(email=request.session['email'])
        policy = Policy.objects.get(pk=pk)
        document = Document.objects.filter(policy=policy, user=user).first()
        net = policy.premium_amount 
        if document:
            # Prevent duplicate bookings 
            if not Booking.objects.filter(user=user, policy=policy).exists():
                booking = Booking.objects.create(
                    user=user,
                    policy=policy,
                    document=document,
                    payment_status='pending',
                    amt_paid=policy.premium_amount,
                    transaction_id=str(uuid.uuid4().hex[:10]),
                    is_active=True,
                )


                client = razorpay.Client(auth = (settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
                amount = int(float(net) * 100)  # convert Decimal to float, then to int (amount in paise)
                payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': 1})

        
                context = {
                                'payment': payment,
                                #'book':book,  # Ensure the amount is in paise
                            }
                


            else:
                booking = Booking.objects.get(user=user, policy=policy)

            # Send email
            subject = 'Booking Confirmation'
            message = f"""
                        Dear {user.name},

                        Your booking for {policy.provider} has been confirmed.

                        Booking ID: {booking.transaction_id}
                        Policy No: {policy.policyNo}
                        Amount Paid: ₹{policy.premium_amount}
                        Payment Status: {booking.payment_status}

                        Regards,  
                        Inbee Team
                        """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            return render(request, 'summary.html', {
                'user': user,
                'policy': policy,
                'documents': [document],
                'booking': booking,
            })
        else:
            return redirect('upload', pk=pk)

    except (User.DoesNotExist, Policy.DoesNotExist):
        return redirect('login')  

    

def thankyou(request):
    user = User.objects.get(email=request.session['email'])
    try:
        booking = Booking.objects.filter(user=user).order_by('-booking_date').first()  # Get the latest booking from multiple bookings
        booking.payment_status = 'completed'
        booking.save()
        
        # Send email
        subject = 'Payment Successful'
        message = f"""
                    Dear {user.name},

                    Your payment has been successfully processed.

                    Payment ID: {booking.transaction_id}
                    Amount Paid: ₹{booking.amt_paid}
                    Payment Status: {booking.payment_status}

                    Regards,  
                    Inbee Team
                    """
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        return render(request, 'thankyou.html')
    except Booking.DoesNotExist:
        return redirect('login')



def profile(request):
    try:
        user = User.objects.get(email=request.session['email'])
        documents = Document.objects.filter(user=user)
        bookings = Booking.objects.filter(user=user, payment_status='completed').order_by('-booking_date')
        claims = Claims.objects.filter(user=user).order_by('-claim_date')

        # Check if profile is incomplete 
        fields = [user.gender, user.dateofbirth, user.age, user.address]
        incomplete = any(f in [None, '', 0] for f in fields)
        # Check if documents are pending for verification and count them
        pending = documents.filter(is_verified=False).exists()
        pending_count = documents.filter(is_verified=False).count()
        # Counts the number of active policies
        policy_count = Booking.objects.filter(user=user, payment_status='completed', is_active=True).count()
        # Checks the number of claims under review
        claims_count = claims.count()

        if request.method == 'POST':
            user.name = request.POST['name']
            user.email = request.POST['email']
            user.mobile = request.POST['mobile']
            user.gender = request.POST['gender']
            user.dateofbirth = request.POST['dateofbirth']
            user.age = request.POST['age']
            user.address = request.POST['address']
            user.save()

            return render(request, 'profile.html', {
                'user': user,
                'incomplete': incomplete,
                'pending': pending_count > 0,
                'pending_count' : pending_count,
                'policy_count' : policy_count,
                'documents': documents,
                'bookings' : bookings,
                'claims' : claims,
                'claims_count' : claims_count
            })

        return render(request, 'profile.html', {
            'user': user,
            'incomplete': incomplete,
            'pending': pending_count > 0,
            'pending_count' : pending_count,
            'policy_count' : policy_count,
            'documents': documents,
            'bookings' : bookings,
            'claims' : claims,
            'claims_count' : claims_count
        })

    except Exception as e:
        print(e)
        return redirect('login')
    

def claim(request):
    try: 
        user = User.objects.get(email=request.session['email'])

        if request.method == 'POST':
            booking_id = request.POST.get('booking_id')
            claim_reason = request.POST.get('claim_reason')
            claim_amount = request.POST.get('claim_amount')
            notes = request.POST.get('notes','')
            document = request.FILES.get('document')

            booking = Booking.objects.get(id=booking_id, user=user)
            claim = Claims.objects.create(
                booking=booking,
                user=user,
                claim_reason=claim_reason,
                claim_amount=claim_amount,
                document=document,
                notes=notes,
            )
            print(claim)
            # Send email
            subject = 'Claim Request Submitted'
            message = f"""
                        Dear {user.name},

                        Your claim request has been submitted successfully.

                        Claim ID: {claim.id}
                        Booking ID: {booking.transaction_id}
                        Claim Amount: ₹{claim.claim_amount}
                        Claim Reason: {claim.claim_reason}

                        Regards,  
                        Inbee Team
                        """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            return redirect('dashboard')

        

        bookings = Booking.objects.filter(user=user, payment_status='completed').order_by('-booking_date')
        return render(request, 'claim.html', {'user': user, 'bookings': bookings})
    
    except Exception as e:
        print(e)
        return redirect('claim')
    
# download PDF code using report lab  : 
def create_letterhead():
    """Creates the InsureBee company letterhead elements"""
    elements = []
    
    # Company logo and header
    header_data = [
        ['InsureBee', ''],
        ['Protecting What Matters Most', 'Generated: ' + datetime.now().strftime('%Y-%m-%d')]
    ]
    
    header_style = TableStyle([
        ('SPAN', (0, 0), (0, 1)),
        ('ALIGN', (0, 0), (0, 1), 'LEFT'),
        ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 18),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#007bff')),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, 1), (0, 1), 10),
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica'),
        ('FONTSIZE', (1, 1), (1, 1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ])
    
    header = Table(header_data, colWidths=[4*inch, 3*inch])
    header.setStyle(header_style)
    elements.append(header)
    
    # Separator line
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#007bff'), spaceBefore=5, spaceAfter=10))
    
    return elements

def create_footer():
    """Creates the footer with contact information and legal text"""
    elements = []
    
    # Separator line
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#007bff'), spaceBefore=10, spaceAfter=5))
    
    # Contact info
    contact_data = [
        ['Contact Us:', 'Legal Disclaimer:'],
        ['InsureBee Insurance Ltd.', 'This document is an official record issued by InsureBee Insurance Ltd.'],
        ['123 Financial District, Mumbai 400001', 'All insurance policies are subject to the terms and conditions'],
        ['Phone: 0123456789', 'specified in the policy document. As per IRDAI guidelines,'],
        ['Email: info@insurebee.com', 'policyholders are advised to verify coverage details before filing claims.'],
        ['www.insurebee.com', 'InsureBee is regulated by the Insurance Regulatory and Development Authority of India.']
    ]
    
    footer_style = TableStyle([
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#007bff')),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.white),
    ])
    
    footer = Table(contact_data, colWidths=[2.5*inch, 4.5*inch])
    footer.setStyle(footer_style)
    elements.append(footer)
    
    return elements

def generate_claims_pdf(request, user_id):
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="insurebee_claims_report.pdf"'
    
    # Create the PDF document using ReportLab
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Add letterhead
    elements.extend(create_letterhead())
    
    # Title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=10,
        textColor=colors.HexColor('#007bff')
    )
    elements.append(Paragraph("Claims History Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Get user info
    user = get_object_or_404(User, id=user_id)
    
    # User info section
    user_info = [
        ['Policy Holder:', user.name],
        ['Email:', user.email],
        ['Mobile:', str(user.mobile)],
        ['Report Date:', datetime.now().strftime('%d %b %Y')],
    ]
    
    if user.address:
        user_info.append(['Address:', user.address])
    
    user_info_table = Table(user_info, colWidths=[1.5*inch, 5*inch])
    user_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(user_info_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Instructions section
    instruction_style = ParagraphStyle(
        'Instructions',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        spaceBefore=10,
        spaceAfter=10,
        backColor=colors.HexColor('#f8f9fa'),
        borderColor=colors.HexColor('#e9ecef'),
        borderWidth=1,
        borderPadding=5,
        textColor=colors.HexColor('#495057')
    )
    
    instructions = """
    <b>Important Instructions:</b>
    <ol>
        <li>This document serves as an official record of your claim history with InsureBee.</li>
        <li>Review all claims for accuracy and report any discrepancies within 15 days.</li>
        <li>For pending or rejected claims, please contact our claims department for assistance.</li>
        <li>Keep this document for your tax and insurance records.</li>
    </ol>
    """
    elements.append(Paragraph(instructions, instruction_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Claims data
    claims = Claims.objects.filter(user_id=user_id).order_by('-claim_date')
    
    if claims:
        # Header for the claims table
        claims_data = [['Date', 'Policy', 'Reason', 'Amount', 'Status']]
        
        # Add claim data rows
        for claim in claims:
            try:
                amount = float(claim.claim_amount)
                formatted_amount = f"Rs {amount:,.2f}"
            except (ValueError, TypeError):
                formatted_amount = f"Rs {claim.claim_amount}"
            
            # Truncate reason if too long and add ellipsis
            reason = claim.claim_reason[:25] + "..." if len(claim.claim_reason) > 25 else claim.claim_reason
            
            # Get policy number from booking
            policy_no = claim.booking.policy.policyNo
            
            claims_data.append([
                claim.claim_date.strftime('%d-%b-%Y'),
                str(policy_no),
                reason,
                formatted_amount,
                claim.status.replace('_', ' ').title()
            ])
        
        # Create the table style
        claims_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ])
        
        # Add alternating row colors
        for i in range(1, len(claims_data)):
            if i % 2 == 0:
                claims_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa'))
        
        # Add conditional formatting for status column
        for i in range(1, len(claims_data)):
            status = claims_data[i][4].lower()
            if 'approved' in status:
                claims_table_style.add('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#28a745'))
                claims_table_style.add('FONTNAME', (4, i), (4, i), 'Helvetica-Bold')
            elif 'rejected' in status:
                claims_table_style.add('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#dc3545'))
                claims_table_style.add('FONTNAME', (4, i), (4, i), 'Helvetica-Bold')
            elif 'under review' in status or 'pending' in status:
                claims_table_style.add('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#ffc107'))
                claims_table_style.add('FONTNAME', (4, i), (4, i), 'Helvetica-Bold')
            elif 'completed' in status:
                claims_table_style.add('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#17a2b8'))
                claims_table_style.add('FONTNAME', (4, i), (4, i), 'Helvetica-Bold')
        
        claims_table = Table(claims_data, colWidths=[1*inch, 1*inch, 2.5*inch, 1.2*inch, 1*inch])
        claims_table.setStyle(claims_table_style)
        elements.append(claims_table)
    else:
        elements.append(Paragraph("No claims found for this user.", styles['Normal']))
    
    # Summary section - if claims exist
    if claims:
        elements.append(Spacer(1, 0.3*inch))
        
        # Calculate summary data
        total_claims = claims.count()
        approved_claims = claims.filter(status='approved').count()
        rejected_claims = claims.filter(status='rejected').count()
        pending_claims = claims.filter(status__in=['under_review']).count()
        completed_claims = claims.filter(status='completed').count()
        
        # Create summary table
        summary_data = [
            ['Claims Summary', '', ''],
            ['Total Claims', str(total_claims), '100%'],
            ['Approved', str(approved_claims), f"{approved_claims/total_claims*100:.1f}%" if total_claims > 0 else "0%"],
            ['Under Review', str(pending_claims), f"{pending_claims/total_claims*100:.1f}%" if total_claims > 0 else "0%"],
            ['Rejected', str(rejected_claims), f"{rejected_claims/total_claims*100:.1f}%" if total_claims > 0 else "0%"],
            ['Completed', str(completed_claims), f"{completed_claims/total_claims*100:.1f}%" if total_claims > 0 else "0%"],
        ]
        
        summary_style = TableStyle([
            ('SPAN', (0, 0), (2, 0)),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#007bff')),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.white),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (2, 0), 12),
            ('BOTTOMPADDING', (0, 0), (2, 0), 8),
            ('TOPPADDING', (0, 0), (2, 0), 8),
            ('BACKGROUND', (0, 1), (2, 1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('GRID', (0, 1), (2, -1), 0.5, colors.HexColor('#dee2e6')),
        ])
        
        # Color-code the status rows
        summary_style.add('TEXTCOLOR', (0, 2), (0, 2), colors.HexColor('#28a745'))  # Approved - green
        summary_style.add('TEXTCOLOR', (0, 3), (0, 3), colors.HexColor('#ffc107'))  # Under Review - yellow
        summary_style.add('TEXTCOLOR', (0, 4), (0, 4), colors.HexColor('#dc3545'))  # Rejected - red
        summary_style.add('TEXTCOLOR', (0, 5), (0, 5), colors.HexColor('#17a2b8'))  # Completed - blue
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1*inch, 1*inch])
        summary_table.setStyle(summary_style)
        elements.append(summary_table)
    
    # Legal information section
    elements.append(Spacer(1, 0.5*inch))
    legal_style = ParagraphStyle(
        'Legal',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=0,
        textColor=colors.HexColor('#6c757d')
    )
    
    legal_text = """
    <b>Important Information about Indian Insurance Policies:</b>
    
    As per IRDAI (Insurance Regulatory and Development Authority of India) guidelines, all claim settlements are subject to policy terms and conditions. The Insurance Ombudsman scheme has been created to provide efficient resolution for complaints related to claim settlements.
    
    Claims must be reported within the timeframe specified in your policy document. Insurance policies are governed by the Indian Insurance Act, 1938 and various amendments thereafter.
    
    Section 45 of the Insurance Act prevents insurers from questioning policy validity after three years from the date of issuance of policy, commencement of risk, revival of policy, or rider to the policy, whichever is later.
    """
    elements.append(Paragraph(legal_text, legal_style))
    
    # Add footer
    elements.append(Spacer(1, 0.5*inch))
    elements.extend(create_footer())
    
    # Build the PDF
    doc.build(elements)
    return response

def generate_payment_history_pdf(request, user_id):
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="insurebee_payment_history.pdf"'
    
    # Create the PDF document using ReportLab
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Add letterhead
    elements.extend(create_letterhead())
    
    # Title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=10,
        textColor=colors.HexColor('#007bff')
    )
    elements.append(Paragraph("Payment History Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Get user info
    user = get_object_or_404(User, id=user_id)
    
    # User info section
    user_info = [
        ['Policy Holder:', user.name],
        ['Email:', user.email],
        ['Mobile:', str(user.mobile)],
        ['Report Date:', datetime.now().strftime('%d %b %Y')],
    ]
    
    if user.address:
        user_info.append(['Address:', user.address])
    
    user_info_table = Table(user_info, colWidths=[1.5*inch, 5*inch])
    user_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(user_info_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Instructions section
    instruction_style = ParagraphStyle(
        'Instructions',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        spaceBefore=10,
        spaceAfter=10,
        backColor=colors.HexColor('#f8f9fa'),
        borderColor=colors.HexColor('#e9ecef'),
        borderWidth=1,
        borderPadding=5,
        textColor=colors.HexColor('#495057')
    )
    
    instructions = """
    <b>Important Instructions:</b>
    <ol>
        <li>This document is proof of your premium payments to InsureBee Insurance Ltd.</li>
        <li>All payment confirmations are subject to realization of funds.</li>
        <li>Premium receipts are valid for tax deductions under Section 80D of the Income Tax Act.</li>
        <li>Please retain this document for future reference and tax filing purposes.</li>
    </ol>
    """
    elements.append(Paragraph(instructions, instruction_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Payment data
    payments = Booking.objects.filter(user_id=user_id, payment_status='completed')
    
    if payments:
        # Header for the payments table
        payments_data = [['Payment Date', 'Policy Number', 'Provider', 'Policy Type', 'Amount Paid', 'Transaction ID']]
        
        # Add payment data rows
        for booking in payments:
            try:
                amount = float(booking.amt_paid)
                formatted_amount = f"Rs {amount:,.2f}"
            except (ValueError, TypeError):
                formatted_amount = f"Rs {booking.amt_paid}"
            
            # Get policy details
            policy = booking.policy
            policy_type = dict(Policy.POLICY_TYPES).get(policy.policy_type, policy.policy_type)
            
            payments_data.append([
                booking.booking_date.strftime('%d-%b-%Y'),
                str(policy.policyNo),
                policy.provider,
                policy_type,
                formatted_amount,
                booking.transaction_id
            ])
        
        # Create the table style
        payments_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ])
        
        # Add alternating row colors
        for i in range(1, len(payments_data)):
            if i % 2 == 0:
                payments_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa'))
        
        # Make transaction ID column data bold
        for i in range(1, len(payments_data)):
            payments_table_style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')
        
        payments_table = Table(payments_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1.7*inch])
        payments_table.setStyle(payments_table_style)
        elements.append(payments_table)
        
        # Summary section
        elements.append(Spacer(1, 0.3*inch))
        
        # Calculate summary data
        total_transactions = payments.count()
        total_amount = sum(payment.amt_paid for payment in payments)
        
        # Get policy type breakdown
        policy_types = {}
        for booking in payments:
            policy_type = booking.policy.policy_type
            if policy_type in policy_types:
                policy_types[policy_type] += 1
            else:
                policy_types[policy_type] = 1
        
        # Format policy type counts
        policy_type_summary = []
        for p_type, count in policy_types.items():
            readable_type = dict(Policy.POLICY_TYPES).get(p_type, p_type)
            policy_type_summary.append(f"{readable_type}: {count}")
        policy_type_text = ", ".join(policy_type_summary)
        
        # Create summary paragraph
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            spaceBefore=10,
            spaceAfter=10,
            backColor=colors.HexColor('#e9f7ff'),
            borderColor=colors.HexColor('#b8daff'),
            borderWidth=1,
            borderPadding=10,
            textColor=colors.HexColor('#004085')
        )
        
        summary_text = f"""
        <b>Payment Summary</b><br/>
        Total Transactions: {total_transactions}<br/>
        Total Amount Paid: Rs {total_amount:,.2f}<br/>
        Policy Types: {policy_type_text}
        """
        elements.append(Paragraph(summary_text, summary_style))
        
    else:
        elements.append(Paragraph("No payment history found for this user.", styles['Normal']))
    
    # Tax and Legal information section
    elements.append(Spacer(1, 0.5*inch))
    legal_style = ParagraphStyle(
        'Legal',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=0,
        textColor=colors.HexColor('#6c757d')
    )
    
    legal_text = """
    <b>Tax and Legal Information:</b>
    
    As per Section 80D of the Income Tax Act, 1961, individuals can claim deduction for health insurance premium paid for self, spouse, dependent children and parents. The maximum deduction available is Rs 25,000 for self, spouse and dependent children, and an additional Rs 25,000 for parents (Rs 50,000 if parents are senior citizens).
    
    GST of 18% is applicable on all insurance premiums as per current regulations. Payments are subject to verification and approval by the insurance company. For any discrepancy in payment records, please contact customer service within 15 days of receipt.
    
    As per IRDAI guidelines, policy lapses due to non-payment of premium within the grace period may require medical underwriting for revival.
    """
    elements.append(Paragraph(legal_text, legal_style))
    
    # Add footer
    elements.append(Spacer(1, 0.5*inch))
    elements.extend(create_footer())
    
    # Build the PDF
    doc.build(elements)
    return response 



def view(request, booking_id):
    try: 
        user = User.objects.get(email=request.session['email'])
        booking = get_object_or_404(Booking, pk=booking_id)
        claim = Claims.objects.filter(booking=booking)
        return render(request, 'view.html', {'booking': booking , 'user': user , 'claim': claim})
    except Exception as e:
        print(e)
        return redirect('login')
    



def fpass(request):
    try:
        print("Request method:", request.method)
        if request.method == 'POST':
            email = request.POST['email']
            otp = random.randint(100000, 999999)

            # Send OTP to user's email
            subject = 'Password Reset OTP'
            message = f"""
                        Dear User,\n
                        We received a request to change the password associated with your InsureBee account.\n
                        To proceed, please use the One-Time Password (OTP) below:\n
                        
                        Your OTP : {otp}\n

                        If you did not request this, please ignore this email.\n
                        Thank you for choosing InsureBee.\n
                        Warm regards,\n
                        Team InsureBee\n
                        📧 support@insurebee.com
                        🌐 www.insurebee.com
            """ 
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list, fail_silently=False)
            
            # Store OTP in session for verification
            request.session['otp'] = otp
            request.session['email'] = email
            return redirect('verify_otp')
        
        # ✅ For GET request, show the form
        return render(request, 'fpass.html')

    except Exception as e:
        print("Error:", e)
        return redirect('login')

    
def verify_otp(request):
    try:
        if request.method == 'POST':
            email = request.session['email']
            stored_otp = request.session['otp']
            user_otp = request.POST['uotp']

            if int(user_otp) == int(stored_otp):
                # OTP is correct, redirect to password reset page
                return redirect('reset_password')
                del request.session['otp']  # Clear OTP from session after verification
            else:
                # Incorrect OTP, show error message 
                return redirect('verify_otp')
            
        else:
            return render(request, 'verify_otp.html')
    except KeyError:
        return redirect('login')
    

def reset_password(request):
    try:
        if request.method == 'POST':
            email = request.session['email']
            user = User.objects.get(email=email)

            npassword = request.POST['npassword']
            cpassword = request.POST['cpassword']
            print(npassword, cpassword)

            if npassword == cpassword:
                user.password = request.POST['npassword']
                user.save()

                del request.session['email']
                return redirect('login')
            else:
                msg = "Passwords do not match."
                return render(request, 'reset_password.html', {'msg': msg})
        else:
            return render(request, 'reset_password.html')
    except User.DoesNotExist:
        return redirect('login')
    


def lindex(request):
    user = User.objects.get(email=request.session['email'])
    policy=Policy.objects.filter(user=user) # filters the policies for the user
    total_policy = policy.count()   # counts the number of policies for the user
    activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5] # gets the last 5 activities of the user
    activity_count = activity.count() # counts the number of activities for the user

    # Get the count of active users with active policies
    active_users = User.objects.filter(policies__status='active').distinct()
    total_active_customers = active_users.count()

    # Get the Total of Premium amount Collected from the user
    total_premium_collected = sum(float(p.premium_amount) for p in policy if p.status == 'active')

    # Get the count of active policies for the user
    active_policies = policy.filter(status='active').count()

    
    return render(request, 'lindex.html' , {'user': user, 'policy': policy, 'total_policy': total_policy, 'total_active_customers': total_active_customers , 'active_policies': active_policies, 'total_premium_collected': total_premium_collected, 'activity': activity , 'activity_count': activity_count})


def addin(request):
    user = User.objects.get(email=request.session['email'])
    try:
        if request.method == 'POST':
            policy = Policy.objects.create(
                user = user,
                provider = request.POST['provider'],
                policyNo = request.POST['policyNo'],
                policy_type = request.POST['policy_type'],
                coverage_amount = request.POST['coverage_amount'],
                premium_amount = request.POST['premium_amount'],
                duration = request.POST['duration'],
                description = request.POST['description'],
                coverage_start_date = request.POST['coverage_start_date'],
                coverage_end_date = request.POST['coverage_end_date'],
                status = request.POST['status'],
                providerim = request.FILES.get('providerim'),
            )


            # Add features to the policy
            feature_titles = request.POST.getlist('feature_title[]')
            feature_details = request.POST.getlist('feature_detail[]')

            for i in range(len(feature_titles)):
                if feature_titles[i] and feature_details[i]:
                    Features.objects.create(
                        policy=policy,
                        title=feature_titles[i],
                        detail=feature_details[i]
                    )

            # Log activity {records the activity of the user}
            log_activity(
                user=user,
                action='create',
                instance= policy,
                description=f"Added policy #{request.POST['policyNo']} for provider {request.POST['provider']}."
            )


            # Send email
            subject = 'Policy Added Successfully'
            message = f"""
                        Dear {user.name},

                        Your policy has been added successfully.

                        Policy Number: {request.POST['policyNo']}
                        Provider: {request.POST['provider']}
                        Coverage Amount: ₹{request.POST['coverage_amount']}
                        Premium Amount: ₹{request.POST['premium_amount']}
                        Duration: {request.POST['duration']} months
                        Status: {request.POST['status']}

                        Regards,  
                        Inbee Team
                        """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            # Redirect to the insurance provider page
            return redirect('provider')

        else:
            # GET request, show the form
            return render(request, 'addin.html', {'user': user})
        
    except Exception as e:
        print(e)
        return redirect('login')
    


def provider(request):
    user = User.objects.get(email=request.session['email'])
    policy = Policy.objects.filter(user=user).order_by('-coverage_start_date')
    activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5] # gets the last 5 activities of the user
    activity_count = activity.count() # counts the number of activities for the user
    return render(request, 'provider.html' , {'user': user , 'policy': policy, 'activity': activity, 'activity_count': activity_count})



def viewins(request, policy_id):
    user = User.objects.get(email=request.session['email'])
    policy = get_object_or_404(Policy, pk=policy_id)
    activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5] # gets the last 5 activities of the user
    activity_count = activity.count() # counts the number of activities for the user
    features = Features.objects.filter(policy=policy) # filters the features for the policy
    return render(request, 'viewins.html', {'policy': policy , 'user': user, 'activity': activity, 'activity_count': activity_count, 'features': features})


def updateins(request, policy_id):
    user = User.objects.get(email=request.session['email'])
    policy = get_object_or_404(Policy, pk=policy_id)
    activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5] # gets the last 5 activities of the user
    activity_count = activity.count() # counts the number of activities for the user

    if request.method == 'POST':
        provider = request.POST.get('provider')
        policy_type = request.POST.get('policy_type')
        status = request.POST.get('status')
        coverage_amount = request.POST.get('coverage_amount')
        premium_amount = request.POST.get('premium_amount')
        duration = request.POST.get('duration')
        coverage_start_date = request.POST.get('coverage_start_date')
        coverage_end_date = request.POST.get('coverage_end_date')
        description = request.POST.get('description')

        #update policy

        policy.provider = provider
        policy.policy_type = policy_type
        policy.status = status
        policy.coverage_amount = coverage_amount
        policy.premium_amount = premium_amount
        policy.duration = duration
        policy.coverage_start_date = coverage_start_date
        policy.coverage_end_date = coverage_end_date
        policy.description = description

        if 'providerim' in request.FILES:
            policy.providerim = request.FILES['providerim']
        
        policy.save()

        #handles features
        feature_count = int(request.POST.get('feature_count', 0))

        #Process features 
        for i in range(1, feature_count + 1):
            title = request.POST.get(f'feature_title_{i}')
            detail = request.POST.get(f'feature_detail_{i}')
            feature_id = request.POST.get(f'feature_id{i}')

            #skip if the feature has been removed 
            if not title or not detail:
                continue

            #if it's a new feature
            if feature_id == 'new':
                Features.objects.create(
                    policy = policy, 
                    title = title,
                    detail = detail,
                )
            else:
                #update existing features
                try:
                    feature = Features.objects.get(id= feature_id)
                    feature.title = title
                    feature.detail = detail
                    feature.save()

                except Features.DoesNotExist:
                    #if the feature doesnt exist (might have deleted), create new one
                    Features.objects.create(
                        policy=policy,
                        title = title,
                        detail = detail
                    )

        #create activity log
        ActivityLog.objects.create(
            user=user,
            action='update',
            entity_type='Policy',
            entity_id=policy.id,
            description=f'Updated policy {policy.policyNo} from {policy.provider}'
        )
        

    return render(request, 'updateins.html', {'user' : user , 'policy' : policy, 'activity' : activity, 'activity_count' : activity_count})


def deleteins(request, policy_id):
    user = User.objects.get(email=request.session['email'])
    policy =get_object_or_404(Policy, pk=policy_id)
    policy.delete()
    return redirect('provider')



def noti(request):
    user = User.objects.get(email=request.session['email'])
    activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')
    activity_count = activity.count() # counts the number of activities for the user
    return render(request, 'noti.html' , {'user': user , 'activity': activity, 'activity_count': activity_count})



def lprofile(request):
    user = User.objects.get(email=request.session['email'])
    current_time = timezone.now()
    
    # Handle profile update
    if request.method == 'POST' and 'update_profile' in request.POST:
        user.name = request.POST.get('full-name')
        user.save()

        # Log the activity
        ActivityLog.objects.create(
            user=user,
            action='update',
            entity_type='User',
            entity_id=user.id,
            description='Profile updated'
        )
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('lprofile')
    
    # Handle password change
    if request.method == 'POST' and 'change_password' in request.POST:
        current_password = request.POST.get('current-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')
        
        # Verify current password
        if user.password == current_password:
            user.password = request.POST.get('new-password')
            user.save()

        else:
            messages.error(request, 'Current password is incorrect.')
            return redirect('lprofile')
    
        
        # Log the activity
        ActivityLog.objects.create(
        user=user,
        action='update',
        entity_type='User',
        entity_id=user.id,
        description='Password changed'
    )
        
        messages.success(request, 'Password changed successfully!')
        return redirect('lprofile')
    
    # Get user activity logs
    activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5]
    activity_count = activity.count()
    
    return render(request, 'lprofile.html', {
        'user': user,
        'activity': activity,
        'activity_count': activity_count,
        'current_time': current_time
    })


def lclaims(request):
    user = User.objects.get(email=request.session['email'])

    # Get all customers 
    customers = User.objects.filter(user_type='user')

    # Get all claims for the user
    claims = Claims.objects.filter(user__in=customers).order_by('-claim_date') # using user__in to filter claims for all customers 
    total_claims = claims.count() # counts the number of claims for the user
    under_review_claims = claims.filter(status='under_review').count() # counts the number of claims for the user
    approved_claims = claims.filter(status='approved').count() # counts the number of claims for the user
    total_claim_amount = sum(float(c.claim_amount) for c in claims if c.claim_amount) # calculates the total claim amount for the user

    activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5] # gets the last 5 activities of the user
    activity_count = activity.count() # counts the number of activities for the user
    return render(request, 'lclaims.html' , {'user': user , 'claims': claims, 'activity': activity, 'activity_count': activity_count, 'total_claims': total_claims, 'under_review_claims': under_review_claims, 'approved_claims': approved_claims, 'total_claim_amount': total_claim_amount})



def customers(request):
    user = User.objects.get(email=request.session['email'])
    
    # Get all customers
    customers = User.objects.filter(user_type='user')

    # Annotate each customer with their number of policies
    for customer in customers:
        customer.policy_count = Booking.objects.filter(user=customer).count()
        customer.total_premium = Booking.objects.filter(user=customer).aggregate(total=Sum('amt_paid'))['total'] or 0   


    # Activity log for the logged-in user
    activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5]
    activity_count = activity.count()
    
    return render(request, 'customers.html', {
        'user': user,
        'customers': customers,
        'activity': activity,
        'activity_count': activity_count,
        'total_customers': customers.count()
    })



def docverifi(request):
    try:
        if 'email' not in request.session:
            return redirect('lindex')
            
        user = User.objects.get(email=request.session['email'])
        
        # Check if user is admin
        if user.user_type != 'admin':
            return redirect('dashboard')
        
        # Handle document approval
        if request.method == 'POST':
            document_id = request.POST.get('document_id')
            action = request.POST.get('action')
            
            if document_id and action:
                document = Document.objects.get(id=document_id)
                
                if action == 'approve':
                    document.is_verified = True
                    document.is_rejected = False
                    document.save()
                    
                    # Create activity log for approval
                    ActivityLog.objects.create(
                        user=user,
                        action='update',
                        entity_type='Document',
                        entity_id=document.id,
                        description=f'Document #{document.id} for {document.user.name} has been approved'
                    )
                    
                elif action == 'reject':
                    reason = request.POST.get('reason', 'Documents are incomplete')
                    document.is_verified = False
                    document.is_rejected = True
                    document.save()
                    
                    # Create activity log for rejection
                    ActivityLog.objects.create(
                        user=user,
                        action='update',
                        entity_type='Document',
                        entity_id=document.id,
                        description=f'Document #{document.id} for {document.user.name} has been rejected. Reason: {reason}'
                    )

        # Get all customers
        customers = User.objects.filter(user_type='user')
        policies = Policy.objects.all()

        customer_data = []

        for customer in customers:
            cust_documents = Document.objects.filter(user=customer)
            customer_data.append({
                'customer': customer,
                'documents': cust_documents,
            })

        # Get recent activity logs
        activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5]
        activity_count = activity.count()
        
        return render(request, 'docverifi.html', {
            'user': user,
            'activity': activity,
            'activity_count': activity_count,
            'policies': policies,
            'customer_data': customer_data
        })
    
    except Exception as e:
        print(e)
        return redirect('lindex')
    



def lclaimsview(request, claim_id):
    user = User.objects.get(email=request.session['email'])
    claim = get_object_or_404(Claims, pk=claim_id)

    # Get the policy associated with the claim
    if request.method == 'POST':
        claim.status = request.POST.get('action')
        claim.notes = request.POST.get('notes')
        if request.POST.get('is_verified'):
            claim.is_verified = True
        else:
            claim.is_verified = False
        claim.save()

        # Send email notification to the user about the claim status update
        subject = 'Claim Status Update'
        message = f"""
                    Dear {claim.user.name},

                    Your claim #{claim.id} has been updated. Do check the details below:

                    New Status: {claim.status}
                    Notes: {claim.notes}

                    Regards,  
                    Inbee Team
                    """
        send_mail(subject, message, settings.EMAIL_HOST_USER, [claim.user.email]) 

        # Log the activity
        ActivityLog.objects.create(
            user=user,
            action='update',
            entity_type='Claim',
            entity_id=claim.id,
            description=f"Claim #{claim.id} status updated to {claim.status}."
        )
        
        return redirect('lclaims')  
    
    else:
        # GET request, show the claim details
        activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5]
        activity_count = activity.count()
        return render(request, 'lclaimsview.html', {
            'claim': claim,
            'user': user,
            'activity': activity,
            'activity_count': activity_count,
        })

    
def transaction(request):
    user = User.objects.get(email=request.session['email'])
    activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5] # gets the last 5 activities of the user
    activity_count = activity.count() # counts the number of activities for the user
    customers = User.objects.filter(user_type = 'user')
    transactions = Booking.objects.filter(user__in = customers)

    total_transactions = transactions.count()
    successful_transactions = transactions.filter(payment_status = 'completed').count()
    pending_transactions = transactions.filter(payment_status = 'pending').count()
    failed_transactions = transactions.filter(payment_status = 'failed').count()


    return render(request, 'transaction.html' , {'user': user , 'activity': activity, 'activity_count': activity_count, 'transactions' : transactions, 'total_transactions' : total_transactions, 'successful_transactions' : successful_transactions, 'pending_transactions' : pending_transactions, 'failed_transactions' : failed_transactions})



def psettings(request):
    return render(request, 'psettings.html')

