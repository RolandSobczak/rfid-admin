cd src/backend
source poetry shell
export PYTHONPATH="$PWD:$PYTHONPATH"
export INSIDE_DOCKER=False
fastapi dev main.py

