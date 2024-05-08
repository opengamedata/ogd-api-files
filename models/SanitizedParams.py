# standard imports
import datetime, re
from typing import Optional

# 3rd-party imports
from flask import request

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
    def sanitizeGameId(game_id: str) -> str:
        if re.search("^[A-Za-z_]+$", game_id) is None:
            game_id = ""
        return game_id.upper()

    # Shared utility function to retrieve game_id, year, and month from the request's query string.
    # Defaults are used if a value was not given or is invalid
    @staticmethod
    def FromRequest(default_date:datetime.date=datetime.date.today()) -> 'SanitizedParams':

        # Extract query string parameters
        game_id = SanitizedParams.sanitizeGameId(request.args.get("game_id", default ="", type=str))
        year = request.args.get("year",   default=default_date.year, type=int)
        month = request.args.get("month", default=default_date.month, type=int)

        if game_id == "":
            game_id = None
        
        if month < 1 or month > 12:
            month = default_date.month

        if year < 2000 or year > datetime.date.today().year:
            year = default_date.year

        return SanitizedParams(game_id=game_id, year=year, month=month)
        return { "game_id": game_id, "year": year, "month": month }
