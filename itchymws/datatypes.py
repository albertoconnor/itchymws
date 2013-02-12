"""
MWS has several complex combinations of related data.

Here we used namedtuples as a C style struct of pod or "plain old data".

There are mungers like the MemberMunger which know how to convert these
structures to HTTP arguments MWS expects.
"""

from collections import namedtuple


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
