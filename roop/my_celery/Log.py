import logging
import os


def initialize():
    work_folder = os.path.dirname(os.path.dirname(__file__))
    logs_folder = os.path.join(work_folder, 'logs')
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    logfile = os.path.join(logs_folder, 'roop-celery.log')
    logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')