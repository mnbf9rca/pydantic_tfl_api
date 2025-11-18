import unittest
from typing import get_args

from pydantic_tfl_api import endpoints


class TestTypeHints(unittest.TestCase):
    def test_model_literal(self) -> None:
        # endpoints.TfLEndpoint is a Literal which should contain the names of sync endpoints
        # endpoints.AsyncTfLEndpoint should contain async endpoints
        # Together they should equal __all__

        sync_endpoints = list(get_args(endpoints.TfLEndpoint))
        async_endpoints = list(get_args(endpoints.AsyncTfLEndpoint))
        all_endpoints = sync_endpoints + async_endpoints

        self.assertListEqual(all_endpoints, endpoints.__all__)
