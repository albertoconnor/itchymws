import hashlib
import hmac
import base64
import re
from urllib import quote
from time import strftime, gmtime

from requests import request

from xml2obj import fromstring


class APISection(object):
    def __init__(self, mws, version):
        self.mws = mws
        self.version = version
        
    def _api_defaults(self, kwargs):
        kwargs.update({
            'AWSAccessKeyId': self.mws.mws_access_key,
            'SellerId': self.mws.merchant_id,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Timestamp': timestamp(),  
        })
        
    def _get_endpoint(self):
        return '/{0}/{1}'.format(self.__class__.__name__,self.version),
        
    def _request(self, name, **kwargs):
        params = dict(
            Version=self.version,
            Action=name,
        )
        self._api_defaults(kwargs)
        params.update(kwargs)
        params = self._munge_params(params)
        
        response = self._mws_request(
            'POST',
            self._get_endpoint(),
            params
        )
        return self._process_response(name, response)

    def _mws_request(self, method, endpoint, params=None, host='mws.amazonservices.com'):
        formatted_params = '&'.join(['='.join((k, quote(params[k], safe='-_.~')))
                                     for k in sorted(params)])
        formatted_params = formatted_params.encode('utf-8')
        request_data = [
            method,
            host,
            endpoint,
            formatted_params,
        ]
        
        params["Signature"] = calculate_signature(request_data, self.mws.mws_secret_key)
        headers = {'User-Agent': 'ItchyMWS/0.0.1 (Language=Python)'}
        response = request(method, 'https://'+host+endpoint, data=params, headers=headers)
        return response
    
    def _process_response(self, name, response):
        resp = fromstring(response.content)
        
        if not isinstance(resp, dict):
            return resp
        
        for wrap in ("{0}Response".format(name), "{0}Result".format(name)):
            if wrap in resp:
                resp = resp[wrap]
        return resp

    def _munge_params(self, kwargs):
        munged = {}
        for key in kwargs:
            # Convert NameList = [1,2,3] into NameList_Name_1=1, NameList_Name_2=2, ...
            if isinstance(kwargs[key], list) and "List" in key:
                base = "{0}.{1}.".format(key, key.replace('List', ''))
                for index, value in enumerate(kwargs[key]):
                    
                    munged['{0}{1}'.format(base, index+1)] = value
            else:
                munged[key] = kwargs[key]
                
        return munged


class Reports(APISection):
    
    def _get_endpoint(self):
        return '/'
    
    def RequestReport(self, **kwargs):
        """
        Arguments:
        ReportType = "_GET_AFN_INVENTORY_DATA_" # Plus many more options
        """
        return self._request(
                'RequestReport',
                **kwargs
            )

    def GetReportRequestList(self, **kwargs):
        """
        Arguments:
        ReportRequestIdList = ['0000000']
        """
        return self._request(
                'GetReportRequestList',
                **kwargs
            )

    def tabbed(self, data):
        lines = data.split("\r\n")
        headers, data = lines[0], lines[1:]
        ret = []
        for line in data:
            ret.append(dict(zip(headers.split('\t'), line.split('\t'))))
            
        return ret

    def GetReport(self, **kwargs):
        """
        Arguments:
        ReportId = '0000000'
        """
        return self.tabbed(self._request(
                'GetReport',
                **kwargs
            ))

class Products(APISection):

    def GetMyPriceForSKU(self, **kwargs):
        """
        Arguments:
        SellerSKUList=['741185344766']
        MarketplaceId="XXXXXX"
        
        Note if SellerSKUList contains more than 1 item, the response is a list
        of responses. 
        """
        if 'MarketplaceId' not in kwargs:
            kwargs.update(dict(MarketplaceId=self.mws.default_marketplace_id))
        return self._request(
            'GetMyPriceForSKU',
            **kwargs
        )
    
    def GetMatchingProductForId(self, **kwargs):
        """
        Arguments:
        IdType="UPC" # See docs for other options
        IdList=['667443581147']
        MarketplaceId="XXXXXX"
        
        Note if SellerSKUList contains more than 1 item, the response is a list
        of responses. 
        """
        if 'MarketplaceId' not in kwargs:
            kwargs.update(dict(MarketplaceId=self.mws.default_marketplace_id))
        return self._request(
            'GetMatchingProductForId',
            **kwargs
        )


class MWS(object):
    _api_sections = (
        (u'reports', Reports, u'2009-01-01'),
        (u'products', Products, u'2011-10-01'),
    )
    
    def __init__(self,
                 mws_access_key,
                 mws_secret_key,
                 merchant_id,
                 default_marketplace_id):
        self.mws_access_key = mws_access_key
        self.mws_secret_key = mws_secret_key
        self.merchant_id = merchant_id
        self.default_marketplace_id = default_marketplace_id
        
        self._initialize_sections()
        
    def _initialize_sections(self):
        for name, section_class, version in self._api_sections:
            setattr(self, name, section_class(self, version))
            


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

