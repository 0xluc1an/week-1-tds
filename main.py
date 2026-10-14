from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

DEFAULTS = {"port": 8000, "workers": 1, "debug": False,
            "log_level": "info", "api_key": "default-secret-000"}
YAML = {"port": 8992, "workers": 2, "log_level": "error",
        "api_key": "key-kkmcbrs21i"}
DOTENV = {"APP_LOG_LEVEL": "info", "APP_API_KEY": "key-vcx8s44onc"}
OS_ENV = {"APP_PORT": "8935", "APP_LOG_LEVEL": "info"}

ALIASES = {"num_workers": "workers"}

def norm(key):
    key = key.strip().lower()
    if key.startswith("app_"):
        key = key[4:]
    return ALIASES.get(key, key)

def layer(d):
    return {norm(k): v for k, v in d.items()}

def to_bool(v):
    return str(v).strip().lower() in ("true", "1", "yes", "on")

def coerce(cfg):
    for k in ("port", "workers"):
        if k in cfg:
            try:
                cfg[k] = int(cfg[k])
            except (ValueError, TypeError):
                pass
    if "debug" in cfg:
        cfg["debug"] = to_bool(cfg["debug"])
    for k, v in cfg.items():
        if k not in ("port", "workers", "debug"):
            cfg[k] = str(v)
    return cfg

@app.get("/effective-config")
def effective_config(request: Request):
    cfg = {}
    for d in (DEFAULTS, YAML, DOTENV, OS_ENV):
        cfg.update(layer(d))
    for item in request.query_params.getlist("set"):
        if "=" in item:
            k, v = item.split("=", 1)
            cfg[norm(k)] = v
    cfg = coerce(cfg)
    cfg["api_key"] = "****"
    return cfg
