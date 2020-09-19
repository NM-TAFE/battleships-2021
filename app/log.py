import logging


def get_logger(name):
    """Create a customer logger.

    :param name: Name to be used for the logger
    :return: Custom logger
    """
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger
