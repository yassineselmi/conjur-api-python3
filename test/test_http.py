import unittest

from enum import auto, Enum
from unittest.mock import patch

import requests

from conjur_api_python3.endpoints import ConjurEndpoint
from conjur_api_python3.http import HttpVerb, invoke_endpoint


class HttpVerbTest(unittest.TestCase):
    def test_http_verb_has_all_the_verbs_expected(self):
        self.assertTrue(HttpVerb.GET)
        self.assertTrue(HttpVerb.PUT)
        self.assertTrue(HttpVerb.POST)
        self.assertTrue(HttpVerb.DELETE)


class HttpInvokeEndpointTest(unittest.TestCase):
    class MockEndpoint(Enum):
        NO_PARAMS = "no/params"
        WITH_URL = "{url}/no/params"

    @patch.object(requests, 'get')
    def test_invoke_endpoint_can_invoke_http_client(self, mock_get):
        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, {})

        mock_get.assert_called_once_with('no/params', auth=None, headers={}, verify=True)

    @patch.object(requests, 'get')
    def test_invoke_endpoint_can_handle_unset_params(self, mock_get):
        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, None)

        mock_get.assert_called_once_with('no/params', auth=None, headers={}, verify=True)

    @patch.object(requests, 'get')
    @patch.object(requests, 'post')
    @patch.object(requests, 'delete')
    def test_invoke_endpoint_uses_http_verb_for_method_name(self, mock_delete, mock_post, mock_get):
        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, {})
        mock_get.assert_called_once_with('no/params', auth=None, headers={}, verify=True)

        invoke_endpoint(HttpVerb.POST, self.MockEndpoint.NO_PARAMS, {})
        mock_post.assert_called_once_with('no/params', auth=None, headers={}, verify=True)

        invoke_endpoint(HttpVerb.DELETE, self.MockEndpoint.NO_PARAMS, {})
        mock_delete.assert_called_once_with('no/params', auth=None, headers={}, verify=True)

    @patch.object(requests, 'get')
    def test_invoke_endpoint_generates_url_from_endpoint_object(self, mock_get):
        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.WITH_URL, {'url': 'http://host'})

        mock_get.assert_called_once_with('http://host/no/params', auth=None, headers={}, verify=True)

    @patch.object(requests, 'get')
    def test_invoke_endpoint_attaches_api_token_header_if_present_in_params(self, mock_get):
        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, None, api_token='token')

        mock_get.assert_called_once_with('no/params', auth=None, verify=True,
                                         headers={'Authorization': 'Token token="dG9rZW4="'})

    @patch.object(requests, 'get')
    def test_invoke_endpoint_verifies_ssl_by_default(self, mock_get):
        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, None)

        mock_get.assert_called_once_with('no/params', auth=None, verify=True, headers={})

    @patch.object(requests, 'get')
    def test_invoke_endpoint_passes_ssl_verify_param_to_http_client(self, mock_get):
        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, None, ssl_verify='foo')

        mock_get.assert_called_once_with('no/params', auth=None, verify='foo', headers={})

    @patch.object(requests, 'get')
    def test_invoke_endpoint_passes_auth_param_to_hettp_client_if_provided(self, mock_get):
        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, None, auth='bar')

        mock_get.assert_called_once_with('no/params', auth='bar', verify=True, headers={})

    @patch.object(requests, 'get')
    def test_invoke_endpoint_passes_extra_args_to_http_client(self, mock_get):
        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, None, 'a', 'b')

        mock_get.assert_called_once_with('no/params', 'a', 'b', auth=None, verify=True, headers={})

    @patch.object(requests, 'get')
    def test_invoke_endpoint_raises_error_if_bad_status_code_is_returned(self, mock_get):
        class MockResponse(object):
            def raise_for_status(self):
                raise Exception('bad status code!')
        mock_get.return_value = MockResponse()

        with self.assertRaises(Exception) as context:
            invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, None)

    @patch.object(requests, 'get')
    def test_invoke_endpoint_does_not_raise_error_if_bad_status_but_check_errors_is_false(self, mock_get):
        class MockResponse(object):
            def raise_for_status(self):
                raise Exception('bad status code!')
        mock_get.return_value = MockResponse()

        invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, None, check_errors=False)

    @patch.object(requests, 'get')
    def test_invoke_endpoint_returns_http_client_response(self, mock_get):
        class MockResponse(object):
            def raise_for_status(self):
                pass
        mock_get.return_value = MockResponse()

        response = invoke_endpoint(HttpVerb.GET, self.MockEndpoint.NO_PARAMS, None)

        self.assertEquals(response, mock_get.return_value)