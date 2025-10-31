from loguru import logger
# simple file logger; rotates at 5MB
logger.add("gitsafeops.log", rotation="5 MB", level="INFO", enqueue=True)
