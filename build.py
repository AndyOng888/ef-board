"""Regenerate tasks.json for the public board from video-tools/TASKS.md.

    python build.py        -> writes tasks.json
    git add -A && git commit -m "board update" && git push

The board reads tasks.json only. There is no Google Sheet involved any more:
the task board in TASKS.md is the single source, and Claude updates it on request.
"""
import datetime
import io
import json
import re
from pathlib import Path

SRC = Path(r"C:/Users/Andy/video-tools/TASKS.md")
OUT = Path(__file__).parent / "tasks.json"

STATUS = {
    "\U0001f7e2": "done",       # green
    "\U0001f7e1": "active",     # yellow
    "\U0001f535": "waiting",    # blue
    "\u26aa": "idle",           # white
    "\u274c": "dropped",
}

# Tasks that have a countable job, for the little progress bars.
COUNTS = {
    "EFS-001": (10, 10),
    "EFS-002": (13, 13),
    "EFS-003": (56, 56),
    "EFS-009": (10, 10),
    "EFS-011": (0, 5),
}

ORDER = {"active": 0, "waiting": 1, "idle": 2, "done": 3, "dropped": 4}


def clean(cell):
    cell = cell.strip()
    cell = re.sub(r"\*\*(.+?)\*\*", r"\1", cell)
    cell = cell.replace("`", "")
    return cell.strip()


def main():
    text = io.open(SRC, encoding="utf-8").read()
    tasks = []
    for line in text.split("\n"):
        if not line.startswith("| EFS-"):
            continue
        parts = [c for c in line.split("|")][1:-1]
        if len(parts) < 5:
            continue
        uid, title, status, nxt, files = (clean(p) for p in parts[:5])
        key = next((v for k, v in STATUS.items() if k in status), "idle")
        done, total = COUNTS.get(uid, (0, 0))
        tasks.append({
            "uid": uid,
            "title": title,
            "status": key,
            "next": nxt,
            "files": "" if files in ("\u2014", "-", "") else files,
            "done": done,
            "total": total,
        })

    tasks.sort(key=lambda t: (ORDER.get(t["status"], 9), t["uid"]))
    stamp = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    payload = {"generated": stamp, "tasks": tasks}
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print("wrote {} with {} tasks".format(OUT, len(tasks)))


if __name__ == "__main__":
    main()
