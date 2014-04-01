from base import APISection, BaseMunger


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
    	"""
    	For more on pod, see datatypes.
    	"""
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
        QueryStartDateTime = "2013-03-29T19:56:50+00:00"
        """
        return self._request(
            'ListInventorySupply',
            **kwargs
        )

    def ListInventorySupplyByNextToken(self, **kwargs):
        """
        Arguments:
        NextToken  = "IAAAAAAAAADXPS3KCMAAA0Ks4bLtAPi1kpnQmwUCwo5DwmcZ..."
        """
        return self._request(
            'ListInventorySupplyByNextToken',
            **kwargs
        )
