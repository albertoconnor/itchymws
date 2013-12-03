import csv
from io import BytesIO
from base import APISection, BaseMunger


stupid = u'''\ufeff"Includes Amazon Marketplace, Fulfillment by Amazon (FBA), and Amazon Webstore transactions"\n"All amounts in USD, unless specified"\n"Definitions:"\n"Sales tax collected: Includes sales tax collected from buyers for product sales, shipping, and gift wrap."\n"Selling fees: Includes variable closing fees, per-item fees, and referral fees."\n"Other transaction fees: Includes shipping chargebacks, shipping holdbacks, and sales tax collection fees."\n"Other: Includes non-order transaction amounts. For more details, see the ""Type"" and ""Description"" columns for each order ID."\n'''


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class ReportMunger(BaseMunger):
    def munge_list(self, key, value):
        if "List" in key:
            munged = {}
            if "Type" in key:
                base = "{0}.{1}.".format(key, 'Type')
            else:
                base = "{0}.{1}.".format(key, 'Id')
            for index, value in enumerate(value):
                munged['{0}{1}'.format(base, index+1)] = value
            return munged
        else:
            return {key: value}


class Reports(APISection):
    _munger = ReportMunger()

    def _get_endpoint(self):
        return '/'

    def _process_response(self, name, response):
        if name == "GetReport":
            return response.text
        else:
            return super(Reports, self)._process_response(name, response)

    def RequestReport(self, **kwargs):
        """
        Arguments:
        ReportType = "_GET_AFN_INVENTORY_DATA_" # Plus more options
        StartDate = "2013-03-29T19:56:50+00:00"
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

    def csv(self, data):

        def UnicodeDictReader(utf8_data, **kwargs):
            csv_reader = csv.DictReader(utf8_data, **kwargs)
            for row in csv_reader:
                yield dict([(key, unicode(value, 'utf-8')) for key, value in row.iteritems()])

        if data is not None:

            #Hack for financial tractions by date
            if data.startswith(u'\ufeff"Includes Amazon Marketplace, Fulfillment by Amazon (FBA),'):
                data = data.replace(stupid, u'')

            f = BytesIO(data.encode('utf-8'))
            return list(UnicodeDictReader(f))

        return None

    def tabbed(self, data):
        if data is not None:
            if u'\r\n' in data:
                lines = data.split(u'\r\n')
            else:
                lines = data.split(u'\n')

            delimiter = u'\t'

            headers, data = lines[0], lines[1:]
            keys = headers.split(delimiter)
            ret = []
            for line in data:
                line = line.strip()
                if line != '':
                    ret.append(dict(zip(keys, line.split(delimiter))))
            return ret
        return None

    def GetReport(self, hint=None, **kwargs):
        """
        Arguments:
        ReportId = '0000000'
        """

        if hint == u'csv':
            return self.csv(self._request(
                'GetReport',
                **kwargs
            ))

        return self.tabbed(self._request(
            'GetReport',
            **kwargs
        ))
