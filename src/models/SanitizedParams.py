# standard imports
import datetime, re
from typing import Any, Dict, Optional, Union

# 3rd-party imports
from flask_restful import reqparse

# local imports

class SanitizedParams:
    """Dumb struct to store the sanitized params from a request
    """
    def __init__(self, game_id:Optional[str], year:int, month:int, default_date:Optional[datetime.date]=None):
        default_date = default_date if default_date is not None else datetime.date.today()
        self._game_id : Optional[str] = SanitizedParams.sanitizeGameId(game_id) if game_id is not None else None
        self._year    : int           = SanitizedParams.sanitizeYear(year, default_date=default_date)
        self._month   : int           = SanitizedParams.sanitizeMonth(month, default_date=default_date)
    
    @property
    def GameID(self) -> Optional[str]:
        return self._game_id
    @property
    def Year(self) -> int:
        return self._year
    @property
    def Month(self) -> int:
        return self._month

    # If the given game_id contains allowed characters, return it in UPPERCASE, otherwise return empty string
    @staticmethod
    def sanitizeGameId(game_id:str) -> str:
        if re.search("^[A-Za-z_]+$", game_id) is None:
            game_id = ""
        return game_id.upper()

    @staticmethod
    def sanitizeYear(year:Union[int, str]) -> Optional[int]:
        ret_val: Optional[int] = None

        if not isinstance(year, int):
            if re.search("^[0-9]+$", str(year)) is not None:
                year = int(str(year))

        if ret_val and ret_val not in range(2000, datetime.date.today().year+1):
            ret_val = None

        return ret_val

    @staticmethod
    def sanitizeMonth(month:Union[int, str]) -> Optional[int]:
        ret_val: Optional[int] = None

        if not isinstance(month, int):
            if re.search("^[0-9]+$", str(month)) is not None:
                ret_val = int(str(month))
        
        if ret_val and ret_val not in range(1, 12+1):
            ret_val = None

        return ret_val

    # Shared utility function to retrieve game_id, year, and month from the request's query string.
    # Defaults are used if a value was not given or is invalid
    @staticmethod
    def FromRequest(default_date:datetime.date=datetime.date.today()) -> 'SanitizedParams':

        # Extract query string parameters
        parser = reqparse.RequestParser()
        parser.add_argument("game_id", type=str, nullable=True, required=False, default="",                 location="args")
        parser.add_argument("year",    type=int, nullable=True, required=False, default=default_date.year,  location="args")
        parser.add_argument("month",   type=int, nullable=True, required=False, default=default_date.month, location="args")
        args : Dict[str, Any] = parser.parse_args()

        game_id : Optional[str] = SanitizedParams.sanitizeGameId(args.get("game_id", ""))
        year    : int           = args.get("year",  default_date.year)
        month   : int           = args.get("month", default_date.month)

        if game_id == "":
            game_id = None

        return SanitizedParams(game_id=game_id, year=year, month=month)
        # return { "game_id": game_id, "year": year, "month": month }
