from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from accounts.serializer import UserSerializer, VerifyAccountSerializer
from accounts.email import send_otp_via_email
from accounts.utils import OTPRequestLimitDay, OTPRequestLimitSec
from accounts.models import User
from rest_framework.throttling import ScopedRateThrottle
from datetime import datetime
from django.conf import settings
# from ratelimit.decorators import RateLimitDecorator

class RegisterView(APIView):

    def post(self, request):
        try:
            data = request.data
            print(data)
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                user_data = serializer.data
                send_otp_via_email(user_data.get('email'))
                response_data = {
                    'message': 'Please check your email and verify OTP',
                    'data': user_data
                }
                return Response(data=response_data, status=HTTP_200_OK)
            
            response_data = {
                    'message': 'Something went wrong',
                    'data': serializer.errors
                }
            return Response(data=response_data, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
        return Response(data={}, status=HTTP_400_BAD_REQUEST)


class ResendOTP(APIView):
    throttle_classes = [OTPRequestLimitSec, OTPRequestLimitDay]

    def post(self, request, format = None):
        try:
            user_email = request.data['email']
            users = User.objects.filter(email=user_email)
            if not users.exists():
                return Response(data={
                    'message': "Given email is not registered! User doesn't exists"
                }, status=HTTP_401_UNAUTHORIZED)
            
            if users.first().is_verified:
                return Response(data={
                    'message': 'You are already verified user!!',
                    'data': user_email
                })

            send_otp_via_email(email=user_email)
            return Response(data={
                'message': 'OTP is re-sent successfully to your email! Please check inbox',
                'data': user_email
            })
        except Exception as e:
            print(e)
            return Response(data={
                'message': 'Something went wrong'
            }, status=HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):
    serializer_class = VerifyAccountSerializer

    def post(self, request):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                email = serializer.data.get('email')
                otp_provided = serializer.data.get('otp')
                users = User.objects.filter(email=email)
                if not users.exists():
                    response_data = {
                        'message': 'User does not exists'
                    }
                    return Response(data=response_data, status=HTTP_400_BAD_REQUEST)
                
                user = users.first()
                if user.is_verified:
                    return Response(data={
                        'message': 'You are already verified user!!',
                        'data': email
                    })
                otp_creation_time = user.otp_created_at.strftime('%Y-%m-%d %H:%M:%S')
                current_time = (datetime.now() - settings.OTP_TTL).strftime('%Y-%m-%d %H:%M:%S')
                
                if otp_creation_time < current_time:
                    return Response(data={
                        'message': 'OTP expired! Please request another OTP'
                    }, status=HTTP_408_REQUEST_TIMEOUT)

                if not user.otp == otp_provided:
                    response_data = {
                        'message': 'OTP is not valid! Please enter correct OTP'
                    }
                    return Response(data=response_data, status=HTTP_400_BAD_REQUEST)
                
                user.is_verified = True
                user.save()
                response_data = {
                    'message': 'Account verified successfully !!!',
                }
                return Response(data=response_data, status=HTTP_202_ACCEPTED)

            response_data = {
                'message': 'Something went wrong',
                'data': serializer.errors
            }
        except Exception as e:
            print(e)
            response_data = {
                'message': 'Something went wrong',
                'error': e
            }
        return Response(data=response_data, status=HTTP_400_BAD_REQUEST)