# scripts/serve_api.py
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from app.api import create_app

# ✅ use new model + metadata
app = create_app("models/model.pkl", "models/metadata.json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)