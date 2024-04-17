# 主程序
from celery import Celery

app = Celery("my_celery")
app.config_from_object("celery_config")

# 加载任务
# 参数必须必须是一个列表，里面的每一个任务都是任务的路径名称
# app.autodiscover_tasks(["任务1","任务2"]),因为我的目录下只有一个tasks.py，
# 如果你的目录结构下有多个tasks.py,结构类似task1/tasks.py，task2/tasks.py
# 那这里就应该app.autodiscover_tasks(["my_celery.task1", "my_celery.task2"])
app.autodiscover_tasks(["my_celery"])

# 启动Celery的命令
# 强烈建议切换目录到my_celery根目录下启动
# celery -A my_celery.main worker --loglevel=info
# celery -A my_celery.main worker -Q celery --loglevel=info -c 1 #指定消费不同的队列
