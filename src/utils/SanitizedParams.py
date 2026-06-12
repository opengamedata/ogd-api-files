# standard imports
import datetime, re
import builtins
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

# 3rd-party imports
from flask_restful import reqparse

# local imports

@dataclass
class SanitizedParams:
    """Dumb struct to store the sanitized params from a request
    """
    game_id : str
    year    : int
    month   : int
    
    @property
    def GameID(self) -> str:
        return self.game_id
    @property
    def Year(self) -> int:
        return self.year
    @property
    def Month(self) -> int:
        return self.month

    @property
    def IsValid(self) -> bool:
        return None not in {self.GameID, self.Year, self.Month}

    # If the given game_id contains allowed characters, return it in UPPERCASE, otherwise return empty string
    @staticmethod
    def SanitizeGameID(game_id:str) -> Optional[str]:
        ret_val: Optional[str] = None

        if re.search("^[A-Za-z_]+$", game_id) is not None:
            ret_val = game_id.upper()

        return ret_val

    @staticmethod
    def SanitizeYear(year:int | str) -> Optional[int]:
        ret_val: Optional[int] = None

        match year:
            case int():
                ret_val = int(year)
            case str():
                if re.search(r"^[0-9]{4}$", str(year)) is not None:
                    ret_val = int(year)
            case _:
                if re.search(r"^[0-9]{4}$", str(year)) is not None:
                    ret_val = int(str(year))

        if ret_val and ret_val not in range(2000, datetime.date.today().year+1):
            ret_val = None

        return ret_val

    @staticmethod
    def SanitizeMonth(month:int | str) -> Optional[int]:
        ret_val: Optional[int] = None

        match month:
            case int():
                ret_val = int(month)
            case str():
                if re.search(r"^[0-9]{1,2}$", month) is not None:
                    ret_val = int(month)
            case _:
                if re.search(r"^[0-9]{1,2}+$", str(month)) is not None:
                    ret_val = int(str(month))
        
        if ret_val and ret_val not in range(1, 12+1):
            ret_val = None

        return ret_val

    @staticmethod
    def FromParams(game_id:Optional[str], year:int, month:int) -> Optional["SanitizedParams"]:
        _game_id : Optional[str] = SanitizedParams.SanitizeGameID(game_id) if game_id is not None else None
        _year    : Optional[int] = SanitizedParams.SanitizeYear(year)
        _month   : Optional[int] = SanitizedParams.SanitizeMonth(month)
        if _game_id is not None and _year is not None and _month is not None:
            return SanitizedParams(game_id=_game_id, year=_year, month=_month)
        else:
            return None
