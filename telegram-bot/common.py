import json, os
from pathlib import Path

BASE = Path(__file__).parent
QUEUE = Path(os.environ.get("BOT_QUEUE", BASE / "queue"))
for d in ("inbox", "sent", "answers", "messages"):
    (QUEUE / d).mkdir(parents=True, exist_ok=True)


def load_env():
    f = BASE / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def load_gare():
    f = BASE / "gare.json"
    return json.loads(f.read_text())["gare"] if f.exists() else {}


def save_gare(gare):
    (BASE / "gare.json").write_text(json.dumps({"gare": gare}, indent=2, ensure_ascii=False))


def write_json(path: Path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False))
    tmp.replace(path)
