import functools
import subprocess
import sys

import flask

from utils import root_path

@functools.cache
def app() -> flask.Flask:
    """Make Flask application if needed"""
    _app = flask.Flask(__name__, instance_relative_config=True)

    @_app.route('/update_plots', methods=['POST'])
    def update_plots():
        try:
            subprocess.run(
                [
                    sys.executable,
                    root_path() / "sensor_logger" / "plot.py",
                    root_path() / "www" / "html",
                ],
                capture_output=True,
                check=True,
            )
            return flask.jsonify({
                "status": "success",
                "plot_dir": "/",
            })
        except subprocess.CalledProcessError as e:
            return (
                flask.jsonify({"status": "error", "message": str(e.stderr.decode())}),
                500,
            )

    return _app

if __name__ == "__main__":
    app().run(host="0.0.0.0", port=5000)
