import os
from dotenv import load_dotenv
load_dotenv()


broker_url = 'redis://127.0.0.1:6379/1'
result_backend = 'redis://127.0.0.1:6379/2'

# 结果保存时间(秒)
result_expires = 6*60*60

# 追踪状态
task_track_started = True

# celery升到5.3后使用原来的启动命令会出警告，加上这个配置后就不会了
broker_connection_retry_on_startup = True

# 下面两个控制时区的，但结果存储数时间仍为utc时间
enable_utc = True
timezone = 'Asia/Shanghai'

# 如果将此设置为None，将永远重连
broker_connection_max_retries = None

# 设置优先级队列列表数量(针对redis，因为如果中间件为redis的话，如果同一个任务设置10个优先级的话，
# redis会默认将任务列表根据你设置的任务优先级动态调整列表数，比如你设置了10个优先级不同的任务，
# redis默认不会生成10个任务列表，可能会生成3个优先级任务列表，就变成了1～3优先级为一个，4～6为一个，7～9为一个
# 这种情况后，1～3优先级里的任务设置就不成立了，就可能会出现3优先级任务执行优先于1的，这时候任务的执行顺序就会完全按照任务进入队列的顺序，
# 当然priority_steps也不是无限设置的，好像最大为10)
# 当然我们这里并不要设置10个优先级，但这并不影响
# broker_transport_options = {
#     'priority_steps': list(range(10)),
# }
accept_content = ['json']
result_accept_content = ['json']
