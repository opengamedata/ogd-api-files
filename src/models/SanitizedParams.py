# standard imports
import datetime, re
from typing import Any, Dict, Optional, Union

# 3rd-party imports
from flask_restful import reqparse

# local imports

class SanitizedParams:
    """Dumb struct to store the sanitized params from a request
    """
    def __init__(self, game_id:Optional[str], year:int, month:int):
        self._game_id : Optional[str] = game_id
        self._year    : int           = year
        self._month   : int           = month
    
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
    def sanitizeYear(year:Union[int, str], default_date:datetime.date=datetime.date.today()) -> int:
        ret_val: int

        if isinstance(year, int):
            ret_val = year
        else:
            if re.search("^[1-9]+$", str(year)) is None:
                ret_val = default_date.year
            else:
                ret_val = int(str(year))

        return ret_val

    @staticmethod
    def sanitizeMonth(month:Union[int, str], default_date:datetime.date=datetime.date.today()) -> int:
        ret_val: int

        if isinstance(month, int):
            ret_val = month
        else:
            if re.search("^[1-9]+$", str(month)) is None:
                ret_val = default_date.month
            else:
                ret_val = int(str(month))

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
        year    : int           = SanitizedParams.sanitizeYear(args.get("year",  default_date.year))
        month   : int           = SanitizedParams.sanitizeMonth(args.get("month", default_date.month))

        if game_id == "":
            game_id = None
        
        if month < 1 or month > 12:
            month = default_date.month

        if year < 2000 or year > datetime.date.today().year:
            year = default_date.year

        return SanitizedParams(game_id=game_id, year=year, month=month)
        return { "game_id": game_id, "year": year, "month": month }
