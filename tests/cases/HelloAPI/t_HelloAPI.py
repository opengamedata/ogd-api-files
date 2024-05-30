# import libraries
import requests
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
        result : requests.Response

        _url = _config.ExternEndpoint
        try:
            result = requests.get(url=_url)
        except Exception as err:
            raise err
        else:
            if _config.Verbose:
                print(f"Sent request to {_url}")
                if result is not None:
                    print(f"Result of get:\n{result.text}")
                else:
                    print(f"No response to GET request.")
                print()
        finally:
            self.assertTrue(result.ok)

    def test_get(self):
        result : requests.Response

        _url = f"{_config.ExternEndpoint}/hello"
        try:
            result = requests.get(url=_url)
        except Exception as err:
            raise err
        else:
            if _config.Verbose:
                print(f"Sent request to {_url}")
                if result is not None:
                    print(f"Result of get:\n{result.text}")
                else:
                    print(f"No response to GET request.")
        finally:
            self.assertTrue(result.ok)

    def test_post(self):
        result : requests.Response

        _url = f"{_config.ExternEndpoint}/hello"
        try:
            result = requests.post(url=_url)
        except Exception as err:
            raise err
        else:
            if _config.Verbose:
                print(f"Sent request to {_url}")
                if result is not None:
                    print(f"Result of post:\n{result.text}")
                else:
                    print(f"No response to POST request.")
        finally:
            self.assertTrue(result.ok)

    def test_put(self):
        result : requests.Response

        _url = f"{_config.ExternEndpoint}/hello"
        try:
            result = requests.put(url=_url)
        except Exception as err:
            raise err
        else:
            if _config.Verbose:
                print(f"Sent request to {_url}")
                if result is not None:
                    print(f"Result of put:\n{result.text}")
                else:
                    print(f"No response to PUT request.")
        finally:
            self.assertTrue(result.ok)