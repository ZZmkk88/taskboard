"""Live self-test for taskboard: boots a real uvicorn server on a scratch
database and walks the whole user flow over HTTP.

Run: .venv/bin/python tests/live_selftest.py
"""
import os
import subprocess
import sys
import tempfile
import time

import httpx

BASE = "http://127.0.0.1:8131"
http = httpx.Client(trust_env=False)
CHECKS = 0


def check(name, cond, extra=""):
    global CHECKS
    CHECKS += 1
    print(("PASS " if cond else "FAIL ") + name + (f" | {extra}" if extra else ""))
    if not cond:
        raise SystemExit(f"selftest failed at: {name}")


def main():
    tmp = tempfile.mkdtemp(prefix="tb-live-")
    env = dict(os.environ)
    env["TASKBOARD_DB_PATH"] = os.path.join(tmp, "live.db")
    env["PORT"] = "8131"
    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(50):
            try:
                if http.get(BASE + "/", timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.2)
        else:
            raise SystemExit("server did not come up")

        page = http.get(BASE + "/").text
        check("首页能打开且是 taskboard 页面", "taskboard" in page)

        res = http.post(BASE + "/api/login", json={"username": "admin", "password": "admin123"})
        check("默认账号登录成功", res.status_code == 200, res.text[:120])
        data = res.json()
        check("首次登录提示改密", data["must_change_password"] is True)
        h = {"Authorization": f"Bearer {data['token']}"}

        res = http.post(BASE + "/api/boards", json={"name": "自测看板"}, headers=h)
        check("建看板成功", res.status_code == 200, res.text[:120])
        board = res.json()
        titles = [c["title"] for c in board["columns"]]
        check("自带三列 待办/进行中/已完成", titles == ["待办", "进行中", "已完成"], str(titles))
        cols = {c["title"]: c for c in board["columns"]}

        res = http.post(BASE + f"/api/boards/{board['id']}/columns", json={"title": "待评审"}, headers=h)
        check("加一列成功", res.status_code == 200, res.text[:120])

        def add(col_id, **kw):
            body = {"title": kw.pop("title")}
            body.update(kw)
            r = http.post(BASE + f"/api/columns/{col_id}/cards", json=body, headers=h)
            assert r.status_code == 200, r.text
            return r.json()

        c1 = add(cols["待办"]["id"], title="写周报", tag="工作", tag_color="red", due_date="2026-12-31")
        c2 = add(cols["待办"]["id"], title="买咖啡豆")
        c3 = add(cols["待办"]["id"], title="约访谈")
        check("连建三张卡成功", all([c1["id"], c2["id"], c3["id"]]))

        res = http.post(BASE + f"/api/cards/{c1['id']}/move",
                        json={"to_column_id": cols["进行中"]["id"], "to_index": 0}, headers=h)
        check("卡片移到进行中", res.status_code == 200 and res.json()["column_id"] == cols["进行中"]["id"])

        res = http.post(BASE + f"/api/cards/{c1['id']}/move",
                        json={"to_column_id": cols["已完成"]["id"], "to_index": 0}, headers=h)
        check("卡片移到已完成", res.status_code == 200 and res.json()["column_id"] == cols["已完成"]["id"])

        res = http.post(BASE + f"/api/cards/{c3['id']}/move",
                        json={"to_column_id": cols["待办"]["id"], "to_index": 0}, headers=h)
        check("列内排序：约访谈提到最前", res.status_code == 200 and res.json()["position"] == 0)

        board = http.get(BASE + f"/api/boards/{board['id']}", headers=h).json()
        todo_titles = [c["title"] for c in board["columns"][0]["cards"]]
        check("待办顺序正确", todo_titles == ["约访谈", "买咖啡豆"], str(todo_titles))

        res = http.post(BASE + f"/api/cards/{c2['id']}/archive", headers=h)
        check("归档买咖啡豆", res.status_code == 200 and res.json()["is_archived"] is True)
        arch = http.get(BASE + f"/api/boards/{board['id']}/archived", headers=h).json()
        check("归档箱里有 1 张且记着原列", len(arch) == 1 and arch[0]["column_title"] == "待办")

        res = http.post(BASE + f"/api/cards/{c2['id']}/restore", headers=h)
        check("恢复归档卡", res.status_code == 200 and res.json()["is_archived"] is False)
        board = http.get(BASE + f"/api/boards/{board['id']}", headers=h).json()
        todo_titles = [c["title"] for c in board["columns"][0]["cards"]]
        check("恢复后回到待办末尾", todo_titles == ["约访谈", "买咖啡豆"], str(todo_titles))

        res = http.put(BASE + f"/api/boards/{board['id']}", json={"name": "自测看板·改名"}, headers=h)
        check("看板改名", res.status_code == 200 and res.json()["name"] == "自测看板·改名")

        print(f"\nALL {CHECKS} CHECKS PASSED")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
