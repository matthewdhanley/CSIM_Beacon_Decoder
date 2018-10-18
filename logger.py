import logging
import os


class Logger:
    def __init__(self):
        self.create_log()

    def create_log(self):
        """
        For debugging and informational purposes.
        """
        self.ensure_log_folder_exists()
        log = logging.getLogger('csim_beacon_decoder_debug')

        if not self.logger_exists(log):
            handler = logging.FileHandler(self.create_log_filename())
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            log.addHandler(handler)
            log.setLevel(logging.DEBUG)

        return log

    @staticmethod
    def logger_exists(log):
        if len(log.handlers) > 0:
            return True
        else:
            return False

    @staticmethod
    def ensure_log_folder_exists():
        if not os.path.exists(os.path.join(os.path.expanduser("~"), "CSIM_Beacon_Decoder", "log")):
            os.makedirs(os.path.join(os.path.expanduser("~"), "CSIM_Beacon_Decoder", "log"))

    @staticmethod
    def create_log_filename():
        return os.path.join(os.path.expanduser("~"), "CSIM_Beacon_Decoder", "log", "csim_beacon_decoder_debug.log")
