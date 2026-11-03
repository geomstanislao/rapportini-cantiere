import json, os
from pathlib import Path

BASE = Path(__file__).parent


def load_env():
    f = BASE / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


load_env()
QUEUE = Path(os.environ.get("BOT_QUEUE", BASE / "queue"))
for d in ("inbox", "sent", "answers", "messages"):
    (QUEUE / d).mkdir(parents=True, exist_ok=True)


def gare_file():
    return Path(os.environ.get("GARE_FILE", BASE / "gare.json"))


def load_gare():
    f = gare_file()
    return json.loads(f.read_text())["gare"] if f.exists() else {}


def save_gare(gare):
    gare_file().write_text(json.dumps({"gare": gare}, indent=2, ensure_ascii=False))


def write_json(path: Path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False))
    tmp.replace(path)
