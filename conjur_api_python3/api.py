import base64
from enum import auto, Enum
from urllib.parse import quote

import requests
from requests.auth import HTTPBasicAuth

class HttpVerb(Enum):
    GET = auto()
    POST = auto()

class ConjurEndpoint(Enum):
    AUTHENTICATE = "{url}/authn/{account}/{login}/authenticate"
    LOGIN = "{url}/authn/{account}/login"
    SECRETS = "{url}/secrets/{account}/{kind}/{identifier}"

class Api(object):
    KIND_VARIABLE='variable'

    def __init__(self, url=None, server_cert=None, account='default', ssl_verify=True, debug=False):
        if not url or not account:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in Api creation!")

        self._url = url
        self._server_cert = server_cert
        self._account = account
        self._ssl_verify = ssl_verify

        self._default_params = {
            'url': url,
            'account': quote(account)
        }

        if not ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if debug:
            import logging
            from http.client import HTTPConnection

            HTTPConnection.debuglevel = 1

            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    def login(self, login_id=None, password=None):
        """
        TODO
        """

        if not self._url or not login_id or not password:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in login invocation!")

        print("Logging in to {}...".format(self._url))
        return self._invoke_endpoint(HttpVerb.GET, ConjurEndpoint.LOGIN,
                None, auth=HTTPBasicAuth(login_id, password)).text

    def authenticate(self, login_id=None, api_key=None):
        """
        TODO
        """

        if not self._url or not login_id or not api_key:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in authentication invocation!")

        print("Authenticating to {}...".format(self._url))
        return self._invoke_endpoint(HttpVerb.POST, ConjurEndpoint.AUTHENTICATE,
                { 'login': quote(login_id) }, api_key).text

    def set_variable(self, variable_id, value, login_id, api_key):
        token = self.authenticate(login_id, api_key)

        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': quote(variable_id)
        }

        return self._invoke_endpoint(HttpVerb.POST, ConjurEndpoint.SECRETS, params,
                                     value, api_token=token).text

    def get_variable(self, variable_id, login_id, api_key):
        token = self.authenticate(login_id, api_key)

        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': quote(variable_id)
        }

        return self._invoke_endpoint(HttpVerb.GET, ConjurEndpoint.SECRETS, params,
                                     api_token=token).content

    def _base64encode(self, source_str):
        return base64.b64encode(source_str.encode())

    def _invoke_endpoint(self, verb_id, endpoint_id, params, *args,
            check_errors=True, auth=None, api_token=None):

        if params is None:
            params = {}

        url = ConjurEndpoint(endpoint_id).value.format(**self._default_params, **params)

        headers={}
        if api_token and len(api_token) > 0:
            encoded_token = self._base64encode(api_token).decode('utf-8')
            headers['Authorization'] = 'Token token="{}"'.format(encoded_token)

        verb = HttpVerb(verb_id).name.lower()
        request_method = getattr(requests, verb)

        response = request_method(url, *args, verify=self._ssl_verify, auth=auth, headers=headers)
        if check_errors and response.status_code >= 300:
            # TODO: Use custom errors
            raise RuntimeError("Request failed: {}: {}".format(response.status_code,
                                                               response.text))

        return response