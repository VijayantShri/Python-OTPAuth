from django.urls import path
from accounts.views import RegisterView, VerifyOTP, ResendOTP

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verify-otp/', VerifyOTP.as_view()),
    path('resend-otp/', ResendOTP.as_view()),
]
