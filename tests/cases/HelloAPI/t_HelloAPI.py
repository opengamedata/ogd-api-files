# import libraries
import requests
from typing import Optional
from unittest import TestCase, TestSuite
# import locals
from tests.schemas.TestConfigSchema import TestConfigSchema
from tests.config.t_config import settings

_config = TestConfigSchema.FromDict(name="HelloAPITestConfig", all_elements=settings, logger=None)

class t_HelloAPI(TestCase):
    def RunAll(self):
        t = t_HelloAPI()
        t.test_home()
        t.test_get()
        t.test_post()
        t.test_put()

    def test_home(self):
        result : Optional[requests.Response]

        _url = _config.ExternEndpoint
        result = t_HelloAPI._sendTestRequest(url=_url, request="GET")
        if result is not None:
            self.assertTrue(result.ok)
        else:
            self.fail(f"No result from request to {_url}")

    def test_get(self):
        result : Optional[requests.Response]

        _url = f"{_config.ExternEndpoint}/hello"
        result = t_HelloAPI._sendTestRequest(url=_url, request="GET")
        if result is not None:
            self.assertTrue(result.ok)
        else:
            self.fail(f"No result from request to {_url}")

    def test_post(self):
        result : Optional[requests.Response]

        _url = f"{_config.ExternEndpoint}/hello"
        result = t_HelloAPI._sendTestRequest(url=_url, request="POST")
        if result is not None:
            self.assertTrue(result.ok)
        else:
            self.fail(f"No result from request to {_url}")

    def test_put(self):
        result : Optional[requests.Response]

        _url = f"{_config.ExternEndpoint}/hello"
        result = t_HelloAPI._sendTestRequest(url=_url, request="PUT")
        if result is not None:
            self.assertTrue(result.ok)
        else:
            self.fail(f"No result from request to {_url}")

    @staticmethod
    def _sendTestRequest(url:str, request:str) -> Optional[requests.Response]:
        result : Optional[requests.Response] = None
        try:
            if _config.Verbose:
                print(f"Sending request to {url}")
            match (request.upper()):
                case "GET":
                    result = requests.get(url)
                case "POST":
                    result = requests.post(url)
                case "PUT":
                    result = requests.put(url)
                case _:
                    print(f"Bad request type {request}, defaulting to GET")
                    result = requests.get(url)
        except Exception as err:
            if _config.Verbose:
                print(f"Error on {request} request to {url} : {err}")
            raise err
        else:
            if _config.Verbose:
                if result is not None:
                    print(f"Result of {request} request:\n{result.text}")
                else:
                    print(f"No response to {request} request.")
                print()
        finally:
            return result