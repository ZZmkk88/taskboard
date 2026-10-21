"""taskboard: a lightweight self-hosted kanban board.

Boards hold ordered columns; cards live in a column, can be dragged (or
button-moved) between columns, reordered inside a column, and archived.
Single-file FastAPI backend + SQLite + one static page.
Design notes live in NOTES.md.
"""
import hashlib
import os
import re
import secrets
import sqlite3
import sys
import time
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get("TASKBOARD_DB_PATH", str(BASE_DIR / "data" / "taskboard.db"))
TOKEN_TTL_SECONDS = 24 * 60 * 60
INITIAL_USERNAME = os.environ.get("TB_INITIAL_USERNAME", "admin")
INITIAL_PASSWORD = os.environ.get("TB_INITIAL_PASSWORD", "admin123")
HOST = os.environ.get("TASKBOARD_HOST", "127.0.0.1")

MAX_BOARD_NAME = 100
MAX_COLUMN_TITLE = 100
MAX_CARD_TITLE = 200
MAX_CARD_DESC = 5000
MAX_TAG = 30
MAX_PASSWORD = 1024
DEFAULT_COLUMNS = ["待办", "进行中", "已完成"]
TAG_COLORS = ["gray", "red", "orange", "yellow", "green", "blue", "purple", "pink"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="taskboard",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    if request.url.path.startswith("/api/"):
        # 接口返回不进任何缓存：令牌在请求头里，退出后也不留可复读的响应
        response.headers["Cache-Control"] = "no-store"
    return response


# ---------------------------------------------------------------------------
# small utilities
# ---------------------------------------------------------------------------

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def _clean_text(value: str, max_len: int, label: str) -> str:
    value = (value or "").replace("\x00", "").strip()
    if not value:
        raise HTTPException(status_code=400, detail=f"{label}不能为空")
    if len(value) > max_len:
        raise HTTPException(status_code=400, detail=f"{label}太长了")
    return value


def _clean_due_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if not DATE_RE.match(value):
        raise HTTPException(status_code=400, detail="截止日期格式应为 YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=400, detail="截止日期不是有效日期")
    return value


def _clean_tag_color(value: str) -> str:
    value = (value or "").strip().lower()
    if not value:
        return "blue"
    if value not in TAG_COLORS:
        raise HTTPException(status_code=400, detail="标签颜色不在可选范围内")
    return value


# ---------------------------------------------------------------------------
# database
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 200_000
    ).hex()


# 用户不存在时的时序填充：固定哑盐+哑哈希，让"用户不存在"和"密码错误"耗时一致
_DUMMY_SALT = "0" * 32
_DUMMY_HASH = hash_password("dummy-password", _DUMMY_SALT)


def _validate_initial_password(pw: str) -> None:
    """默认口令入库前校验：空串和超长都直接拒绝并说明原因，不静默写入。"""
    if not pw or not pw.strip():
        print("错误：TB_INITIAL_PASSWORD 不能为空（未设置初始口令）", file=sys.stderr)
        raise SystemExit(2)
    if len(pw) > MAX_PASSWORD:
        print(f"错误：TB_INITIAL_PASSWORD 超过 {MAX_PASSWORD} 位", file=sys.stderr)
        raise SystemExit(2)


def init_db() -> None:
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                must_change_password INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                expires_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS board_columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                position INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                column_id INTEGER NOT NULL REFERENCES board_columns(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                tag TEXT NOT NULL DEFAULT '',
                tag_color TEXT NOT NULL DEFAULT 'blue',
                due_date TEXT NOT NULL DEFAULT '',
                position INTEGER NOT NULL DEFAULT 0,
                is_archived INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        row = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
        if row["c"] == 0:
            _validate_initial_password(INITIAL_PASSWORD)
            salt = secrets.token_hex(16)
            conn.execute(
                "INSERT INTO users (username, password_hash, salt, must_change_password, created_at)"
                " VALUES (?, ?, ?, 1, ?)",
                (INITIAL_USERNAME, hash_password(INITIAL_PASSWORD, salt), salt, iso(utcnow())),
            )
        # 顺手清掉过期会话行（查询时本来就过滤，这里只是防止表无限变长）
        conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (time.time(),))
        conn.commit()
    finally:
        conn.close()




# ---------------------------------------------------------------------------
# auth (same proven pattern as the team's earlier projects)
# ---------------------------------------------------------------------------

class LoginIn(BaseModel):
    username: str
    password: str


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str


def current_user(request: Request) -> sqlite3.Row:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = auth[len("Bearer "):].strip()
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id"
            " WHERE s.token = ? AND s.expires_at > ?",
            (_token_hash(token), time.time()),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
        return row
    finally:
        conn.close()


@app.post("/api/login")
def login(body: LoginIn):
    if len(body.password) > MAX_PASSWORD:
        raise HTTPException(status_code=400, detail="密码太长了")
    init_db()
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (body.username.strip(),)
        ).fetchone()
        if not user:
            # 用户不存在时也做一次等长哈希，避免用响应时序区分"用户不存在"和"密码错误"
            secrets.compare_digest(hash_password(body.password, _DUMMY_SALT), _DUMMY_HASH)
            raise HTTPException(status_code=401, detail="用户名或密码不正确")
        if not secrets.compare_digest(
            hash_password(body.password, user["salt"]), user["password_hash"]
        ):
            raise HTTPException(status_code=401, detail="用户名或密码不正确")
        token = secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
            (_token_hash(token), user["id"], time.time() + TOKEN_TTL_SECONDS),
        )
        conn.commit()
        return {
            "token": token,
            "username": user["username"],
            "must_change_password": bool(user["must_change_password"]),
        }
    finally:
        conn.close()


