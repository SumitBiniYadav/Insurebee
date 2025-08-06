"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('index/', views.index, name='index'),
    path('lindex/', views.lindex, name='lindex'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('fpass/', views.fpass, name='fpass'),
    path('otp/', views.otp, name='otp'),
    path('query/', views.query, name='query'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout, name='logout'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('health/', views.health, name='health'),
    path('appointment/', views.appointment, name='appointment'),
    path('life/', views.life, name='life'),
    path('auto/', views.auto, name='auto'),
    path('autoins/', views.autoins, name='autoins'),
    path('home/', views.home, name='home'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('quote/<int:pk>', views.quote, name='quote'),
    path('lifequote/<int:pk>', views.lifequote, name='lifequote'),
    path('business/', views.business, name='business'),
    path('msg/', views.msg, name='msg'),
    path('view/', views.view, name='view'),
    path('loading/', views.loading, name='loading'),
    path('upmsg/<int:pk>', views.upmsg, name='upmsg'),
    path('summary/<int:pk>', views.summary, name='summary'),
    path('call/<int:pk>/', views.call, name='call'),
    path('details/<int:pk>', views.details, name='details'),
    path('lifedetails/<int:pk>', views.lifedetails, name='lifedetails'),
    path('upload/<int:pk>', views.upload, name='upload'),
    path('thankyou/', views.thankyou, name='thankyou'),
    path('claim/', views.claim, name='claim'),
    path('download/claims/<int:user_id>/', views.generate_claims_pdf, name='download_claims_pdf'),
    path('download/payments/<int:user_id>/', views.generate_payment_history_pdf, name='download_payments_pdf'),
    path('view/<int:booking_id>',views.view,name='view'),
    path('provider/', views.provider, name='provider'),
    path('addin/', views.addin, name='addin'),
    path('noti/', views.noti, name='noti'),
    path('viewins/<int:policy_id>', views.viewins, name='viewins'),
    path('lprofile/', views.lprofile, name='lprofile'),
    path('lclaims/', views.lclaims, name='lclaims'),
    path('customers/', views.customers, name='customers'),
    path('docverifi/', views.docverifi, name='docverifi'),
    path('lclaimsview/<int:claim_id>', views.lclaimsview, name='lclaimsview'),
    path('transaction/', views.transaction, name='transaction'),
    path('psettings/', views.psettings, name='psettings'),
    path('updateins/<int:policy_id>', views.updateins, name='updateins'),
    path('deleteins/<int:policy_id>', views.deleteins, name='deleteins'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
