# import 3rd-party libraries
from flask import Flask
from flask_restful import Api

# import local files
from apis.resources.GameList import GameList
from apis.resources.GameSummaries import GameSummaries
from apis.resources.GameSummary import GameSummary
from apis.resources.DatasetList import DatasetList
from apis.resources.DatasetResources import DatasetResources
from apis.resources.DatasetFile import DatasetFile
from apis.resources.DatasetManifest import DatasetManifest
from configs.FileAPIConfig import FileAPIConfig

class FileAPI:
    """Class to define an API matching the original website API.

    This will eventually be superseded by a new version of the API,
    implementing the same functionality, but with cleaner endpoint routes/naming.
    """

    server_config : FileAPIConfig

    @staticmethod
    def register(app:Flask, settings:FileAPIConfig):
        """Set up the Legacy Web api in a flask app.

        :param app: _description_
        :type app: Flask
        """
        api = Api(app)

        try:
            api.add_resource(GameList,         '/games')
        except Exception as err:
            app.logger.warning(f"Couldn't register GameList resource:\n{err}")
        try:
            api.add_resource(GameSummaries,    '/games/details')
        except Exception as err:
            app.logger.warning(f"Couldn't register GameSummaries resource:\n{err}")
        try:
            api.add_resource(GameSummary,      '/games/<string:game_id>')
        except Exception as err:
            app.logger.warning(f"Couldn't register GameSummary resource:\n{err}")
        try:
            api.add_resource(DatasetList,      '/games/<string:game_id>/datasets',
                                               '/games/<string:game_id>/datasets/<int:year>')
        except Exception as err:
            app.logger.warning(f"Couldn't register DatasetList resource:\n{err}")
        try:
            api.add_resource(DatasetResources, '/games/<string:game_id>/datasets/<int:year>/<int:month>')
        except Exception as err:
            app.logger.warning(f"Couldn't register DatasetResources resource:\n{err}")
        try:
            api.add_resource(DatasetManifest,  '/games/<string:game_id>/datasets/<int:year>/<int:month>/manifest')
        except Exception as err:
            app.logger.warning(f"Couldn't register DatasetManifest resource:\n{err}")
        try:
            api.add_resource(DatasetFile,      '/games/<string:game_id>/datasets/<int:year>/<int:month>/<string:file_type>')
        except Exception as err:
            app.logger.warning(f"Couldn't register DatasetFile resource:\n{err}")
        FileAPI.server_config = settings
