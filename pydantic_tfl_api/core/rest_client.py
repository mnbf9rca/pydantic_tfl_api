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

from typing import Any
from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit

from .http_client import HTTPClientBase, get_default_http_client
from .response import UnifiedResponse


class RestClient:
    """RestClient.

    :param str app_key: App key to access TfL unified API
    :param HTTPClientBase http_client: HTTP client implementation (defaults to HttpxClient)
    """

    def __init__(self, app_key: str | None = None, http_client: HTTPClientBase | None = None) -> None:
        self.app_key = {"app_key": app_key} if app_key else None
        self.http_client = http_client if http_client is not None else get_default_http_client()

    def send_request(
        self, base_url: str, location: str, params: dict[str, Any] | None = None
    ) -> UnifiedResponse:
        request_headers = self._get_request_headers()
        request_path = urljoin(base_url, location)

        # Build URL using urllib for reliability
        query_string = self._get_query_strings(params)
        url_parts = urlsplit(request_path)
        url = urlunsplit((
            url_parts.scheme,
            url_parts.netloc,
            url_parts.path,
            query_string,
            url_parts.fragment,
        ))

        response = self.http_client.get(
            url,
            headers=request_headers,
            timeout=30,
        )
        return UnifiedResponse(response)

    def _get_request_headers(self) -> dict[str, str]:
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.app_key is not None:
            request_headers |= self.app_key
        return request_headers

    def _get_query_strings(self, params: dict[str, Any] | None) -> str:
        if params is None:
            params = {}
        # drop params that are None
        return urlencode({k: v for k, v in params.items() if v is not None})
