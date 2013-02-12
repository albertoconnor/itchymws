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
    
    def RequestReport(self, **kwargs):
        """
        Arguments:
        ReportType = "_GET_AFN_INVENTORY_DATA_" # Plus many more options
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
        lines = data.split("\r\n")
        headers, data = lines[0], lines[1:]
        ret = []
        for line in data:
            ret.append(dict(zip(headers.split('\t'), line.split('\t'))))
            
        return ret

    def GetReport(self, **kwargs):
        """
        Arguments:
        ReportId = '0000000'
        """
        return self.tabbed(self._request(
                'GetReport',
                **kwargs
            ))
