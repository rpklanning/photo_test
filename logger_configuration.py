import sys
from datetime import date, datetime
import logging

def LOGGER_CONFIGURATION():
    # 1. define a new filename for logging the events
    # get day
    day = date.today().strftime('%Y%m%d')
    day_str = (str(day)).replace("-","")
    print("day = ", day_str)
    # get time
    now = datetime.now()
    hour = str(now.hour)
    minute = str(now.minute)
    second = str(now.second)
    time_str =hour + minute + second
    print("time = ", time_str)

    #2 generate the error log filename
    error_log_filename = "Error_Log_" + day_str + "_" + time_str
    print("error log filename = ", error_log_filename)

    # 3. Configure the logging system
    logging.basicConfig(
    filename=error_log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True
    )
    logger = logging.getLogger("neon__db_app")
    return logger


