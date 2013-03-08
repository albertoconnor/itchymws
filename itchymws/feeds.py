import hashlib
import base64

from base import APISection, BaseMunger


def calc_md5(string):
    """Calculates the MD5 encryption for the given string
    """
    md = hashlib.md5()
    md.update(string)
    return base64.encodestring(md.digest()).strip('\n')


class FeedsMunger(BaseMunger):
    pass


class Feeds(APISection):
    _munger = FeedsMunger()

    def _get_endpoint(self):
        return '/'
    
    def SubmitFeed(self, feed, content_type='text/xml', **kwargs):
        """
        Arguments:
        FeedType="_POST_PRODUCT_DATA_"
        PurgeAndReplace=False
        """
        md5 = calc_md5(feed) 
        return self._request(
            'SubmitFeed',
            body=feed,
            extra_headers={'Content-MD5': md5, 'Content-Type': content_type},
            **kwargs
        )

    def GetFeedSubmissionResult(self, **kwargs):
        """
        Arguments:
        FeedSubmissionId: 6686997164
        """
        return self._request(
            'GetFeedSubmissionResult',
            **kwargs
        )
