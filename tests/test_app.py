"""Automated tests for taskboard. Run: .venv/bin/python -m pytest tests/ -q"""
import hashlib
import os
import sqlite3
import tempfile

import pytest

_tmp = tempfile.mkdtemp(prefix="tb-test-")
os.environ["TASKBOARD_DB_PATH"] = os.path.join(_tmp, "test.db")
os.environ["TB_INITIAL_USERNAME"] = "admin"
os.environ["TB_INITIAL_PASSWORD"] = "admin123"

import app as appmod  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(appmod.app) as c:
        yield c


def do_login(client, password="admin123"):
    res = client.post("/api/login", json={"username": "admin", "password": password})
    assert res.status_code == 200, res.text
    return res.json()


@pytest.fixture(scope="module")
def auth(client):
    data = do_login(client)
    return {"Authorization": f"Bearer {data['token']}"}


def make_board(client, auth, name="项目甲"):
    res = client.post("/api/boards", json={"name": name}, headers=auth)
    assert res.status_code == 200, res.text
    return res.json()


def col_by_title(board, title):
    for col in board["columns"]:
        if col["title"] == title:
            return col
    raise AssertionError(f"column {title} not found in {board}")


def add_card(client, auth, column_id, **kw):
    body = {"title": kw.pop("title", "卡片")}
    body.update(kw)
    res = client.post(f"/api/columns/{column_id}/cards", json=body, headers=auth)
    assert res.status_code == 200, res.text
    return res.json()


def get_board(client, auth, board_id):
    res = client.get(f"/api/boards/{board_id}", headers=auth)
    assert res.status_code == 200, res.text
    return res.json()


# ---------------------------------------------------------------- auth ----

def test_login_wrong_password(client):
    res = client.post("/api/login", json={"username": "admin", "password": "nope"})
    assert res.status_code == 401


def test_login_ok_and_must_change(client):
    data = do_login(client)
    assert data["token"]
    assert data["must_change_password"] is True


def test_unauthenticated_rejected(client):
    assert client.get("/api/boards").status_code == 401
    assert client.get("/api/me").status_code == 401


def test_change_password_roundtrip(client, auth):
    res = client.post(
        "/api/change-password",
        json={"old_password": "wrong", "new_password": "newpass123"},
        headers=auth,
    )
    assert res.status_code == 400
    res = client.post(
        "/api/change-password",
        json={"old_password": "admin123", "new_password": "short"},
        headers=auth,
    )
    assert res.status_code == 400
    res = client.post(
        "/api/change-password",
        json={"old_password": "admin123", "new_password": "newpass123"},
        headers=auth,
    )
    assert res.status_code == 200
    data = do_login(client, "newpass123")
    assert data["must_change_password"] is False
    # 用最初那个（仍有效的）会话把密码改回去，模块级 auth 夹具才能继续用
    res = client.post(
        "/api/change-password",
        json={"old_password": "newpass123", "new_password": "admin123"},
        headers=auth,
    )
    assert res.status_code == 200
    assert client.get("/api/me", headers=auth).status_code == 200


def test_session_tokens_stored_hashed(client):
    data = do_login(client)
    token = data["token"]
    conn = sqlite3.connect(os.environ["TASKBOARD_DB_PATH"])
    try:
        stored = {r[0] for r in conn.execute("SELECT token FROM sessions").fetchall()}
    finally:
        conn.close()
    assert stored, "sessions 表应有记录"
    assert token not in stored, "明文令牌不应落库"
    assert hashlib.sha256(token.encode("utf-8")).hexdigest() in stored
    headers = {"Authorization": f"Bearer {token}"}
    # 哈希入库不影响正常使用与退出
    assert client.get("/api/me", headers=headers).status_code == 200
    assert client.post("/api/logout", headers=headers).status_code == 200
    assert client.get("/api/me", headers=headers).status_code == 401


def test_change_password_revokes_other_sessions(client, auth):
    other = do_login(client)["token"]
    other_headers = {"Authorization": f"Bearer {other}"}
    assert client.get("/api/me", headers=other_headers).status_code == 200
    res = client.post(
        "/api/change-password",
        json={"old_password": "admin123", "new_password": "tmppass123"},
        headers=auth,
    )
    assert res.status_code == 200
    # 其他会话已失效，当前会话仍可用
    assert client.get("/api/me", headers=other_headers).status_code == 401
    assert client.get("/api/me", headers=auth).status_code == 200
    # 改回去，同样用当前会话，它自己不受影响
    res = client.post(
        "/api/change-password",
        json={"old_password": "tmppass123", "new_password": "admin123"},
        headers=auth,
    )
    assert res.status_code == 200
    assert client.get("/api/me", headers=auth).status_code == 200


