from application import create_app
import logging
import os

if __name__ == '__main__':
    app = create_app()
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host="127.0.0.1", port=2020, debug=debug)
else:
    app = create_app()
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)