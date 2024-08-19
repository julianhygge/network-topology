import logging
import os

from app.config.configuration import ApiConfiguration

logging_configuration = ApiConfiguration().logging
logger = logging.getLogger("Peer to peer energy trading API")
logger.setLevel(getattr(logging, logging_configuration.level))

log_file = os.path.join(logging_configuration.log_directory, "logfile.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(getattr(logging, logging_configuration.level))

console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, logging_configuration.level))


formatter = logging.Formatter(
    "%(asctime)s %(levelname)-2s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)


logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info(f"{ApiConfiguration().load_profile}")
