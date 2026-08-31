from fastapi import FastAPI

app = FastAPI(title="AstroAssistant")


@app.get("/health")
def health():
    return {"status": "ok"}
