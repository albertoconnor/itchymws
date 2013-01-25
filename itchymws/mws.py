import hashlib
import hmac
import base64
import re
import pprint
from urllib import quote
from time import strftime, gmtime
from collections import namedtuple

from requests import request

from xml2obj import fromstring


class BaseMunger(object):
    """
    Different MWS endpoints treat lists and such differently.
    
    Methods named munge_<typename>(self,key,value) are called per value
    if present. They must return dictionaries, either empty or of munged
    values.
    
    Example:
    def munge_list(self, key, value):
    
    This may return a dictionary with an entry for every value in the list
    """
    
    def munge(self, parameters):
        munged = {}
        for key in parameters:
            type_name = type(parameters[key]).__name__
            munger_name = 'munge_{0}'.format(type_name)
            try:
                munged.update(self.__getattribute__(munger_name)(key, parameters[key]))
            except AttributeError:
                munged[key.replace("_", ".")] = parameters[key]
        return munged


class APISection(object):
    _munger = BaseMunger()
    
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
        
    def _get_endpoint_name(self):
        return self.__class__.__name__
        
    def _get_endpoint(self):
        return '/{0}/{1}'.format(self._get_endpoint_name(),self.version)
        
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
        formatted_params = '&'.join(['='.join((k, quote(unicode(params[k]), safe='-_.~')))
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
        # pprint.pprint(params)
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
        return self._munger.munge(kwargs)

class MemberMunger(BaseMunger):
    def munge_list(self, key, value):
        munged = {}
        for index, value in enumerate(value):
            key_base = '{0}.member.{1}'.format(key, index+1)
            if isinstance(value, dict):
                for value_key in value:
                    munged['{0}.{1}'.format(key_base, value_key)] = value[value_key]
            else:
                munged[key_base] = value
        return munged
    
    def munge_pod(self, key, value):
        pairs = recursive_munge_pod(key, value, "")
        return dict(pairs)
    
def recursive_munge_pod(key, value, base=""):
    if not type(value).__name__ == 'pod':
        if base != "":
            return [(".".join((base,key)), value)]
        else:
            return [(key, value)]
    else:
        ret = []
        value_dict = value._asdict()
        if base != "":
                key = ".".join((base,key))
        for value_key in value_dict:
            ret += recursive_munge_pod(value_key, value_dict[value_key], key)
        return ret
            
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
    
ShipFromAddress = namedtuple('pod', # Plain old data
                             ['Name',
                              'AddressLine1',
                              'AddressLine2',
                              'City',
                              'StateOrProvinceCode',
                              'PostalCode',
                              'CountryCode'])

InboundShipmentHeader = namedtuple('pod', # Plain old data
                                    ['ShipmentName',
                                     'ShipFromAddress',
                                     'DestinationFulfillmentCenterId',
                                     'ShipmentStatus',
                                     'LabelPrepPreference',])
    
class  Inbound(APISection):
    _munger = MemberMunger()
    
    def _get_endpoint_name(self):
        return 'FulfillmentInboundShipment'
    
    def CreateInboundShipmentPlan(self, **kwargs):
        """
        Arguments:
        ShipFromAddress = ShipFromAddress()
        LabelPrepPreference = 'SELLER_LABEL' #Optioal
        InboundShipmentPlanRequestItems = [{SellerSKU:00000000, Quantity:3}]
        """
        if 'LabelPrePreference' not in kwargs:
            kwargs['LabelPrePreference'] = 'SELLER_LABEL'
            
        return self._request(
            'CreateInboundShipmentPlan',
            **kwargs
        )
    
    def CreateInboundShipment(self, **kwargs):
        """
        Arguments:
        ShipmentId=XXXXXXX
        InboundShipmentHeader = InboundShipmentHeader()
        InboundShipmentItems = [{SellerSKU:00000000, Quantity:3}]
        """
            
        return self._request(
            'CreateInboundShipment',
            **kwargs
        )
    
    
class Inventory(APISection):
    _munger = MemberMunger()
    
    def _get_endpoint_name(self):
        return 'FulfillmentInventory'
        
    def ListInventorySupply(self, **kwargs):
        """
        Arguments:
        SellerSkus = ["000000000"]
        """
        return self._request(
                'ListInventorySupply',
                **kwargs
            )


class ProductMunger(BaseMunger):
    def munge_list(self, key, value):
        if "List" in key:
            munged = {}
            base = "{0}.{1}.".format(key, key.replace('List', ''))
            for index, value in enumerate(value):
                munged['{0}{1}'.format(base, index+1)] = value
            return munged
        else:
            return {key: value}


class Products(APISection):
    _munger = ProductMunger()
    
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
        (u'inbound', Inbound, u'2010-10-01'),
        (u'inventory', Inventory, u'2010-10-01'),
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

