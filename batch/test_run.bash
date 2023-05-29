# find script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# navigate to module directory 
MOD_DIR="$SCRIPT_DIR/bourbon"
CD $MOD_DIR

export PYTHONPATH="$MOD_DIR"
echo $PYTHONPATH

VENV_PATH="$SCRIPT_DIR/bourbon/.venv/bin/activate"
SCRIPT_PATH="$SCRIPT_DIR/bourbon/bourbon/buffalo_trace.py"

source $VENV_PATH
python3 $SCRIPT_PATH