@app.post("/api/logout")
def logout(request: Request, user: sqlite3.Row = Depends(current_user)):
    token = request.headers.get("Authorization", "")[len("Bearer "):].strip()
    conn = get_db()
    try:
        conn.execute("DELETE FROM sessions WHERE token = ?", (_token_hash(token),))
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


def _token_hash(token: str) -> str:
    """会话令牌入库前先做 SHA-256：库文件泄露时无法直接拿去冒充在线会话。"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[len("Bearer "):].strip()
    return ""


@app.post("/api/change-password")
def change_password(body: ChangePasswordIn, request: Request, user: sqlite3.Row = Depends(current_user)):
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少 6 位")
    if len(body.new_password) > MAX_PASSWORD:
        raise HTTPException(status_code=400, detail="新密码太长了")
    if len(body.old_password) > MAX_PASSWORD:
        raise HTTPException(status_code=400, detail="旧密码太长了")
    if not secrets.compare_digest(
        hash_password(body.old_password, user["salt"]), user["password_hash"]
    ):
        raise HTTPException(status_code=400, detail="旧密码不正确")
    if body.new_password == body.old_password:
        raise HTTPException(status_code=400, detail="新密码不能和旧密码相同")
    salt = secrets.token_hex(16)
    current_token = _bearer_token(request)
    conn = get_db()
    try:
        conn.execute(
            "UPDATE users SET password_hash = ?, salt = ?, must_change_password = 0 WHERE id = ?",
            (hash_password(body.new_password, salt), salt, user["id"]),
        )
        # 吊销该用户除本次会话外的全部会话（和改密同事务；取不到当前令牌时不删，避免误踢自己）
        if current_token:
            conn.execute(
                "DELETE FROM sessions WHERE user_id = ? AND token != ?",
                (user["id"], _token_hash(current_token)),
            )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@app.get("/api/me")
def me(user: sqlite3.Row = Depends(current_user)):
    return {
        "username": user["username"],
        "must_change_password": bool(user["must_change_password"]),
    }


# ---------------------------------------------------------------------------
# boards / columns / cards
# ---------------------------------------------------------------------------

class BoardIn(BaseModel):
    name: str


class ColumnIn(BaseModel):
    title: str


class ReorderIn(BaseModel):
    column_ids: list[int]


class CardIn(BaseModel):
    title: str
    description: str = ""
    tag: str = ""
    tag_color: str = "blue"
    due_date: str = ""


class MoveIn(BaseModel):
    to_column_id: int
    to_index: int


def _get_own_board(conn: sqlite3.Connection, board_id: int, user_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM boards WHERE id = ? AND user_id = ?", (board_id, user_id)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="看板不存在")
    return row


def _get_own_column(conn: sqlite3.Connection, column_id: int, user_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT c.* FROM board_columns c JOIN boards b ON b.id = c.board_id"
        " WHERE c.id = ? AND b.user_id = ?",
        (column_id, user_id),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="列不存在")
    return row


def _get_own_card(conn: sqlite3.Connection, card_id: int, user_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT k.* FROM cards k"
        " JOIN board_columns c ON c.id = k.column_id"
        " JOIN boards b ON b.id = c.board_id"
        " WHERE k.id = ? AND b.user_id = ?",
        (card_id, user_id),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="卡片不存在")
    return row


def _card_out(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    col = conn.execute(
        "SELECT board_id, title FROM board_columns WHERE id = ?", (row["column_id"],)
    ).fetchone()
    return {
        "id": row["id"],
        "column_id": row["column_id"],
        "board_id": col["board_id"] if col else None,
        "column_title": col["title"] if col else "",
        "title": row["title"],
        "description": row["description"],
        "tag": row["tag"],
        "tag_color": row["tag_color"],
        "due_date": row["due_date"],
        "position": row["position"],
        "is_archived": bool(row["is_archived"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _active_cards(conn: sqlite3.Connection, column_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM cards WHERE column_id = ? AND is_archived = 0"
        " ORDER BY position ASC, id ASC",
        (column_id,),
    ).fetchall()


def _repack_positions(conn: sqlite3.Connection, column_id: int) -> None:
    """Rewrite positions of the column's active cards as 0,1,2,... in order."""
    for idx, card in enumerate(_active_cards(conn, column_id)):
        if card["position"] != idx:
            conn.execute(
                "UPDATE cards SET position = ? WHERE id = ?", (idx, card["id"])
            )


