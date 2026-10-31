import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
