# import 3rd-party libraries
from flask import Flask
from flask_restful import Api

# import local files
from apis.resources.GameList import GameList
from apis.resources.GameSummary import GameSummary
from apis.resources.DatasetList import DatasetList
from apis.resources.DatasetInfo import DatasetInfo
from apis.resources.DatasetFile import DatasetFile
from apis.resources.DatasetsYear import DatasetsYear
from apis.configs.FileAPIConfig import FileAPIConfig

class FileAPI:
    """Class to define an API matching the original website API.

    This will eventually be superseded by a new version of the API,
    implementing the same functionality, but with cleaner endpoint routes/naming.
    """

    server_config : FileAPIConfig

    # TODO: Remove this action and dependencies (interfaces, config) if we're certain they won't be needed.
    # The SQL for BigQuery did take a bit of effort to compose, but could always be retrieved from old commits

    @staticmethod
    def register(app:Flask, settings:FileAPIConfig):
        """Set up the Legacy Web api in a flask app.

        :param app: _description_
        :type app: Flask
        """
        # Expected WSGIScriptAlias URL path is /data
        api = Api(app)

        api.add_resource(GameList,     '/games')
        api.add_resource(GameSummary,  '/games/<string:game_id>')
        api.add_resource(DatasetList,  '/games/<string:game_id>/datasets')
        api.add_resource(DatasetsYear, '/games/<string:game_id>/datasets/<int:year>')
        api.add_resource(DatasetInfo,  '/games/<string:game_id>/datasets/<int:year>/<int:month>')
        api.add_resource(DatasetFile,  '/games/<string:game_id>/datasets/<int:year>/<int:month>/<string:file_type>')
        FileAPI.server_config = settings
