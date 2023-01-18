from bourbon.buffalo_trace import buffalo_trace_job
from prefect.deployments import Deployment
from prefect.filesystems import S3
from prefect.orion.schemas.schedules import IntervalSchedule
import datetime as dt

# create a schedule 
i_sched = IntervalSchedule(
    interval = dt.timedelta(minutes=5)
)

deployment = Deployment.build_from_flow(
    flow = buffalo_trace_job,
    name = "Buffalo Trace Job",
    version = 1,
    work_queue_name = "bourbon",
    schedule = i_sched
)
deployment.apply()