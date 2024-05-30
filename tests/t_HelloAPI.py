# import libraries
import requests
from unittest import TestCase, TestSuite
# import locals
from tests.t_config import settings

class t_HelloAPI(TestSuite):
    def RunAll(self):
        t = t_HelloAPI.t_Hello()
        t.test_home()
        t.test_get()
        t.test_post()
        t.test_put()

    class t_Hello(TestCase):
        def test_home(self):
            result : requests.Response

            base = settings['EXTERN_SERVER']
            try:
                result = requests.get(url=base)
            except Exception as err:
                raise err
            else:
                if settings.get("VERBOSE", False):
                    if result is not None:
                        print(f"Result of get:\n{result.text}")
                    else:
                        print(f"No response to GET request.")
                    print()
            finally:
                self.assertTrue(result.ok)

        def test_get(self):
            result : requests.Response

            base = settings['EXTERN_SERVER']
            url = f"{base}/hello"
            try:
                result = requests.get(url=url)
            except Exception as err:
                raise err
            else:
                if settings.get("VERBOSE", False):
                    if result is not None:
                        print(f"Result of get:\n{result.text}")
                    else:
                        print(f"No response to GET request.")
            finally:
                self.assertTrue(result.ok)

        def test_post(self):
            result : requests.Response

            base = settings['EXTERN_SERVER']
            url = f"{base}/hello"
            try:
                result = requests.post(url=url)
            except Exception as err:
                raise err
            else:
                if settings.get("VERBOSE", False):
                    if result is not None:
                        print(f"Result of post:\n{result.text}")
                    else:
                        print(f"No response to POST request.")
            finally:
                self.assertTrue(result.ok)

        def test_put(self):
            result : requests.Response

            base = settings['EXTERN_SERVER']
            url = f"{base}/hello"
            try:
                result = requests.put(url=url)
            except Exception as err:
                raise err
            else:
                if settings.get("VERBOSE", False):
                    if result is not None:
                        print(f"Result of put:\n{result.text}")
                    else:
                        print(f"No response to PUT request.")
            finally:
                self.assertTrue(result.ok)