"""
Run using the command:

python celery -A app.celeryapp.celery_worker.celery worker --concurrency=2 -E -l info


"""
from app import celeryapp, create_app

app = create_app(main_app=False)
celery = celeryapp.create_celery_app(app)
celeryapp.celery = celery

if celery:
    from app.tasks import broadcast_latest_info


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls the function every 1 second
    # sender.add_periodic_task(1, fetch_latest.s(1), name='testing beat')
    sender.add_periodic_task(1.0,
                             broadcast_latest_info.s(1),
                             name='check vib1_table')
    sender.add_periodic_task(1.0,
                             broadcast_latest_info.s(2),
                             name='check vib2_table')
    sender.add_periodic_task(1.0,
                             broadcast_latest_info.s(3),
                             name='check vib3_table')
    sender.add_periodic_task(1.0,
                             broadcast_latest_info.s(4),
                             name='check vib4_table')
    sender.add_periodic_task(1.0,
                             broadcast_latest_info.s(5),
                             name='check vib5_table')
    sender.add_periodic_task(1.0,
                             broadcast_latest_info.s(6),
                             name='check vib6_table')
