import os
import logging
import traceback
from datetime import datetime

from src.custom_exceptions import LoggingSetupExceptionError

def setup_logging()->None:
    """Setting upt the log file details for the current project"""
    try:
        #making sure to check log directory if not, it will create
        if not os.path.exists("./logs"):
            os.mkdir("./logs")

        #creating new variable to store the unique time stamp log file name for each run
        log_file_name=datetime.now().strftime("Agentic_chatbot_%Y-%m-%d_%H-%M-%S.log")
        #setting the log configurations
        logging.basicConfig(filename="logs/{}".format(log_file_name),level=logging.DEBUG,
                            format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        #creating unique logger name for better handling instead of using base logging
        logger=logging.getLogger("logsetup_file")
        logger.info(msg="Logging setup completed")
    except Exception as e:
        #setting up log to store the cause of exception while setting up logging for the project
        logging.basicConfig(filename="logs/app.log", level=logging.DEBUG,
                            format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        # creating unique logger name for better handling instead of using base logging
        logger = logging.getLogger("logsetup_file")
        logging.error("Exception : {}".format(e))
        logging.error(msg=traceback.format_exc())
        #raising user defined exception
        raise LoggingSetupExceptionError("Exceptions occurred while setting up logging for the"
                                         "project. Please check app.logs for more information.")