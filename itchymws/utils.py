import hashlib
import hmac
import base64
from time import strftime, gmtime
from datetime import datetime
from dateutil import parser


def calculate_signature(request, secret):
    """
    base64 encode the hmac of the AWS_SECRET_ACCESS_KEY with the signature data.

    The siguature data looks like this:

    POST
    mws.amazonservices.com
    /Products/2011-10-01
    AWSAccessKeyId=KEY&Action=GetServiceStatus&SellerId=SELLERID&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp=2013-01-04T03%3A13%3A24Z&Version=2011-10-01

    request should be a list containing strings that represent each line above
    """
    key = "\n".join(request)
    signature = hmac.new(secret.encode('utf-8'), key, hashlib.sha256).digest()
    return base64.b64encode(signature)


def timestamp():
    return timeformat(gmtime())


def timeformat(t):
    return strftime("%Y-%m-%dT%H:%M:%SZ", t)


def parsetime(time_string):
    return parser.parse(time_string)
