ItchyMWS
--------

Yet another Amazon Markplace Web Service API wrapper inspired by https://github.com/czpython/python-amazon-mws but making a few different design/api decisions.

Status
------

Currently very little of the API has been implemented, only a few Reports endpoints and two Products endpoints.

In the coming weeks I plan to implement most of it, but it will be based on my needs. Extending it to add additional endpoints should be easy, most of the hard work is done unless a endpoint has a different usage pattern.

Usage
-----

    from itchymws import MWS
    mws = MWS(MWS_ACCESS_KEY, MWS_SECRET_KEY, MERCHANT_ID, MARKPLACE_ID)
    product = mws.products.GetMatchingProductForId(IdType="UPC", IdList=["0000000000000"])
    
You can override the per section settings like version

    mws.product.version = "2011-10-01"
