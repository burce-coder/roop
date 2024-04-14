#!/usr/bin/env python3
import os
import shutil
import sys

import cv2
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from roop.core import decode_execution_providers, suggest_execution_threads, limit_resources
from roop.face_analyser import get_one_face
from roop.predictor import predict_image
from roop.processors.frame.core import get_frame_processors_modules
from roop.utilities import clean_temp, is_image
from enum import IntEnum
from dotenv import load_dotenv
import roop.globals

load_dotenv()

if any(arg.startswith('--execution-provider') for arg in sys.argv):
    os.environ['OMP_NUM_THREADS'] = '1'

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

exe_provider = os.getenv("EXECUTION-PROVIDER", "cuda").split(',')
roop.globals.execution_providers = decode_execution_providers(exe_provider)
print(f"{roop.globals.execution_providers}")
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


class TransParam(BaseModel):
    src: str
    tpl: str
    out: str


class TransRes(IntEnum):
    ok = 0
    file_format_err = -1
    no_face = -2
    image_error = -3
    transform_error = -4


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


def pre_start(src: str) -> TransRes:
    if not is_image(src):
        return TransRes.file_format_err
    elif not get_one_face(cv2.imread(src)):
        return TransRes.no_face
    return TransRes.ok


def process(src: str, tpl: str, out: str) -> TransRes:
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


@app.post("/transform")
async def transform(param: TransParam):
    res = process(param.src, param.tpl, param.out)
    return {"res": res}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)

