from base import APISection, BaseMunger


class ReportMunger(BaseMunger):
    def munge_list(self, key, value):
        if "List" in key:
            munged = {}
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

    def tabbed(self, data):
        if data is not None:
            if u'\r\n' in data:
                lines = data.split(u'\r\n')
            else:
                lines = data.split(u'\n')
            headers, data = lines[0], lines[1:]
            keys = headers.split(u'\t')
            ret = []
            for line in data:
                line = line.strip()
                if line != '':
                    ret.append(dict(zip(keys, line.split(u'\t'))))
            return ret
        return None

    def GetReport(self, **kwargs):
        """
        Arguments:
        ReportId = '0000000'
        """
        return self.tabbed(self._request(
                'GetReport',
                **kwargs
            ))
