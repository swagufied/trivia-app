from celery import shared_task

@shared_task
def test(s):
	print('test triggered')
	return 1