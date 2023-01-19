
from rest_framework.throttling import UserRateThrottle

class OTPRequestLimitSec(UserRateThrottle):
    scope='otp_sec'

class OTPRequestLimitDay(UserRateThrottle):
    scope='otp_day'