# find script directory
RESTORE_DIR=$PWD
# SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
SCRIPTPATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPTPATH

# navigate to module directory 
PARENT_DIR="$(dirname "$SCRIPTPATH")"
PROJECT_DIR="$(dirname "$PARENT_DIR")"
echo $PARENT_DIR

# alias for directory
cd "$PARENT_DIR/bourbon"
echo "CURRENT DIRECTORY = $PWD"

# install poetry 
curl -sSL https://install.python-poetry.org | python3 -

# check poetry install 
poetry --version

poetry config virtualenvs.in-project true --local
poetry config virtualenvs.path "$PWD/.venv"

echo "Poetry installed! Saved to \"$PWD/.venv\""

cd $RESTORE_DIR