def _board_out(conn: sqlite3.Connection, board: sqlite3.Row, with_cards: bool) -> dict:
    cols = conn.execute(
        "SELECT * FROM board_columns WHERE board_id = ? ORDER BY position ASC, id ASC",
        (board["id"],),
    ).fetchall()
    out = {
        "id": board["id"],
        "name": board["name"],
        "created_at": board["created_at"],
        "updated_at": board["updated_at"],
        "column_count": len(cols),
        "card_count": conn.execute(
            "SELECT COUNT(*) AS c FROM cards k"
            " JOIN board_columns c ON c.id = k.column_id"
            " WHERE c.board_id = ? AND k.is_archived = 0",
            (board["id"],),
        ).fetchone()["c"],
    }
    if with_cards:
        out["columns"] = [
            {
                "id": c["id"],
                "title": c["title"],
                "position": c["position"],
                "cards": [_card_out(conn, k) for k in _active_cards(conn, c["id"])],
            }
            for c in cols
        ]
    return out


def _touch_board(conn: sqlite3.Connection, board_id: int) -> None:
    conn.execute(
        "UPDATE boards SET updated_at = ? WHERE id = ?", (iso(utcnow()), board_id)
    )


@app.get("/api/boards")
def list_boards(user: sqlite3.Row = Depends(current_user)):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM boards WHERE user_id = ? ORDER BY updated_at DESC, id DESC",
            (user["id"],),
        ).fetchall()
        return [_board_out(conn, b, with_cards=False) for b in rows]
    finally:
        conn.close()


@app.post("/api/boards")
def create_board(body: BoardIn, user: sqlite3.Row = Depends(current_user)):
    name = _clean_text(body.name, MAX_BOARD_NAME, "看板名")
    now = iso(utcnow())
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO boards (user_id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (user["id"], name, now, now),
        )
        board_id = cur.lastrowid
        for idx, title in enumerate(DEFAULT_COLUMNS):
            conn.execute(
                "INSERT INTO board_columns (board_id, title, position) VALUES (?, ?, ?)",
                (board_id, title, idx),
            )
        conn.commit()
        row = conn.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()
        return _board_out(conn, row, with_cards=True)
    finally:
        conn.close()


