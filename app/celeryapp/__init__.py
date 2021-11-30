from celery import Celery
import socketio

CELERY_TASK_LIST = [
    'application.tasks',
]

# db_session = None
celery = None


def create_celery_app(_app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's config.

    Wrap all tasks in the context of the Flask application.

    :param _app: Flask app
    :return: Celery app
    """
    # New Relic integration
    # if os.environ.get('NEW_RELIC_CELERY_ENABLED') == 'True':
    #     _app.initialize('celery')
    print(f'_app = {_app}')
    celery = Celery(_app.import_name,
                    broker=_app.config['CELERY_BROKER_URL'],
                    backend=_app.config['RESULT_BACKEND'],
                    include=CELERY_TASK_LIST)
    celery.conf.update(_app.config)
    # always_eager = _app.config['TESTING'] or False
    # celery.conf.update({'CELERY_ALWAYS_EAGER': always_eager,
    #                     'CELERY_RESULT_BACKEND': f"db+{_app.config['SQLALCHEMY_DATABASE_URI']}"})
    # if _app.config['CELERY_REDIS_USE_SSL']:
    #     broker_use_ssl = {'ssl_cert_reqs': ssl.CERT_NONE}
    #     celery.conf.update({'BROKER_USE_SSL': broker_use_ssl})

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # Sentry error tracking
    # minion.init_celery_client(_app)

    return celery

# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls the function every 1 second
#     sender.add_periodic_task(1, test.s('hello'), name='testing beat')
