# standard imports
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Optional

# local imports
from ogd.core.schemas.Schema import Schema

class DatasetSchema(Schema):
    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._date_modified       : date | str
        self._start_date          : date | str
        self._end_date            : date | str
        self._ogd_revision        : str
        self._session_ct          : Optional[int]
        self._player_ct           : Optional[int]
        self._raw_file            : Optional[Path]
        self._events_file         : Optional[Path]
        self._events_template     : Optional[Path]
        self._sessions_file       : Optional[Path]
        self._sessions_template   : Optional[Path]
        self._players_file        : Optional[Path]
        self._players_template    : Optional[Path]
        self._population_file     : Optional[Path]
        self._population_template : Optional[Path]

        if not isinstance(all_elements, dict):
            all_elements = {}
    # 1. Parse dates
        if "date_modified" in all_elements.keys():
            self._date_modified = DatasetSchema._parseDateModified(all_elements["date_modified"])
        else:
            self._date_modified = "UNKNOWN"
        if "start_date" in all_elements.keys():
            self._start_date = DatasetSchema._parseStartDate(all_elements["start_date"])
        else:
            self._start_date = "UNKNOWN"
        if "end_date" in all_elements.keys():
            self._end_date = DatasetSchema._parseEndDate(all_elements["end_date"])
        else:
            self._end_date = "UNKNOWN"
    # 2. Parse metadata
        if "ogd_revision" in all_elements.keys():
            self._ogd_revision = DatasetSchema._parseOGDRevision(all_elements["ogd_revision"])
        else:
            self._ogd_revision = "UNKNOWN"
        if "sessions" in all_elements.keys():
            self._session_ct = DatasetSchema._parseSessionCount(all_elements["sessions"])
        else:
            self._session_ct = None
        if "players" in all_elements.keys():
            self._players = DatasetSchema._parsePlayerCount(all_elements["players"])
        else:
            self._player_ct = None
    # 3. Parse file/template paths
        if "raw_file" in all_elements.keys():
            self._raw_file = DatasetSchema._parseRawFile(all_elements["raw_file"])
        else:
            self._raw_file = None
        if "events_file" in all_elements.keys():
            self._events_file = DatasetSchema._parseEventsFile(all_elements["events_file"])
        else:
            self._events_file = None
        if "events_template" in all_elements.keys():
            self._events_template = DatasetSchema._parseEventsTemplate(all_elements["events_template"])
        else:
            self._events_template = None
        if "sessions_file" in all_elements.keys():
            self._sessions_file = DatasetSchema._parseSessionsFile(all_elements["sessions_file"])
        else:
            self._sessions_file = None
        if "sessions_template" in all_elements.keys():
            self._sessions_template = DatasetSchema._parseSessionsTemplate(all_elements["sessions_template"])
        else:
            self._sessions_template = None
        if "players_file" in all_elements.keys():
            self._players_file = DatasetSchema._parsePlayersFile(all_elements["players_file"])
        else:
            self._players_file = None
        if "players_template" in all_elements.keys():
            self._players_template = DatasetSchema._parsePlayersTemplate(all_elements["players_template"])
        else:
            self._players_template = None
        if "population_file" in all_elements.keys():
            self._population_file = DatasetSchema._parsePopulationFile(all_elements["population_file"])
        else:
            self._population_file = None
        if "population_template" in all_elements.keys():
            self._population_template = DatasetSchema._parsePopulationTemplate(all_elements["population_template"])
        else:
            self._population_template = None

        _used = {"date_modified", "start_date", "end_date", "ogd_revision", "sessions", "players",
                 "raw_file", "events_file", "events_template",
                 "sessions_file", "sessions_template", "players_file", "players_template",
                 "population_file", "population_template"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    # *** Properties ***

    @property
    def DateModified(self) -> date | str:
        return self._date_modified
    @property
    def DateModifiedStr(self) -> str:
        ret_val : str
        if isinstance(self._date_modified, date):
            ret_val = self._date_modified.strftime("%m/%d/%Y")
        else:
            ret_val = self._date_modified
        return ret_val
    @property
    def StartDate(self) -> date | str:
        return self._start_date
    @property
    def EndDate(self) -> date | str:
        return self._end_date
    @property
    def OGDRevision(self) -> str:
        return self._ogd_revision
    @property
    def SessionCount(self) -> Optional[int]:
        return self._session_ct
    @property
    def PlayerCount(self) -> Optional[int]:
        return self._player_ct
    @property
    def RawFile(self) -> Optional[Path]:
        return self._raw_file
    @property
    def EventsFile(self) -> Optional[Path]:
        return self._events_file
    @property
    def EventsTemplate(self) -> Optional[Path]:
        return self._events_template
    @property
    def SessionsFile(self) -> Optional[Path]:
        return self._sessions_file
    @property
    def SessionsTemplate(self) -> Optional[Path]:
        return self._sessions_template
    @property
    def PlayersFile(self) -> Optional[Path]:
        return self._players_file
    @property
    def PlayersTemplate(self) -> Optional[Path]:
        return self._players_template
    @property
    def PopulationFile(self) -> Optional[Path]:
        return self._population_file
    @property
    def PopulationTemplate(self) -> Optional[Path]:
        return self._population_template

    @property
    def FileSet(self):
        _fset = [
           "r" if self.RawFile is not None else "",
           "e" if self.EventsFile is not None else "",
           "s" if self.SessionsFile is not None else "",
           "p" if self.PlayersFile is not None else "",
           "P" if self.PopulationFile is not None else ""
        ]
        return "".join(_fset)

    @property
    def TemplateSet(self):
        _tset = [
           "e" if self.EventsTemplate is not None else "",
           "s" if self.SessionsTemplate is not None else "",
           "p" if self.PlayersTemplate is not None else "",
           "P" if self.PopulationTemplate is not None else ""
        ]
        return "".join(_tset)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = \
f"""{self.Name}: {self.PlayerCount} players across {self.SessionCount} sessions.  
Last modified {self.DateModified.strftime('%m/%d/%Y') if type(self.DateModified) == date else self.DateModified} with OGD v.{self.OGDRevision or 'UNKNOWN'}  
- Files: [{self.FileSet}]  
- Templates: [{self.TemplateSet}]"""
        return ret_val

    @staticmethod
    def EmptySchema() -> "DatasetSchema":
        return DatasetSchema(name="NOT FOUND", all_elements={})

    # *** Private Functions ***

    # NOTE: Yes, most of these parse functions are redundant, but that's fine,
    # we just want to have one bit of code to parse each piece of the schema, even if most do the same thing.

    @staticmethod
    def _parseDateModified(date_modified) -> date:
        ret_val : date
        if isinstance(date_modified, date):
            ret_val = date_modified
        else:
            ret_val = datetime.strptime(date_modified, "%m/5d/%Y").date()
            # Logger.Log(f"Dataset modified date was unexpected type {type(date_modified)}, defaulting to strptime(date_modified)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseStartDate(start_date) -> date:
        ret_val : date
        if isinstance(start_date, date):
            ret_val = start_date
        else:
            ret_val = datetime.strptime(start_date, "%m/5d/%Y").date()
            # Logger.Log(f"Dataset start date was unexpected type {type(start_date)}, defaulting to strptime(start_date)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseEndDate(end_date) -> date:
        ret_val : date
        if isinstance(end_date, date):
            ret_val = end_date
        else:
            ret_val = datetime.strptime(end_date, "%m/5d/%Y").date()
            # Logger.Log(f"Dataset end date was unexpected type {type(end_date)}, defaulting to strptime(end_date)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseOGDRevision(revision) -> str:
        ret_val : str
        if isinstance(revision, str):
            ret_val = revision
        else:
            ret_val = str(revision)
            # Logger.Log(f"Dataset OGD revision was unexpected type {type(revision)}, defaulting to str(revision)={ret_val}.", logging.WARN)
        return ret_val
