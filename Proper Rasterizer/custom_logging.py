import time

# enum for levels
class LogLevel:
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

DEBUG_COLOR = '\033[94m'
INFO_COLOR = '\033[92m'
WARNING_COLOR = '\033[93m'
ERROR_COLOR = '\033[91m'
CRITICAL_COLOR = '\033[95m'

def LOG(msg:str, level:float=0):
    """
    Logs a message to the console.
    Helpful for debugging, as it prints it with color.

    :param msg: the message to log
    :param level: the level of the message
    """
    levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    # -- {label} -- {msg}
    # label is centered in a 10 character wide field
    # msg is left justified in a 50 character wide field
    # print with a color
    #print("-- [{0:^7}] -- {1:<50}".format(label, msg))
    COLOR = ""
    if level == LogLevel.DEBUG:
        COLOR = DEBUG_COLOR
    elif level == LogLevel.INFO:
        COLOR = INFO_COLOR
    elif level == LogLevel.WARNING:
        COLOR = WARNING_COLOR
    elif level == LogLevel.ERROR:
        COLOR = ERROR_COLOR
    elif level == LogLevel.CRITICAL:
        COLOR = CRITICAL_COLOR

    timestamp = time.strftime("%H:%M:%S", time.localtime())

    timestamp = "[" + timestamp + "] "

    print(COLOR + timestamp + "-- [{0:^7}] -- {1:<50}".format(levels[level], msg) + '\033[0m')