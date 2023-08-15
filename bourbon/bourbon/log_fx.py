import logging
import pathlib 
from sys import stdout, stderr


def setup_log(log_path: pathlib.Path, logger_name = __name__) -> logging.Logger: 
    """setup_log create logger 

    Args:
        log_path (pathlib.Path): the path to set the file manager
        logger_name (_type_, optional): The logger name to use. Defaults to __name__.

    Returns:
        logging.Logger: logger instance
    """
    log_fmt = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",datefmt="%H:%M:%S")
    stream_fmt = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # set up streams for logging stdout and err
    stream = logging.StreamHandler(stdout)
    stream.setLevel(logging.DEBUG)
    stream.setFormatter(stream_fmt)
    logger.addHandler(stream)

    # err formatting for stdout
    err_stream = logging.StreamHandler(stderr)
    err_stream.setLevel(logging.ERROR)
    err_stream.setFormatter(stream_fmt)
    logger.addHandler(err_stream)

    fileHandler = logging.FileHandler(filename=log_path)
    fileHandler.setFormatter(log_fmt)
    fileHandler.setLevel(level=logging.INFO)

    logger.addHandler(fileHandler)

    return logger