# --------------------------------------------------------------- boards ----

def test_create_board_has_default_columns(client, auth):
    board = make_board(client, auth, "默认列看板")
    titles = [c["title"] for c in board["columns"]]
    assert titles == ["待办", "进行中", "已完成"]
    assert [c["position"] for c in board["columns"]] == [0, 1, 2]


def test_board_list_and_rename(client, auth):
    board = make_board(client, auth, "待改名")
    res = client.get("/api/boards", headers=auth)
    mine = [b for b in res.json() if b["id"] == board["id"]]
    assert mine and mine[0]["column_count"] == 3 and mine[0]["card_count"] == 0
    res = client.put(
        f"/api/boards/{board['id']}", json={"name": "新名字"}, headers=auth
    )
    assert res.status_code == 200 and res.json()["name"] == "新名字"
    res = client.post("/api/boards", json={"name": "   "}, headers=auth)
    assert res.status_code == 400
    assert client.get("/api/boards/999999", headers=auth).status_code == 404


# -------------------------------------------------------------- columns ----

def test_column_crud_and_reorder(client, auth):
    board = make_board(client, auth, "列操作")
    bid = board["id"]
    res = client.post(f"/api/boards/{bid}/columns", json={"title": "待评审"}, headers=auth)
    assert res.status_code == 200
    new_col = res.json()
    assert new_col["position"] == 3
    res = client.put(f"/api/columns/{new_col['id']}", json={"title": "评审中"}, headers=auth)
    assert res.status_code == 200 and res.json()["title"] == "评审中"
    # reorder: move the new column to the front
    ids = [c["id"] for c in board["columns"]] + [new_col["id"]]
    ids = [new_col["id"]] + ids[:-1]
    res = client.post(f"/api/boards/{bid}/columns/reorder", json={"column_ids": ids}, headers=auth)
    assert res.status_code == 200
    titles = [c["title"] for c in res.json()["columns"]]
    assert titles[0] == "评审中"
    # incomplete reorder data is rejected
    res = client.post(f"/api/boards/{bid}/columns/reorder", json={"column_ids": ids[:-1]}, headers=auth)
    assert res.status_code == 400
    # delete the column
    res = client.delete(f"/api/columns/{new_col['id']}", headers=auth)
    assert res.status_code == 200
    after = get_board(client, auth, bid)
    assert [c["title"] for c in after["columns"]] == ["待办", "进行中", "已完成"]
    assert [c["position"] for c in after["columns"]] == [0, 1, 2]


def test_delete_column_cascades_cards(client, auth):
    board = make_board(client, auth, "删列连卡")
    todo = col_by_title(board, "待办")
    add_card(client, auth, todo["id"], title="会没的卡")
    res = client.delete(f"/api/columns/{todo['id']}", headers=auth)
    assert res.status_code == 200
    after = get_board(client, auth, board["id"])
    assert after["card_count"] == 0


# ---------------------------------------------------------------- cards ----

def test_card_crud_and_validation(client, auth):
    board = make_board(client, auth, "卡片操作")
    todo = col_by_title(board, "待办")
    card = add_card(
        client, auth, todo["id"],
        title="写方案", description="初稿", tag="工作", tag_color="red", due_date="2026-11-01",
    )
    assert card["tag"] == "工作" and card["tag_color"] == "red"
    assert card["due_date"] == "2026-11-01" and card["position"] == 0
    # validation failures
    assert client.post(f"/api/columns/{todo['id']}/cards", json={"title": " "}, headers=auth).status_code == 400
    assert client.post(f"/api/columns/{todo['id']}/cards", json={"title": "x", "due_date": "2026-13-40"}, headers=auth).status_code == 400
    assert client.post(f"/api/columns/{todo['id']}/cards", json={"title": "x", "due_date": "11/01/2026"}, headers=auth).status_code == 400
    assert client.post(f"/api/columns/{todo['id']}/cards", json={"title": "x", "tag_color": "neon"}, headers=auth).status_code == 400
    # update
    res = client.put(
        f"/api/cards/{card['id']}",
        json={"title": "写方案 v2", "description": "", "tag": "", "tag_color": "blue", "due_date": ""},
        headers=auth,
    )
    assert res.status_code == 200
    assert res.json()["title"] == "写方案 v2" and res.json()["due_date"] == ""
    # delete
    assert client.delete(f"/api/cards/{card['id']}", headers=auth).status_code == 200
    after = get_board(client, auth, board["id"])
    assert after["card_count"] == 0


