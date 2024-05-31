import requests
from typing import Any, Dict, Optional

from tests.schemas.TestConfigSchema import TestConfigSchema

def SendTestRequest(url:str, request:str, params:Dict[str, Any], config:TestConfigSchema) -> Optional[requests.Response]:
    result : Optional[requests.Response] = None
    if not (url.startswith("https://") or url.startswith("http://")):
        url = f"https://{url}" # give url a default scheme
    try:
        if config.Verbose:
            print(f"Sending request to {url}")
        match (request.upper()):
            case "GET":
                result = requests.get(url, params=params)
            case "POST":
                result = requests.post(url, params=params)
            case "PUT":
                result = requests.put(url, params=params)
            case _:
                print(f"Bad request type {request}, defaulting to GET")
                result = requests.get(url)
    except Exception as err:
        if config.Verbose:
            print(f"Error on {request} request to {url} : {err}")
        raise err
    else:
        if config.Verbose:
            if result is not None:
                print(f"Result of {request} request:\n{result.text}")
            else:
                print(f"No response to {request} request.")
            print()
    finally:
        return result