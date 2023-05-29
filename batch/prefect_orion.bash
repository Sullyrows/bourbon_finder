# find script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# navigate to module directory 
MOD_DIR="$SCRIPT_DIR/bourbon/"
CD $MOD_DIR

prefect orion start