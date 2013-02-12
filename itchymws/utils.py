import hashlib
import hmac
import base64
from time import strftime, gmtime


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
    signature = hmac.new(secret, "\n".join(request), hashlib.sha256).digest()
    return base64.b64encode(signature)


def timestamp():
    return strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
