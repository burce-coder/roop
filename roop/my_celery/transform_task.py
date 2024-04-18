import logging
import os
import shutil

import cv2
from dotenv import load_dotenv

import roop.globals
from roop.core import decode_execution_providers, suggest_execution_threads, limit_resources
from roop.face_analyser import get_one_face
from roop.my_celery.model import TransRes
from roop.predictor import predict_image
from roop.processors.frame.core import get_frame_processors_modules
from roop.utilities import is_image, clean_temp

CELERY_TRANSFORM_INIT = False


def init():
    global CELERY_TRANSFORM_INIT
    if CELERY_TRANSFORM_INIT:
        return
    CELERY_TRANSFORM_INIT = True
    logging.info("transform_task.init()")
    load_dotenv()
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    exe_provider = os.getenv("EXECUTION_PROVIDER", "cuda").split(',')
    roop.globals.execution_providers = decode_execution_providers(exe_provider)
    roop.globals.headless = True
    roop.globals.keep_fps = True
    roop.globals.keep_frames = True
    roop.globals.skip_audio = True
    roop.globals.many_faces = False
    roop.globals.reference_face_position = 0
    roop.globals.reference_frame_number = 0
    roop.globals.similar_face_distance = 0.85
    roop.globals.temp_frame_format = 'jpg'
    roop.globals.temp_frame_quality = 0
    roop.globals.output_video_encoder = 'libx264'
    roop.globals.output_video_quality = 35
    roop.globals.execution_threads = suggest_execution_threads()

    limit_resources()


def pre_start(src: str) -> TransRes:
    if not is_image(src):
        return TransRes.file_format_err
    elif not get_one_face(cv2.imread(src)):
        return TransRes.no_face
    return TransRes.ok


def process(src: str, tpl: str, out: str) -> TransRes:
    init()
    res = pre_start(src)
    if res != TransRes.ok:
        return res

    if predict_image(tpl):
        clean_temp(tpl)
        return TransRes.image_error

    shutil.copy2(tpl, out)
    # process frame
    for frame_processor in get_frame_processors_modules(['face_swapper', 'face_enhancer']):
        frame_processor.process_image(src, out, out)
        frame_processor.post_process()
    # validate image
    if is_image(tpl):
        return TransRes.ok
    else:
        return TransRes.transform_error
