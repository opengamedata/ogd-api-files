# standard imports
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Self

# ogd imports
from ogd.common.filters.Filter import Filter
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.schemas.locations.FileLocationSchema import FileLocationSchema
from ogd.common.schemas.events.EventSchema import EventSchema
from ogd.common.schemas.events.GameStateSchema import GameStateSchema
from ogd.common.schemas.features.FeatureSchema import FeatureSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema

class DatasetManifest(DatasetSchema):
    """Model representing a DatasetManifest.

    In practice, this is just a wrapper around a DatasetSchema with a few tweaks to the structure to make it nicer to receive from an API request.
    The full 2.0.0 release of ogd-common will address this, but for now, this temporary measure gets us to a point of allowing a test of this.

    :param DatasetSchema: _description_
    :type DatasetSchema: _type_
    """

    def __init__(self, name:str, game_id:Optional[str],       dataset_id:Optional[DatasetKey],
                 filters:Optional[Dict[str, str | Filter]],   session_ct:Optional[int],                 player_ct:Optional[int],
                 game_state:Optional[GameStateSchema],        events:Optional[Dict[str, EventSchema]],  features:Optional[Dict[str, FeatureSchema]],
                 ogd_version:Optional[SemanticVersion | str], ogd_revision:Optional[str],               event_spec_version:Optional[SemanticVersion | str],
                 base_files_location:Optional[Path],
                 game_events_file:Optional[LocationSchema],   all_events_file:Optional[LocationSchema], combined_feats_file:Optional[LocationSchema],
                 sessions_file:Optional[LocationSchema],      players_file:Optional[LocationSchema],    population_file:Optional[LocationSchema],
                 # deprecated, compatibility params
                 start_date:Optional[date|str],  end_date:Optional[date|str], date_modified:Optional[date|str], 
                 other_elements:Optional[Map]=None):
        """Construct in the same way as a DatasetSchema

        :param name: _description_
        :type name: str
        :param game_id: _description_
        :type game_id: Optional[str]
        :param dataset_id: _description_
        :type dataset_id: Optional[DatasetKey]
        :param filters: _description_
        :type filters: Optional[Dict[str, str  |  Filter]]
        :param session_ct: _description_
        :type session_ct: Optional[int]
        :param player_ct: _description_
        :type player_ct: Optional[int]
        :param game_state: _description_
        :type game_state: Optional[GameStateSchema]
        :param events: _description_
        :type events: Optional[Dict[str, EventSchema]]
        :param features: _description_
        :type features: Optional[Dict[str, FeatureSchema]]
        :param ogd_version: _description_
        :type ogd_version: Optional[SemanticVersion  |  str]
        :param ogd_revision: _description_
        :type ogd_revision: Optional[str]
        :param event_spec_version: _description_
        :type event_spec_version: Optional[SemanticVersion  |  str]
        :param base_files_location: _description_
        :type base_files_location: Optional[Path]
        :param game_events_file: _description_
        :type game_events_file: Optional[LocationSchema]
        :param all_events_file: _description_
        :type all_events_file: Optional[LocationSchema]
        :param combined_feats_file: _description_
        :type combined_feats_file: Optional[LocationSchema]
        :param sessions_file: _description_
        :type sessions_file: Optional[LocationSchema]
        :param players_file: _description_
        :type players_file: Optional[LocationSchema]
        :param population_file: _description_
        :type population_file: Optional[LocationSchema]
        :param start_date: _description_
        :type start_date: Optional[date | str]
        :param end_date: _description_
        :type end_date: Optional[date | str]
        :param date_modified: _description_
        :type date_modified: Optional[date | str]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        super().__init__(name=name, game_id=game_id, dataset_id=dataset_id, filters=filters,
                         session_ct=session_ct, player_ct=player_ct,
                         game_state=game_state, events=events, features=features,
                         ogd_version=ogd_version, ogd_revision=ogd_revision, event_spec_version=event_spec_version,
                         base_files_location=base_files_location, game_events_file=game_events_file, all_events_file=all_events_file,
                         combined_feats_file=combined_feats_file, sessions_file=sessions_file, players_file=players_file, population_file=population_file,
                         start_date=start_date, end_date=end_date, date_modified=date_modified, other_elements=other_elements)
    @property
    def AsDict(self) -> Dict[str, Any]:
        return {
            "game_id"            : self.Key.GameID,
            "dataset_id"         : str(self.Key),
            "population": {
                "session_count"      : self.SessionCount,
                "player_count"       : self.SessionCount,
                "filters"            : {name:str(filt) for name,filt in self.Filters.items()},
            },
            "game_state"         : self.GameState.AsDict if self.GameState else None,
            "events"             : { key : event.AsDict for key,event in self.Events.items() } if self.Events else None,
            "features"           : { key : feature.AsDict for key,feature in self.Features.items() } if self.Features else None,
            "versioning": {
                "ogd_version"        : str(self.OGDVersion),
                "ogd_revision"       : self.OGDRevision,
                "event_spec_version" : str(self.EventSpecificationVersion),
            },
            # output info
            "output": {
                "base_file_location" : str(self._base_files_location),
                "all_events_file"    : self._all_events_file.Location   if self._all_events_file   else None,
                "game_events_file"   : self._game_events_file.Location  if self._game_events_file  else None,
                "all_features_file"  : self._all_features_file.Location if self._all_features_file else None,
                "sessions_file"      : self._sessions_file.Location     if self._sessions_file     else None,
                "players_file"       : self._players_file.Location      if self._players_file      else None,
                "population_file"    : self._population_file.Location   if self._population_file   else None,
            },
            # deprecated/compatibility info
            "date_modified"      : self.DateModified.strftime("%m/%d/%Y") if isinstance(self.DateModified, date) else self.DateModified,
            "start_date"         : self.StartDate.strftime("%m/%d/%Y")    if isinstance(self.StartDate, date)    else self.StartDate,
            "end_date"           : self.EndDate.strftime("%m/%d/%Y")      if isinstance(self.EndDate, date)      else self.EndDate,
        }