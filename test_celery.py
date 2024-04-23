from celery import Celery
app = Celery(broker='redis://127.0.0.1:6379/1', backend='redis://127.0.0.1:6379/2')
app.send_task("roop.my_celery.tasks.transform", kwargs={'src': 's1.jpg', 'tpl': 't1.jpg', 'out': 'o1.jpg'})
# transform.delay({'trans_id': '12345', 'src': 's1.jpg', 'tpl': 't1.jpg', 'out': 'o1.jpg'})
