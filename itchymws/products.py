from base import APISection, BaseMunger


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
    
    def ListMatchingProducts(self, **kwargs):
        """
        Arguments:
        Query="Title" It can be a title, upc, etc.
        MarketplaceId="XXXXXX"
        """
        if 'MarketplaceId' not in kwargs:
            kwargs.update(dict(MarketplaceId=self.mws.default_marketplace_id))
        return self._request(
            'ListMatchingProducts',
            **kwargs
        )

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

    def GetCompetitivePricingForASIN(self, **kwargs):
        """
        Arguments:
        ASINList=["B0000B"]
        MarketplaceId="XXXXXX" # Optional
        """
        if 'MarketplaceId' not in kwargs:
            kwargs.update(dict(MarketplaceId=self.mws.default_marketplace_id))
        return self._request(
            'GetCompetitivePricingForASIN',
            **kwargs
        )

    def GetLowestOfferListingsForASIN(self, **kwargs):
        """
        Arguments:
        ASINList=["B0000B"] # See docs for other options
        ItemCondition="New" # Optional
        MarketplaceId="XXXXXX" # Optional
        """
        if 'MarketplaceId' not in kwargs:
            kwargs.update(dict(MarketplaceId=self.mws.default_marketplace_id))
        return self._request(
            'GetLowestOfferListingsForASIN',
            **kwargs
        )

