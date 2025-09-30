import unittest
from typing import get_args

from pydantic_tfl_api import endpoints


class TestTypeHints(unittest.TestCase):
    def test_model_literal(self) -> None:
        # endpoints.TfLEndpoint is a Literal which should contain the names of all the endpoints in the package
        # this test checks that the names are correct, none are missing.
        # we do this by comparing the __all__ attribute of the endpoints module with the literal

        self.assertListEqual(list(get_args(endpoints.TfLEndpoint)), endpoints.__all__)