@app.get("/api/boards/{board_id}")
def get_board(board_id: int, user: sqlite3.Row = Depends(current_user)):
    conn = get_db()
    try:
        board = _get_own_board(conn, board_id, user["id"])
        return _board_out(conn, board, with_cards=True)
    finally:
        conn.close()


@app.put("/api/boards/{board_id}")
def update_board(board_id: int, body: BoardIn, user: sqlite3.Row = Depends(current_user)):
    name = _clean_text(body.name, MAX_BOARD_NAME, "看板名")
    conn = get_db()
    try:
        _get_own_board(conn, board_id, user["id"])
        conn.execute(
            "UPDATE boards SET name = ?, updated_at = ? WHERE id = ?",
            (name, iso(utcnow()), board_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()
        return _board_out(conn, row, with_cards=False)
    finally:
        conn.close()


@app.delete("/api/boards/{board_id}")
def delete_board(board_id: int, user: sqlite3.Row = Depends(current_user)):
    conn = get_db()
    try:
        _get_own_board(conn, board_id, user["id"])
        conn.execute("DELETE FROM boards WHERE id = ?", (board_id,))
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@app.post("/api/boards/{board_id}/columns")
def create_column(board_id: int, body: ColumnIn, user: sqlite3.Row = Depends(current_user)):
    title = _clean_text(body.title, MAX_COLUMN_TITLE, "列名")
    conn = get_db()
    try:
        _get_own_board(conn, board_id, user["id"])
        row = conn.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 AS p FROM board_columns WHERE board_id = ?",
            (board_id,),
        ).fetchone()
        cur = conn.execute(
            "INSERT INTO board_columns (board_id, title, position) VALUES (?, ?, ?)",
            (board_id, title, row["p"]),
        )
        _touch_board(conn, board_id)
        conn.commit()
        col = conn.execute(
            "SELECT * FROM board_columns WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return {"id": col["id"], "title": col["title"], "position": col["position"]}
    finally:
        conn.close()


@app.post("/api/boards/{board_id}/columns/reorder")
def reorder_columns(
    board_id: int, body: ReorderIn, user: sqlite3.Row = Depends(current_user)
):
    conn = get_db()
    try:
        _get_own_board(conn, board_id, user["id"])
        existing = {
            r["id"]
            for r in conn.execute(
                "SELECT id FROM board_columns WHERE board_id = ?", (board_id,)
            ).fetchall()
        }
        if set(body.column_ids) != existing or len(body.column_ids) != len(existing):
            raise HTTPException(status_code=400, detail="列顺序数据不完整")
        for idx, col_id in enumerate(body.column_ids):
            conn.execute(
                "UPDATE board_columns SET position = ? WHERE id = ?", (idx, col_id)
            )
        _touch_board(conn, board_id)
        conn.commit()
        board = conn.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()
        return _board_out(conn, board, with_cards=True)
    finally:
        conn.close()


@app.put("/api/columns/{column_id}")
def update_column(
    column_id: int, body: ColumnIn, user: sqlite3.Row = Depends(current_user)
):
    title = _clean_text(body.title, MAX_COLUMN_TITLE, "列名")
    conn = get_db()
    try:
        col = _get_own_column(conn, column_id, user["id"])
        conn.execute(
            "UPDATE board_columns SET title = ? WHERE id = ?", (title, column_id)
        )
        _touch_board(conn, col["board_id"])
        conn.commit()
        row = conn.execute(
            "SELECT * FROM board_columns WHERE id = ?", (column_id,)
        ).fetchone()
        return {"id": row["id"], "title": row["title"], "position": row["position"]}
    finally:
        conn.close()


@app.delete("/api/columns/{column_id}")
def delete_column(column_id: int, user: sqlite3.Row = Depends(current_user)):
    conn = get_db()
    try:
        col = _get_own_column(conn, column_id, user["id"])
        board_id = col["board_id"]
        # Cards in the column are removed with it (ON DELETE CASCADE).
        conn.execute("DELETE FROM board_columns WHERE id = ?", (column_id,))
        rows = conn.execute(
            "SELECT id FROM board_columns WHERE board_id = ? ORDER BY position ASC, id ASC",
            (board_id,),
        ).fetchall()
        for idx, r in enumerate(rows):
            conn.execute(
                "UPDATE board_columns SET position = ? WHERE id = ?", (idx, r["id"])
            )
        _touch_board(conn, board_id)
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


def _clean_card_fields(body: CardIn) -> dict:
    title = _clean_text(body.title, MAX_CARD_TITLE, "卡片标题")
    description = (body.description or "").replace("\x00", "").strip()
    if len(description) > MAX_CARD_DESC:
        raise HTTPException(status_code=400, detail="卡片描述太长了")
    tag = (body.tag or "").replace("\x00", "").strip()
    if len(tag) > MAX_TAG:
        raise HTTPException(status_code=400, detail="标签太长了")
    return {
        "title": title,
        "description": description,
        "tag": tag,
        "tag_color": _clean_tag_color(body.tag_color),
        "due_date": _clean_due_date(body.due_date),
    }


@app.post("/api/columns/{column_id}/cards")
def create_card(
    column_id: int, body: CardIn, user: sqlite3.Row = Depends(current_user)
):
    fields = _clean_card_fields(body)
    now = iso(utcnow())
    conn = get_db()
    try:
        col = _get_own_column(conn, column_id, user["id"])
        row = conn.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 AS p FROM cards"
            " WHERE column_id = ? AND is_archived = 0",
            (column_id,),
        ).fetchone()
        cur = conn.execute(
            "INSERT INTO cards (column_id, title, description, tag, tag_color,"
            " due_date, position, is_archived, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)",
            (
                column_id,
                fields["title"],
                fields["description"],
                fields["tag"],
                fields["tag_color"],
                fields["due_date"],
                row["p"],
                now,
                now,
            ),
        )
        _touch_board(conn, col["board_id"])
        conn.commit()
        card = conn.execute(
            "SELECT * FROM cards WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return _card_out(conn, card)
    finally:
        conn.close()


@app.put("/api/cards/{card_id}")
def update_card(card_id: int, body: CardIn, user: sqlite3.Row = Depends(current_user)):
    fields = _clean_card_fields(body)
    conn = get_db()
    try:
        card = _get_own_card(conn, card_id, user["id"])
        if card["is_archived"]:
            raise HTTPException(status_code=400, detail="已归档的卡片不能修改，请先恢复")
        conn.execute(
            "UPDATE cards SET title = ?, description = ?, tag = ?, tag_color = ?,"
            " due_date = ?, updated_at = ? WHERE id = ?",
            (
                fields["title"],
                fields["description"],
                fields["tag"],
                fields["tag_color"],
                fields["due_date"],
                iso(utcnow()),
                card_id,
            ),
        )
        col = conn.execute(
            "SELECT board_id FROM board_columns WHERE id = ?", (card["column_id"],)
        ).fetchone()
        _touch_board(conn, col["board_id"])
        conn.commit()
        row = conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
        return _card_out(conn, row)
    finally:
        conn.close()


@app.delete("/api/cards/{card_id}")
def delete_card(card_id: int, user: sqlite3.Row = Depends(current_user)):
    conn = get_db()
    try:
        card = _get_own_card(conn, card_id, user["id"])
        was_active = not card["is_archived"]
        column_id = card["column_id"]
        conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        if was_active:
            _repack_positions(conn, column_id)
        col = conn.execute(
            "SELECT board_id FROM board_columns WHERE id = ?", (column_id,)
        ).fetchone()
        _touch_board(conn, col["board_id"])
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@app.post("/api/cards/{card_id}/move")
def move_card(card_id: int, body: MoveIn, user: sqlite3.Row = Depends(current_user)):
    conn = get_db()
    try:
        card = _get_own_card(conn, card_id, user["id"])
        if card["is_archived"]:
            raise HTTPException(status_code=400, detail="已归档的卡片不能移动，请先恢复")
        target_col = _get_own_column(conn, body.to_column_id, user["id"])
        source_col = conn.execute(
            "SELECT * FROM board_columns WHERE id = ?", (card["column_id"],)
        ).fetchone()
        if target_col["board_id"] != source_col["board_id"]:
            raise HTTPException(status_code=400, detail="不能把卡片移到其他看板")

        source_ids = [c["id"] for c in _active_cards(conn, source_col["id"])]
        source_ids.remove(card_id)
        if target_col["id"] == source_col["id"]:
            target_ids = source_ids
        else:
            target_ids = [c["id"] for c in _active_cards(conn, target_col["id"])]
        idx = max(0, min(body.to_index, len(target_ids)))
        target_ids.insert(idx, card_id)

        conn.execute(
            "UPDATE cards SET column_id = ?, updated_at = ? WHERE id = ?",
            (target_col["id"], iso(utcnow()), card_id),
        )
        for pos, cid in enumerate(target_ids):
            conn.execute("UPDATE cards SET position = ? WHERE id = ?", (pos, cid))
        if target_col["id"] != source_col["id"]:
            for pos, cid in enumerate(source_ids):
                conn.execute("UPDATE cards SET position = ? WHERE id = ?", (pos, cid))
        _touch_board(conn, target_col["board_id"])
        conn.commit()
        row = conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
        return _card_out(conn, row)
    finally:
        conn.close()


@app.post("/api/cards/{card_id}/archive")
def archive_card(card_id: int, user: sqlite3.Row = Depends(current_user)):
    conn = get_db()
    try:
        card = _get_own_card(conn, card_id, user["id"])
        if card["is_archived"]:
            return _card_out(conn, card)
        conn.execute(
            "UPDATE cards SET is_archived = 1, updated_at = ? WHERE id = ?",
            (iso(utcnow()), card_id),
        )
        _repack_positions(conn, card["column_id"])
        col = conn.execute(
            "SELECT board_id FROM board_columns WHERE id = ?", (card["column_id"],)
        ).fetchone()
        _touch_board(conn, col["board_id"])
        conn.commit()
        row = conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
        return _card_out(conn, row)
    finally:
        conn.close()


@app.post("/api/cards/{card_id}/restore")
def restore_card(card_id: int, user: sqlite3.Row = Depends(current_user)):
    conn = get_db()
    try:
        card = _get_own_card(conn, card_id, user["id"])
        if not card["is_archived"]:
            return _card_out(conn, card)
        row = conn.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 AS p FROM cards"
            " WHERE column_id = ? AND is_archived = 0",
            (card["column_id"],),
        ).fetchone()
        conn.execute(
            "UPDATE cards SET is_archived = 0, position = ?, updated_at = ? WHERE id = ?",
            (row["p"], iso(utcnow()), card_id),
        )
        col = conn.execute(
            "SELECT board_id FROM board_columns WHERE id = ?", (card["column_id"],)
        ).fetchone()
        _touch_board(conn, col["board_id"])
        conn.commit()
        new_row = conn.execute(
            "SELECT * FROM cards WHERE id = ?", (card_id,)
        ).fetchone()
        return _card_out(conn, new_row)
    finally:
        conn.close()


@app.get("/api/boards/{board_id}/archived")
def list_archived(board_id: int, user: sqlite3.Row = Depends(current_user)):
    conn = get_db()
    try:
        _get_own_board(conn, board_id, user["id"])
        rows = conn.execute(
            "SELECT k.* FROM cards k"
            " JOIN board_columns c ON c.id = k.column_id"
            " WHERE c.board_id = ? AND k.is_archived = 1"
            " ORDER BY k.updated_at DESC, k.id DESC",
            (board_id,),
        ).fetchall()
        return [_card_out(conn, r) for r in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# static page
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


if __name__ == "__main__":
    import uvicorn

    port_raw = os.environ.get("PORT", "8000")
    try:
        port = int(port_raw)
    except ValueError:
        print(f"错误：PORT 环境变量必须是数字，当前值 {port_raw!r}", file=sys.stderr)
        raise SystemExit(2)
    uvicorn.run(app, host=HOST, port=port)
