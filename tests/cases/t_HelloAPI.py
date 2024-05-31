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
        t.setUp()
        t.test_Responded()
        t.test_Correct()
        t = t_Version()
        t.setUp()
        t.test_Responded()
        t.test_Correct()

class t_Hello(TestCase):
    def setUp(self):
        self.url    : str                         = f"{_config.ExternEndpoint}/"
        self.result : Optional[requests.Response] = SendTestRequest(url=self.url, request="GET")

    def test_Responded(self):
        _url = f"{_config.ExternEndpoint}/"
        if self.result is not None:
            self.assertTrue(self.result.ok)
        else:
            self.fail(f"No result from request to {_url}")

    def test_Succeeded(self):
        if self.result is not None:
            self.assertEqual(self.result.json()["success"], True)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        if self.result is not None:
            self.assertEqual(self.result.json()["data"], {"message":"hello, world"})
        else:
            self.fail(f"No result from request to {self.url}")

class t_Version(TestCase):
    def setUp(self):
        self.url    : str                         = f"{_config.ExternEndpoint}/version"
        self.result : Optional[requests.Response] = SendTestRequest(url=self.url, request="GET")

    def test_Responded(self):
        if self.result is not None:
            self.assertTrue(self.result.ok)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.result is not None:
            self.assertEqual(self.result.json()["success"], True)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        if self.result is not None:
            self.assertEqual(self.result.json()["data"], {"message":_config.APIVersion})
        else:
            self.fail(f"No result from request to {self.url}")

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