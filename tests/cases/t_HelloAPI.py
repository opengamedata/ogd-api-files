# import libraries
import requests
from typing import Optional
from unittest import TestCase, TestSuite, main
# import locals
from tests.schemas.TestConfigSchema import TestConfigSchema
from tests.config.t_config import settings

_config = TestConfigSchema.FromDict(name="HelloAPITestConfig", all_elements=settings, logger=None)

class t_HelloAPI:
    @staticmethod
    def RunAll():
        t = t_Hello()
        t.test_Hello()
        t.test_Version()

class t_Hello(TestCase):
    def test_Hello(self):
        result : Optional[requests.Response]

        _url = f"{_config.ExternEndpoint}/"
        result = SendTestRequest(url=_url, request="GET")
        if result is not None:
            self.assertTrue(result.ok)
        else:
            self.fail(f"No result from request to {_url}")

    def test_Version(self):
        result : Optional[requests.Response]

        _url = f"{_config.ExternEndpoint}/version"
        result = SendTestRequest(url=_url, request="GET")
        if result is not None:
            self.assertTrue(result.ok)
        else:
            self.fail(f"No result from request to {_url}")

def SendTestRequest(url:str, request:str) -> Optional[requests.Response]:
    result : Optional[requests.Response] = None
    if not (url.startswith("https://") or url.startswith("http://")):
        url = f"https://{url}" # give url a default scheme
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

if __name__ == "__main__":
    main()