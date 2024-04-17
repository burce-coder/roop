import time
import logging

import transform_task
from my_celery import app
from model import TransParam

logging.basicConfig(format='[%(filename)s:%(lineno)d] %(asctime)s - %(levelname)s : %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S %p',
                    level=logging.INFO)


transform_task.init()


@app.task
def transform(param: TransParam):
    logging.info(f'异步任务接口接收到请求，参数为{param}')
    start_time = time.time()
    res = transform_task.process(param["src"], param["tpl"], param["out"])
    logging.info(f"任务执行完成，耗时:{time.time() - start_time}")
    return res

