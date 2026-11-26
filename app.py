"""의도적으로 취약한 로컬 학습 앱. python app.py로만 실행한다."""

from datetime import timedelta
from functools import wraps
import hmac
import secrets
import sqlite3

from flask import Flask, abort, jsonify, redirect, render_template_string, request, session
from werkzeug.security import check_password_hash, generate_password_hash


PASSWORDS = {name: generate_password_hash(f"{name}-lab") for name in ("alice", "bob")}


def create_app(testing=False):
    app = Flask(__name__)
    app.config.update(
        TESTING=testing,
        SECRET_KEY=secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        # HTTP loopback 실습용. 실제 HTTPS 서비스에서는 True로 설정한다.
        SESSION_COOKIE_SECURE=False,
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE,
            password_hash TEXT, display_name TEXT, is_admin INTEGER DEFAULT 0);
        CREATE TABLE notes (id INTEGER PRIMARY KEY, owner_id INTEGER, body TEXT);
        CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO notes VALUES (1, 1, 'Alice private memo'), (2, 2, 'Bob private memo');
        INSERT INTO products VALUES (1, 'Notebook'), (2, 'Pencil');
    """)
    for uid, name in enumerate(("alice", "bob"), 1):
        db.execute("INSERT INTO users VALUES (?, ?, ?, ?, 0)",
                   (uid, name, PASSWORDS[name], name.title()))
    db.commit()
    # 모든 데이터는 프로세스 메모리 안에 있으며 재시작하면 초기화된다.
    active_sessions = {}
    app.extensions["lab_db"] = db
    app.extensions["lab_sessions"] = active_sessions

    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        return session["csrf"]

    def require_csrf():
        supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf", "")
        expected = session.get("csrf", "")
        if not expected or not hmac.compare_digest(supplied.encode(), expected.encode()):
            app.logger.warning("csrf_denied method=%s path=%s", request.method, request.path)
            abort(403)

    def current_user():
        uid = active_sessions.get(session.get("sid"))
        return db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()

    def login_required(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if current_user() is None:
                abort(401)
            return fn(*args, **kwargs)
        return wrapped

    @app.get("/")
    def index():
        user = current_user()
        return render_template_string("""
        <!doctype html><html lang="ko"><meta charset="utf-8">
        <title>보안 실습</title><h1>로컬 보안 실습</h1>
        <p>학습 계정: alice / alice-lab, bob / bob-lab</p>
        {% if user %}
        <p>로그인: {{ user['username'] }} / 표시 이름: {{ user['display_name'] }}</p>
        <form action="/logout" method="post"><input type="hidden" name="csrf" value="{{ token }}">
        <button>로그아웃</button></form>
        {% else %}
        <form action="/login" method="post">
        <input type="hidden" name="csrf" value="{{ token }}">
        <input name="username" value="alice" aria-label="사용자">
        <input name="password" type="password" value="alice-lab" aria-label="비밀번호">
        <button>로그인</button></form>{% endif %}
        <ul><li><a href="/vuln/notes/2">취약한 Bob 메모 조회</a></li>
        <li><a href="/safe/notes/2">방어한 Bob 메모 조회</a></li>
        <li><a href="/vuln/search?q=Note">취약한 검색</a></li>
        <li><a href="/safe/search?q=Note">방어한 검색</a></li>
        <li><a href="/vuln/greet?name=Alice">취약한 인사</a></li>
        <li><a href="/safe/greet?name=Alice">방어한 인사</a></li></ul>
        <p>나머지 실습은 docs/web-security/curriculum.md를 참고하세요.</p></html>
        """, user=user, token=csrf_token())

    @app.get("/session")
    def session_info():
        user = current_user()
        return jsonify(csrf=csrf_token(), username=user["username"] if user else None)

    @app.post("/login")
    def login():
        require_csrf()
        user = db.execute("SELECT * FROM users WHERE username = ?",
                          (request.form.get("username", ""),)).fetchone()
        if user is None or not check_password_hash(user["password_hash"],
                                                   request.form.get("password", "")):
            abort(401)
        active_sessions.pop(session.get("sid"), None)
        session.clear()
        session["sid"] = secrets.token_urlsafe(32)
        active_sessions[session["sid"]] = user["id"]
        session.permanent = True
        csrf_token()
        return redirect("/")

    @app.post("/logout")
    def logout():
        require_csrf()
        active_sessions.pop(session.get("sid"), None)
        session.clear()
        return redirect("/")

    @app.get("/vuln/notes/<int:note_id>")
    @login_required
    def vulnerable_note(note_id):
        # 취약: 로그인 여부만 확인하고 소유권을 확인하지 않는다.
        note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if note is None:
            abort(404)
        return jsonify(dict(note))

    @app.get("/safe/notes/<int:note_id>")
    @login_required
    def safe_note(note_id):
        note = db.execute("SELECT * FROM notes WHERE id = ? AND owner_id = ?",
                          (note_id, current_user()["id"])).fetchone()
        if note is None:
            app.logger.warning("object_access_denied user_id=%s note_id=%s",
                               current_user()["id"], note_id)
            abort(404)
        return jsonify(dict(note))

    @app.get("/vuln/search")
    def vulnerable_search():
        q = request.args.get("q", "")
        # 취약: 입력이 SQL 문법의 일부가 된다. execute는 단일 문장만 실행한다.
        sql = f"SELECT id, name FROM products WHERE name LIKE '%{q}%'"
        try:
            return jsonify([dict(row) for row in db.execute(sql)])
        except sqlite3.Error:
            abort(400)

    @app.get("/safe/search")
    def safe_search():
        q = request.args.get("q", "")
        rows = db.execute("SELECT id, name FROM products WHERE name LIKE ?", (f"%{q}%",))
        return jsonify([dict(row) for row in rows])

    @app.get("/vuln/greet")
    def vulnerable_greet():
        # 취약: 입력을 HTML로 삽입한다. SSTI와는 다른 문제다.
        return "<!doctype html><meta charset=utf-8><p>Hello, " + request.args.get("name", "") + "</p>"

    @app.get("/safe/greet")
    def safe_greet():
        # HTML 텍스트 문맥에서 Jinja 자동 이스케이프를 사용한다.
        return render_template_string("<p>Hello, {{ name }}</p>",
                                      name=request.args.get("name", ""))

    @app.post("/vuln/status")
    @login_required
    def vulnerable_status():
        # 취약: 쿠키 인증만 사용하고 CSRF 토큰을 검사하지 않는다.
        db.execute("UPDATE users SET display_name = ? WHERE id = ?",
                   (request.form.get("display_name", ""), current_user()["id"]))
        db.commit()
        return jsonify(updated=True)

    @app.post("/safe/status")
    @login_required
    def safe_status():
        require_csrf()
        name = request.form.get("display_name", "")
        if not 1 <= len(name) <= 40:
            abort(400)
        db.execute("UPDATE users SET display_name = ? WHERE id = ?",
                   (name, current_user()["id"]))
        db.commit()
        return jsonify(updated=True)

    @app.get("/profile")
    @login_required
    def profile():
        user = current_user()
        return jsonify({key: user[key] for key in ("id", "username", "display_name", "is_admin")})

    @app.post("/vuln/profile")
    @login_required
    def vulnerable_profile():
        require_csrf()  # CSRF가 없어도 인가 취약점은 따로 존재한다.
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            abort(400)
        for field in ("display_name", "is_admin"):
            if field in payload:
                # 열 이름은 고정 목록이므로 SQLi 예제가 아니다. 쓰기 권한이 문제다.
                db.execute(f"UPDATE users SET {field} = ? WHERE id = ?",
                           (payload[field], current_user()["id"]))
        db.commit()
        return jsonify(updated=True)

    @app.post("/safe/profile")
    @login_required
    def safe_profile():
        require_csrf()
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or set(payload) != {"display_name"}:
            abort(400)
        name = payload["display_name"]
        if not isinstance(name, str) or not 1 <= len(name) <= 40:
            abort(400)
        db.execute("UPDATE users SET display_name = ? WHERE id = ?", (name, current_user()["id"]))
        db.commit()
        return jsonify(updated=True)

    @app.get("/admin")
    @login_required
    def admin():
        if current_user()["is_admin"] != 1:
            abort(403)
        return jsonify(message="Lab admin area")

    @app.after_request
    def headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        # XSS를 관찰하기 위해 전역 CSP는 설정하지 않았다.
        return response

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False, threaded=False)
