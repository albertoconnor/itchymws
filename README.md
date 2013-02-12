ItchyMWS
--------

Yet another Amazon Markplace Web Service API wrapper inspired by https://github.com/czpython/python-amazon-mws but making a few different design/api decisions.

Status
------

Current only part of the API has been implemented including parts of Reports, Inventory and Inbound from Fulfillment, and Products.

In the coming weeks I plan to implement more of it, but it will be based on my needs. Extending it to add additional endpoints should be easy, most of the hard work is done unless a endpoint has a different usage pattern.

Usage
-----

    from itchymws import MWS
    mws = MWS(MWS_ACCESS_KEY, MWS_SECRET_KEY, MERCHANT_ID, MARKPLACE_ID)
    product = mws.products.GetMatchingProductForId(IdType="UPC", IdList=["0000000000000"])
    
You can override the per section settings like version

    mws.products.version = "2011-10-01"

Mapping
-------

Currently the doc strings in the source is the best source of documentation. The MWS api is broken into several sections including Feeds, Reports, Fulfillment and Products. Some of the sections contain multiple endpoints such as Fulfillment, in this case I haven't nested them. To access the inbound or inventory you can just call mws.inventory.function().

Functions
---------

	# Under reports.py
    mws.reports.RequestReport()
    mws.reports.GetReportRequestList()
    mws.reports.GetReport()
    # Under fulfillment.py
    mws.inbound.CreateInboundShipmentPlan()
    mws.inbound.CreateInboundShipment()
    mws.inventory.ListInventorySupply()
    # Under product.py
    mws.products.GetMyPriceForSKU()
    mws.products.GetMatchingProductForId()

