import os
from celery import Celery
from driverapp import db, MEDIA_FOLDER, REDIS_URL
from driverapp.models import Scan, Events
from driverapp.helpers.script import NessusDriverScript


#################################################
#   celery -A tasks worker -B --loglevel=info   #
#   celery -A tasks purge                       # 
#################################################

CELERYBEAT_SCHEDULE = {
    "runs-every-500-seconds": {
        "task": "nessus_add_scan",
        "schedule": 300.0,
        "args": (),
    }
}

app = Celery('tasks')

CELERY_ROUTES = {
    'tasks': {'queue': 'nessus_driver'},
}

app.conf.update(
    result_expires=60,
    task_acks_late=True,

    # BROKER URL for docker
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
)

app.conf.beat_schedule.update(CELERYBEAT_SCHEDULE)

app.conf.task_default_queue = 'default'

app.conf.task_routes = CELERY_ROUTES


@app.task(name="nessus_add_scan")
def nessus_add_scan():
    scans = Scan.query.filter_by(status="Running").\
            order_by(Scan.event_id.asc()).first()

    if scans:
        nessus_script = NessusDriverScript(scans)
        scan_status = nessus_script.get_status()

        if bool(scan_status):
            status = ['Queued', 'Running', 'Failed']
            check_status = Scan.query.filter(Scan.status.in_(status)).\
                filter_by(event_id=scans.event_id).count()

            if not check_status:
                events = Events.query.filter_by(id=scans.event_id).first()
                events.event_status = 'Completed'
                db.session.commit()
            create_scan()
    else:
        create_scan()


def create_scan():
    try:
        scan = Scan.query.filter_by(status="Queued").\
            order_by(Scan.event_id.asc()).first()
    except Exception as e:
        print 'create_scan() :: exception :: ', e
        scan = None

    if scan:
        scan.scan_message = 'Scan is {}'.format(scan.status)
        events = Events.query.filter_by(id=scan.event_id).first()
        events.event_status = 'Running'
        nessus_script = NessusDriverScript(scan)
        nessus_script.add_data()
        db.session.commit()
