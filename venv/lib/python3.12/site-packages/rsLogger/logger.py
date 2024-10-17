import logging
import sys
import json
import shutil
import tempfile
import os
from logging import handlers


class Logger:
    """
    https://towardsdatascience.com/how-to-add-a-debug-mode-for-your-python-logging-mid-run-3c7330dc199d
    Singleton Logger class. This class is only instantiated ONCE. It is to keep a consistent
    criteria for the logger throughout the application if need be called upon.
    It serves as the criteria for initiating logger for modules. It creates child loggers.
    It's important to note these are child loggers as any changes made to the root logger
    can be done.

    
    this has been extended to include a debug mode which will save the json and html files to a temp folder
    
    """

    _instance = None

    def __new__(cls, log_folder=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.debug_mode = True
            cls.formatter = logging.Formatter(
                "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
            )
            cls.log_file = "application_log_file.log"
            if log_folder:
                cls.log_folder = log_folder
                if not os.path.exists(cls.log_folder):
                    os.mkdir(cls.log_folder)
            else:
                cls.log_folder = tempfile.mkdtemp()
            print(f"Log folder: {cls.log_folder}")
            if os.path.exists(cls.log_folder):
                shutil.rmtree(cls.log_folder)   
            os.mkdir(cls.log_folder)

        return cls._instance

    def get_console_handler(self):
        """Defines a console handler to come out on the console

        Returns:
            logging handler object : the console handler
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        console_handler.name = "consoleHandler"
        return console_handler

    def get_file_handler(self):
        # cannot write to file in cloud function - setting as console handler
        return self.get_console_handler()
        """Defines a file handler to come out on the console.

        Returns:
            logging handler object : the console handler
        """
        file_handler = handlers.RotatingFileHandler(
            self.log_file, maxBytes=5000, backupCount=1
        )
        file_handler.setFormatter(self.formatter)
        file_handler.name = "fileHandler"
        return file_handler

    def add_handlers(self, logger, handler_list: list):
        """Adds handlers to the logger, checks first if handlers exist to avoid
        duplication

        Args:
            logger: Logger to check handlers
            handler_list: list of handlers to add
        """
        existing_handler_names = []
        for existing_handler in logger.handlers:
            existing_handler_names.append(existing_handler.name)

        for new_handler in handler_list:
            if new_handler.name not in existing_handler_names:
                logger.addHandler(new_handler)

    def get_logger(self, logger_name: str):
        """Generates logger for use in the modules.
        Args:
            logger_name (string): name of the logger

        Returns:
            logger: returns logger for module
        """
        logger = logging.getLogger(logger_name)
        console_handler = self.get_console_handler()
        file_handler = self.get_file_handler()
        self.add_handlers(logger, [console_handler, file_handler])
        logger.propagate = False
        return logger
    
    def set_debug_mode(self, debug_mode: bool):
        """
        Function to set the root level logging to be debug level to be carried forward throughout
        Args:
            debug_mode (bool): debug mode initiation if true
        """
        if debug_mode:
            logging.root.setLevel(logging.DEBUG)
        else:
            logging.root.setLevel(logging.INFO)

        self.debug_mode = debug_mode
    
    def get_debug_mode(self):
        """
        Function to get the debug mode
        Returns:
            bool: debug mode
        """
        return self.debug_mode
    
    def json2file(self, obj, save_filename):
        if self.debug_mode:
            try:
                if not os.path.exists(self.log_folder):
                    os.mkdir(self.log_folder)
                save_path = os.path.join(self.log_folder, save_filename)
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(obj, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(e)
        else:
            pass

    def html2file(self, obj, save_filename):
        if self.debug_mode:
            try:
                if not os.path.exists(self.log_folder):
                    os.mkdir(self.log_folder)
                save_path = os.path.join(self.log_folder, save_filename)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(obj)
            except Exception as e:
                print(e)
        else:
            pass