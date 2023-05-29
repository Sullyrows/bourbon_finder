# find script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PY_SCRIPT="$SCRIPT_DIR/bourbon/bourbon/prefect_util/prefect_register.py"
PY_EXE="$SCRIPT_DIR/bourbon/.venv/bin/python3"

# navigate to module directory 
MOD_DIR="$SCRIPT_DIR/bourbon/"
CD $MOD_DIR

source "$SCRIPT_DIR/bourbon/.venv/bin/activate"
export PYTHONPATH="$MOD_DIR"

$PY_EXE $PY_SCRIPT

# start agent for work queue bourbon
prefect agent start -q bourbon