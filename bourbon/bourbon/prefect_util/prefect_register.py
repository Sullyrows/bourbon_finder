from bourbon.buffalo_trace import buffalo_trace_job
from prefect.deployments import Deployment

if __name__ == "__main__": 
    deployment = Deployment.build_from_flow(
        flow=buffalo_trace_job,
        name="buffalo_trace_run", 
        version=1, 
        work_queue_name="bourbon",
    )
    deployment.apply()