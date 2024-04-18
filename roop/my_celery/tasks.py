import json
import time
import logging

from roop.my_celery import transform_task, Log
from roop.my_celery.main import celery_app

Log.initialize()


class MyTask(celery_app.Task):
    def __init__(self):
        super().__init__()
    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.info(f'{task_id} failed: {exc}')
    # 任务成功时执行
    def on_success(self, retval, task_id, args, kwargs):
        pass
    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pass


@celery_app.task(base=MyTask)
def transform(**kwargs):
    logging.info(f'异步任务接口接收到请求，参数为{kwargs}')
    start_time = time.time()
    res = transform_task.process(kwargs["src"], kwargs["tpl"], kwargs["out"])
    logging.info(f"任务执行完成，耗时:{time.time() - start_time}")
    return {"res_code": res.value, "out": kwargs["out"], "out_url": kwargs["out_url"]}



