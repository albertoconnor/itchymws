from base import APISection, BaseMunger


class Orders(APISection):
    def _get_endpoint_name(self):
        return 'Orders'

    def ListOrders(self, **kwargs):
        """
        Arguments:
        LastUpdateAfter = "2013-03-29T19:56:50+00:00"
        MarketplaceId = 'XXXXXX'
        """
        kwargs['OrderStatus.Status.1'] = 'Shipped'

        if 'MarketplaceId' not in kwargs:
            kwargs['MarketplaceId.Id.1'] = self.mws.default_marketplace_id

        return self._request(
            'ListOrders',
            **kwargs
        )

    def ListOrderItems(self, **kwargs):
        """
        Arguments:
        AmazonOrderId = '###-######..'
        """
        return self._request(
            'ListOrderItems',
            **kwargs
        )

