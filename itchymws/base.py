import pprint
from urllib import quote

from requests import request

from xml2obj import fromstring
from utils import calculate_signature, timestamp

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
