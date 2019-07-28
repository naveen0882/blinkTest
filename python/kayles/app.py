# logging - need to set first
from kayles import config
import logging
formatter = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
logging.basicConfig(format=formatter, level=logging.getLevelName(config.LOGLEVEL))

from flask import Flask
from kayles.routes import routes

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.register_blueprint(routes)

if __name__ == '__main__':
    logger.info('now serving on %s:%s', config.HOST, config.PORT)
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
