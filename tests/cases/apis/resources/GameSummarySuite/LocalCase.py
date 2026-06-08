# import libraries
import logging
import unittest
from json.decoder import JSONDecodeError
from typing import Optional
from unittest import TestCase
# import 3rd-party libraries
import requests
from flask import Flask
from werkzeug.test import TestResponse
# import ogd libraries
from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse, ResponseStatus
from ogd.common.utils.Logger import Logger
# import locals
from src.configs.FileAPIConfig import FileAPIConfig
from src.apis.FileAPI import FileAPI
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config.t_config import settings

