import logging

def log(message, context="Global".center(18, '='), level=logging.INFO):
    for line in message.split('\n'):
        logger.log(level, '[{}] {}'.format(str(context).center(18, '='), line))
