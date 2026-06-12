# standard imports
import datetime, re
from typing import Optional

from ogd.apis.models.files.DatasetFile import FileTypes

class SanitizedParams:
    """Dumb struct to store the sanitized params from a request
    """

    # If the given game_id contains allowed characters, return it in UPPERCASE, otherwise return empty string
    @staticmethod
    def SanitizeGameID(game_id:Optional[str]) -> Optional[str]:
        ret_val: Optional[str] = None
        if game_id is None:
            ret_val = None
        elif re.search("^[A-Za-z_]+$", game_id) is not None:
            ret_val = game_id.upper()

        return ret_val

    @staticmethod
    def SanitizeYear(year:Optional[int | str]) -> Optional[int]:
        ret_val: Optional[int] = None

        match year:
            case None:
                ret_val = None
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
    def SanitizeMonth(month:Optional[int | str]) -> Optional[int]:
        ret_val: Optional[int] = None

        match month:
            case None:
                ret_val = None
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
    def SanitizeFileType(file_type:Optional[FileTypes | str]) -> Optional[FileTypes]:
        ret_val: Optional[FileTypes] = None

        match file_type:
            case None:
                ret_val = None
            case FileTypes():
                ret_val = file_type
            case str():
                if re.search("^[A-Za-z_]+$", file_type) is not None:
                    ret_val = FileTypes[file_type.upper()]

        return ret_val
