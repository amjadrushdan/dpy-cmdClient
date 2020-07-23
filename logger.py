import logging

logger = logging.getLogger()


def log(message, context="Global".center(22, '='), level=logging.INFO):
    for line in message.split('\n'):
        logger.log(level, '[{}] {}'.format(str(context).center(22, '='), line))
