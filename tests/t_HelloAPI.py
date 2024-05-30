# import libraries
import requests
from unittest import TestCase
# import locals
from tests.t_config import settings

class t_HelloAPI(TestCase):
    def RunAll(self):
        t = t_HelloAPI.t_Hello()
        t.test_home()
        t.test_get()
        t.test_post()
        t.test_put()

    class t_Hello:
        def test_home(self):
            base = settings['EXTERN_SERVER']
            print(f"GET test at {base}")
            result = requests.get(url=base)
            if result is not None:
                print(f"Result of get:\n{result.text}")
            else:
                print(f"No response to GET request.")
            print()

        def test_get(self):
            base = settings['EXTERN_SERVER']
            url = f"{base}/hello"
            print(f"GET test at {url}")
            result = requests.get(url=url)
            if result is not None:
                print(f"Result of get:\n{result.text}")
            else:
                print(f"No response to GET request.")

        def test_post(self):
            base = settings['EXTERN_SERVER']
            url = f"{base}/hello"
            print(f"POST test at {url}")
            result = requests.post(url=url)
            if result is not None:
                print(f"Result of post:\n{result.text}")
            else:
                print(f"No response to POST request.")

        def test_put(self):
            base = settings['EXTERN_SERVER']
            url = f"{base}/hello"
            print(f"PUT test at {url}")
            result = requests.put(url=url)
            if result is not None:
                print(f"Result of put:\n{result.text}")
            else:
                print(f"No response to PUT request.")