from typing import Any

class APIResponse: 
    def __init__(self, success:bool, data:Any):
        self._success   : bool     = success
        self._data    : Any          = data

    def ToDict(self):
        return {
            "success"   : self._success,
            "data"    : self._data
        }
