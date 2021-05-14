from .feeds import Feeds
from .reports import Reports
from .fulfillment import Inbound, Inventory
from .products import Products
from .orders import Orders


class MWS(object):
    _api_sections = (
        (u'feeds', Feeds, u'2009-01-01'),
        (u'reports', Reports, u'2009-01-01'),
        (u'inbound', Inbound, u'2010-10-01'),
        (u'inventory', Inventory, u'2010-10-01'),
        (u'orders', Orders, u'2013-09-01'),
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
