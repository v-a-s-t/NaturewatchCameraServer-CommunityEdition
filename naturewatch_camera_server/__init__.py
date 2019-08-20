#!../venv/bin/python
import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from naturewatch_camera_server.CameraController import CameraController
from naturewatch_camera_server.ChangeDetector import ChangeDetector
from flask import Flask
from naturewatch_camera_server.api import api
from naturewatch_camera_server.data import data
from naturewatch_camera_server.static_page import static_page


def create_app():
    """
    Create flask app
    :return: Flask app object
    """
    flask_app = Flask(__name__, static_folder="static/client/build")
    flask_app.register_blueprint(api, url_prefix='/api')
    flask_app.register_blueprint(data, url_prefix='/data')
    flask_app.register_blueprint(static_page)

    # Setup logger
    flask_app.logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    flask_app.logger.addHandler(handler)
    flask_app.logger.setLevel(logging.DEBUG)

    # Load configuration json
    module_path = os.path.abspath(os.path.dirname(__file__))
    flask_app.user_config = json.load(open(os.path.join(module_path, "./config.json")))
    flask_app.user_config["photos_path"] = os.path.join(module_path, flask_app.user_config["photos_path"])

    # Create photos directory if it doesn't exist
    if os.path.isdir(flask_app.user_config["photos_path"]) is False:
        os.mkdir(flask_app.user_config["photos_path"])
        flask_app.logger.warning("Photos directory does not exist, creating path")
    flask_app.user_config["videos_path"] = os.path.join(module_path, flask_app.user_config["videos_path"])
    if os.path.isdir(flask_app.user_config["videos_path"]) is False:
        os.mkdir(flask_app.user_config["videos_path"])
        flask_app.logger.warning("Videos directory does not exist, creating path")

    # Create marker for time updates through the client
    flask_app.is_time_set = False

    # Instantiate classes
    flask_app.camera_controller = CameraController(flask_app.logger,flask_app.user_config, use_splitter_port=True)
    flask_app.change_detector = ChangeDetector(flask_app.camera_controller, flask_app.user_config, flask_app.logger)

    return flask_app