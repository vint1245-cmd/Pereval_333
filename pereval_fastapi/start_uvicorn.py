import os
import sys

sys.path.insert(0, os.getcwd())

from app.main import app
import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8001)
