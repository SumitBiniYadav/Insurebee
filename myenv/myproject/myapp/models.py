from django.db import models
from django.utils.timezone import now

# Create your models here.

class User(models.Model):

    USER_TYPES = [
        ('admin' , 'Admin'),
        ('user' , 'User'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.BigIntegerField()
    password = models.CharField(max_length=100)
    profile = models.ImageField(default="")
    dateofbirth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='user')
    is_active = models.BooleanField(default=True)  # To track if the user is active or not
    created_at = models.DateTimeField(default=now)  # To track when the user was created


    def __str__(self): 
        return self.name
    

class Policy(models.Model):

    POLICY_TYPES = [
        ('life' , 'Life Insurance'),
        ('health' , 'Health Insurance'),
        ('auto' , 'Auto Insurance'),
        ('home' , 'Home Insurance'),
        ('business' , 'Business Insurance'),
    ]

    STATUS = [
        ('active' , 'Active'),
        ('inactive' , 'Inactive'),
        ('expired' , 'Expired'),
        ('pending' , 'Pending'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='policies', default=2)
    provider = models.CharField(max_length=100)
    policyNo = models.BigIntegerField(unique=True)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in years")
    description = models.TextField()
    coverage_start_date = models.DateField()
    coverage_end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS, default='active')
    providerim = models.ImageField(default="")

    def __str__(self):
        return f"{self.provider} - {self.policyNo}"
    


class Features(models.Model):
    policy = models.ForeignKey(Policy, related_name='features', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    detail = models.TextField()

    def __str__(self):
        return f"{self.policy.policyNo} - {self.title}" 


class Call(models.Model):
    PREF_TIME = [
        ('9-12' , '9:00 AM - 12:00 PM'),
        ('12-3' , '12:00 PM - 3:00 PM'),
        ('3-6' , '3:00 PM - 6:00 PM'),

    ]

    CALL_METHOD = [
        ('phone call' , 'Phone Call'),
        ('video call' , 'Video Call'),
    ]

    policy = models.ForeignKey(Policy, related_name='calls', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    call_date = models.DateField()
    alt_call_date = models.DateField()
    call_time = models.CharField(max_length=10, choices=PREF_TIME)
    call_method = models.CharField(max_length=20, default='phone call',choices=CALL_METHOD)
    topics = models.CharField(max_length=255, blank=True, default='')
    question = models.TextField(default="What is covered under this insurance policy?")

    def __str__(self):
        return f"{self.user.name} - {self.policy.policyNo} - {self.call_date}"


class Document(models.Model):
    policy = models.ForeignKey(Policy, related_name='documents', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    identity = models.FileField(upload_to='documents/identity/')
    address = models.FileField(upload_to='documents/address/')
    income = models.FileField(upload_to='documents/income/')
    medical_history = models.FileField(upload_to='documents/medical/', blank=True, null=True)
    prev_insurance = models.FileField(upload_to='documents/previous_insurance/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'Document set for {self.user.name} - Policy #{self.policy.policyNo}'


class Booking(models.Model):

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='bookings')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField(auto_now_add=True)
    amt_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)  # if the policy is still in effect
    notes = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.user.name} - {self.policy.policyNo} - {self.payment_status}"



class Claims(models.Model):
    
    CLAIM_STATUS = [
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='claims')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    claim_reason = models.TextField()
    claim_date = models.DateField(auto_now_add=True)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)
    document = models.FileField(upload_to='claims/documents/')
    status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='under_review')
    notes = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.name} - {self.booking.policy.policyNo} - {self.claim_date} - {self.status}"
    



class CarInsurance(models.Model):
    CAR_TYPES = [
        ('sedan' , 'Sedan'),
        ('suv' , 'SUV'),
        ('hatchback' , 'Hatchback'),
        ('luxary' , 'Luxury'),
    ]

    car_type = models.CharField(max_length=20, choices=CAR_TYPES)
    car_model = models.CharField(max_length=100)
    car_year = models.IntegerField()
    email = models.EmailField(default="default@example.com")


    def __str__(self):
        return f"{self.email} - {self.car_model} - {self.car_year}"
    


class Quote(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.BigIntegerField()
    service = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.service} - {self.created_at}"
    


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)  # e.g., 'Policy', 'Claim', etc.
    entity_id = models.IntegerField()  # ID of the entity being acted upon
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # To track if the log has been read by the user

    def __str__(self):
        return f"{self.user.name} - {self.action} - {self.entity_type} - {self.entity_id} - {self.timestamp}"