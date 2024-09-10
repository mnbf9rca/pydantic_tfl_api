# from https://github.com/dhilmathy/TfL-python-api
# MIT License

# Copyright (c) 2018 Mathivanan Palanisamy

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
# try:
from urllib.parse import urlencode, urljoin
from requests import Response
# except ImportError:
#     from urllib import urlencode
# from config import base_url

class RestClient():
    """RestClient.

    :param str app_key: App key to access TfL unified API
    """

    def __init__(self, app_key: str = None):
        self.app_key = {"app_key": app_key} if app_key else None

    def send_request(self, base_url: str, location: str, params=None) -> Response:
        request_headers = self._get_request_headers()
        request_path = urljoin(base_url, location)

        return requests.get(request_path + "?" + self._get_query_strings(params), headers=request_headers)

    def _get_request_headers(self):
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.app_key is not None:
            request_headers.update(self.app_key)
        return request_headers

    def _get_query_strings(self, params):
        if params is None:
            params = {}
        # drop params that are None
        return urlencode({k: v for k, v in params.items() if v is not None})
    
