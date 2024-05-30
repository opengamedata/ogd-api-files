# import libraries
import requests
from unittest import TestCase, TestSuite
# import locals
from tests.schemas.TestConfigSchema import TestConfigSchema
from tests.config.t_config import settings

class t_HelloAPI(TestSuite):
    _config = TestConfigSchema.FromDict(name="HelloAPITestConfig", all_elements=settings, logger=None)
    def RunAll(self):
        t = t_HelloAPI.t_Hello()
        t.test_home()
        t.test_get()
        t.test_post()
        t.test_put()

    class t_Hello(TestCase):
        def test_home(self):
            result : requests.Response
            print("Running test of home")

            _cfg = t_HelloAPI._config
            try:
                result = requests.get(url=_cfg.ExternEndpoint)
            except Exception as err:
                raise err
            else:
                if _cfg.Verbose:
                    if result is not None:
                        print(f"Result of get:\n{result.text}")
                    else:
                        print(f"No response to GET request.")
                    print()
            finally:
                self.assertTrue(result.ok)

        def test_get(self):
            result : requests.Response
            print("Running test of get")

            _cfg = t_HelloAPI._config
            _url = f"{_cfg.ExternEndpoint}/hello"
            try:
                result = requests.get(url=_url)
            except Exception as err:
                raise err
            else:
                if _cfg.Verbose:
                    if result is not None:
                        print(f"Result of get:\n{result.text}")
                    else:
                        print(f"No response to GET request.")
            finally:
                self.assertTrue(result.ok)

        def test_post(self):
            result : requests.Response
            print("Running test of post")

            _cfg = t_HelloAPI._config
            _url = f"{_cfg.ExternEndpoint}/hello"
            try:
                result = requests.post(url=_url)
            except Exception as err:
                raise err
            else:
                if _cfg.Verbose:
                    if result is not None:
                        print(f"Result of post:\n{result.text}")
                    else:
                        print(f"No response to POST request.")
            finally:
                self.assertTrue(result.ok)

        def test_put(self):
            result : requests.Response
            print("Running test of put")

            _cfg = t_HelloAPI._config
            _url = f"{_cfg.ExternEndpoint}/hello"
            try:
                result = requests.put(url=_url)
            except Exception as err:
                raise err
            else:
                if _cfg.Verbose:
                    if result is not None:
                        print(f"Result of put:\n{result.text}")
                    else:
                        print(f"No response to PUT request.")
            finally:
                self.assertTrue(result.ok)