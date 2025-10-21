from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .calculations import Parameters, compute_results

app = FastAPI(title="Comparateur de chauffage")

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    defaults = Parameters()
    context = {
        "request": request,
        "defaults": defaults.model_dump(),
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/api/calculate")
async def calculate(params: Parameters) -> dict:
    return compute_results(params)