def test_card_move_across_columns(client, auth):
    board = make_board(client, auth, "跨列移动")
    todo = col_by_title(board, "待办")
    doing = col_by_title(board, "进行中")
    a = add_card(client, auth, todo["id"], title="甲")
    b = add_card(client, auth, todo["id"], title="乙")
    res = client.post(
        f"/api/cards/{a['id']}/move",
        json={"to_column_id": doing["id"], "to_index": 0},
        headers=auth,
    )
    assert res.status_code == 200
    assert res.json()["column_id"] == doing["id"] and res.json()["position"] == 0
    after = get_board(client, auth, board["id"])
    todo_after = col_by_title(after, "待办")
    assert [c["title"] for c in todo_after["cards"]] == ["乙"]
    assert todo_after["cards"][0]["position"] == 0
    doing_after = col_by_title(after, "进行中")
    assert [c["title"] for c in doing_after["cards"]] == ["甲"]
    # moving back with an oversized index appends at the end
    res = client.post(
        f"/api/cards/{a['id']}/move",
        json={"to_column_id": todo["id"], "to_index": 999},
        headers=auth,
    )
    assert res.status_code == 200 and res.json()["position"] == 1


def test_card_reorder_within_column(client, auth):
    board = make_board(client, auth, "列内排序")
    todo = col_by_title(board, "待办")
    a = add_card(client, auth, todo["id"], title="A")
    add_card(client, auth, todo["id"], title="B")
    add_card(client, auth, todo["id"], title="C")
    res = client.post(
        f"/api/cards/{a['id']}/move",
        json={"to_column_id": todo["id"], "to_index": 2},
        headers=auth,
    )
    assert res.status_code == 200
    after = get_board(client, auth, board["id"])
    cards = col_by_title(after, "待办")["cards"]
    assert [c["title"] for c in cards] == ["B", "C", "A"]
    assert [c["position"] for c in cards] == [0, 1, 2]


def test_move_to_other_board_rejected(client, auth):
    b1 = make_board(client, auth, "看板一")
    b2 = make_board(client, auth, "看板二")
    card = add_card(client, auth, col_by_title(b1, "待办")["id"], title="不能乱跑")
    res = client.post(
        f"/api/cards/{card['id']}/move",
        json={"to_column_id": col_by_title(b2, "待办")["id"], "to_index": 0},
        headers=auth,
    )
    assert res.status_code == 400


# -------------------------------------------------------------- archive ----

def test_archive_and_restore(client, auth):
    board = make_board(client, auth, "归档测试")
    todo = col_by_title(board, "待办")
    a = add_card(client, auth, todo["id"], title="要归档的")
    add_card(client, auth, todo["id"], title="留着的")
    res = client.post(f"/api/cards/{a['id']}/archive", headers=auth)
    assert res.status_code == 200 and res.json()["is_archived"] is True
    after = get_board(client, auth, board["id"])
    assert [c["title"] for c in col_by_title(after, "待办")["cards"]] == ["留着的"]
    # archived cards cannot be moved
    res = client.post(
        f"/api/cards/{a['id']}/move",
        json={"to_column_id": todo["id"], "to_index": 0},
        headers=auth,
    )
    assert res.status_code == 400
    # archived list
    res = client.get(f"/api/boards/{board['id']}/archived", headers=auth)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1 and items[0]["title"] == "要归档的"
    assert items[0]["column_title"] == "待办"
    # restore -> appended at the end of its original column
    res = client.post(f"/api/cards/{a['id']}/restore", headers=auth)
    assert res.status_code == 200
    assert res.json()["is_archived"] is False and res.json()["position"] == 1
    after = get_board(client, auth, board["id"])
    assert [c["title"] for c in col_by_title(after, "待办")["cards"]] == ["留着的", "要归档的"]
    assert client.get(f"/api/boards/{board['id']}/archived", headers=auth).json() == []


def test_delete_board(client, auth):
    board = make_board(client, auth, "要删的看板")
    add_card(client, auth, col_by_title(board, "待办")["id"], title="陪葬卡")
    assert client.delete(f"/api/boards/{board['id']}", headers=auth).status_code == 200
    assert client.get(f"/api/boards/{board['id']}", headers=auth).status_code == 404
