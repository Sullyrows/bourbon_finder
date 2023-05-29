# find script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# navigate to module directory 
MOD_DIR="$SCRIPT_DIR/bourbon/"
SCRIPT_PATH="$SCRIPT_DIR/bourbon/bourbon/buffalo_trace.py"
MY_YAML="$SCRIPT_DIR/buffalo_trace_job-deployment.yaml"
CD $MOD_DIR

export PYTHONPATH="$MOD_DIR"

# start agent for work queue bourbon
prefect deployment build $SCRIPT_PATH:buffalo_trace_job -n buffalo_trace_remote -q test
prefect agent start -q bourbon
prefect deployment apply $MY_YAML
prefect agent start -q test