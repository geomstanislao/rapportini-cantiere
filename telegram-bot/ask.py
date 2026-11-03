#!/usr/bin/env python3
"""Usato dagli agenti (via Bash) per parlare con Stanislao su Telegram.

  ask.py ask GARA "Domanda?" -o "Sì" -o "No" [--timeout 3600]   -> stampa la risposta
  ask.py notify GARA "Messaggio"                               -> invia e basta
  ask.py read GARA                                             -> messaggi non letti da Stanislao
Exit code 2 se scade il timeout.
"""
import argparse, json, sys, time, uuid
from common import QUEUE, write_json


def cmd_ask(a, wait=True):
    qid = uuid.uuid4().hex[:8]
    write_json(QUEUE / "inbox" / f"{qid}.json",
               {"id": qid, "gara": a.gara, "text": a.text, "options": a.option or [], "wait": wait})
    if not wait:
        return 0
    ans = QUEUE / "answers" / f"{qid}.json"
    start = time.time()
    while True:
        if ans.exists():
            print(json.loads(ans.read_text())["answer"])
            ans.unlink()
            return 0
        if a.timeout and time.time() - start > a.timeout:
            print("TIMEOUT", file=sys.stderr)
            return 2
        time.sleep(1.5)


def cmd_read(a):
    f = QUEUE / "messages" / f"{a.gara}.jsonl"
    if f.exists():
        for line in f.read_text().splitlines():
            print(json.loads(line)["text"])
        f.unlink()
    return 0


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    for name in ("ask", "notify"):
        sp = s.add_parser(name)
        sp.add_argument("gara")
        sp.add_argument("text")
        if name == "ask":
            sp.add_argument("-o", "--option", action="append")
            sp.add_argument("--timeout", type=int, default=0)
    s.add_parser("read").add_argument("gara")
    a = p.parse_args()
    sys.exit(cmd_ask(a, wait=a.cmd == "ask") if a.cmd != "read" else cmd_read(a))


if __name__ == "__main__":
    main()
