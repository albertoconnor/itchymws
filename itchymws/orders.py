from .base import APISection, BaseMunger


class OrderMunger(BaseMunger):
    def munge_list(self, key, value):
        munged = {}
        for index, value in enumerate(value):
            key_base = '{0}.Id.{1}'.format(key, index+1)
            munged[key_base] = value
        return munged
    pass


class Orders(APISection):
    _munger = OrderMunger()

    def _get_endpoint_name(self):
        return 'Orders'

    def ListOrders(self, **kwargs):
        """
        Arguments:
        LastUpdateAfter = "2013-03-29T19:56:50+00:00"
        MarketplaceId = 'XXXXXX'
        """
        kwargs['OrderStatus.Status.1'] = 'Shipped'
        kwargs['OrderStatus.Status.2'] = 'Unshipped'
        kwargs['OrderStatus.Status.3'] = 'PartiallyShipped'

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

