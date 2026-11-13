import unittest

from app import create_app


class WebLabTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.addCleanup(self.app.extensions["lab_db"].close)
        self.client = self.app.test_client()

    def token(self, client=None):
        return (client or self.client).get("/session").json["csrf"]

    def login(self, name="alice", client=None):
        client = client or self.client
        response = client.post("/login", data={"username": name, "password": name + "-lab",
                                               "csrf": self.token(client)})
        self.assertEqual(response.status_code, 302)
        return self.token(client)

    def test_login_requires_valid_password_and_csrf(self):
        self.assertEqual(self.client.post("/login", data={}).status_code, 403)
        token = self.token()
        response = self.client.post("/login", data={"username": "alice", "password": "wrong",
                                                   "csrf": token})
        self.assertEqual(response.status_code, 401)
        self.assertIsNone(self.client.get("/session").json["username"])

    def test_login_rotates_csrf_and_logout_revokes_old_cookie(self):
        old_token = self.token()
        token = self.login()
        self.assertNotEqual(token, old_token)
        cookie = self.client.get_cookie("session").value
        replay = self.app.test_client()
        replay.set_cookie("session", cookie)
        self.assertEqual(replay.get("/profile").status_code, 200)
        self.assertEqual(self.client.post("/logout", data={"csrf": token}).status_code, 302)
        self.assertEqual(replay.get("/profile").status_code, 401)

    def test_notes_require_login_in_both_versions(self):
        for mode in ("vuln", "safe"):
            self.assertEqual(self.client.get(f"/{mode}/notes/1").status_code, 401)

    def test_vulnerable_idor_exposes_other_users_note(self):
        self.login()
        response = self.client.get("/vuln/notes/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["body"], "Bob private memo")

    def test_safe_idor_allows_owner_and_blocks_other_user(self):
        self.login()
        self.assertEqual(self.client.get("/safe/notes/1").json["body"], "Alice private memo")
        self.assertEqual(self.client.get("/safe/notes/2").status_code, 404)
        bob = self.app.test_client()
        self.login("bob", bob)
        self.assertEqual(bob.get("/safe/notes/2").status_code, 200)
        self.assertEqual(bob.get("/safe/notes/1").status_code, 404)

    def test_missing_note_is_404(self):
        self.login()
        for mode in ("vuln", "safe"):
            self.assertEqual(self.client.get(f"/{mode}/notes/999").status_code, 404)

    def test_sql_injection_exposes_notes_only_on_vulnerable_route(self):
        payload = "x' UNION SELECT id, body FROM notes -- "
        vulnerable = self.client.get("/vuln/search", query_string={"q": payload})
        safe = self.client.get("/safe/search", query_string={"q": payload})
        self.assertIn("Bob private memo", [row["name"] for row in vulnerable.json])
        self.assertEqual(safe.json, [])

    def test_normal_search_and_quotes_work(self):
        for mode in ("vuln", "safe"):
            response = self.client.get(f"/{mode}/search", query_string={"q": "Note"})
            self.assertEqual(response.json, [{"id": 1, "name": "Notebook"}])
        self.assertEqual(self.client.get("/safe/search", query_string={"q": "O'Reilly"}).json, [])

    def test_xss_html_is_raw_or_escaped(self):
        payload = "<script>document.title='LAB_XSS'</script>"
        vulnerable = self.client.get("/vuln/greet", query_string={"name": payload})
        safe = self.client.get("/safe/greet", query_string={"name": payload})
        self.assertIn(payload, vulnerable.text)
        self.assertNotIn("<script>", safe.text)
        self.assertIn("&lt;script&gt;", safe.text)

    def test_safe_greeting_preserves_normal_text(self):
        self.assertIn("안녕하세요", self.client.get("/safe/greet", query_string={"name": "안녕하세요"}).text)

    def test_csrf_missing_token_changes_only_vulnerable_route(self):
        self.login()
        self.assertEqual(self.client.post("/safe/status", data={"display_name": "bad"}).status_code, 403)
        self.assertEqual(self.client.get("/profile").json["display_name"], "Alice")
        self.assertEqual(self.client.post("/vuln/status", data={"display_name": "CSRF"}).status_code, 200)
        self.assertEqual(self.client.get("/profile").json["display_name"], "CSRF")

    def test_csrf_wrong_token_and_another_users_token_are_rejected(self):
        self.login()
        bob = self.app.test_client()
        bob_token = self.login("bob", bob)
        for token in ("wrong", bob_token):
            self.assertEqual(self.client.post("/safe/status", data={"display_name": "bad", "csrf": token}).status_code, 403)

    def test_safe_status_accepts_token_and_validates_length(self):
        token = self.login()
        self.assertEqual(self.client.post("/safe/status", data={"display_name": "새 이름", "csrf": token}).status_code, 200)
        self.assertEqual(self.client.get("/profile").json["display_name"], "새 이름")
        self.assertEqual(self.client.post("/safe/status", data={"display_name": "x" * 41, "csrf": token}).status_code, 400)

    def test_vulnerable_mass_assignment_grants_admin(self):
        token = self.login()
        self.assertEqual(self.client.get("/admin").status_code, 403)
        self.assertEqual(self.client.post("/vuln/profile", json={"is_admin": 1},
                                         headers={"X-CSRF-Token": token}).status_code, 200)
        self.assertEqual(self.client.get("/admin").status_code, 200)

    def test_safe_mass_assignment_rejects_privilege_and_unknown_fields(self):
        token = self.login()
        for payload in ({"is_admin": 1}, {"display_name": "name", "extra": 1}, [],
                        {"display_name": 3}, {"display_name": ""}):
            self.assertEqual(self.client.post("/safe/profile", json=payload,
                                             headers={"X-CSRF-Token": token}).status_code, 400)
        self.assertEqual(self.client.get("/profile").json["is_admin"], 0)
        self.assertEqual(self.client.get("/admin").status_code, 403)

    def test_safe_profile_allows_normal_update(self):
        token = self.login()
        response = self.client.post("/safe/profile", json={"display_name": "Alicia"},
                                    headers={"X-CSRF-Token": token})
        self.assertEqual(response.status_code, 200)
        profile = self.client.get("/profile").json
        self.assertEqual(profile["display_name"], "Alicia")
        self.assertNotIn("password_hash", profile)

    def test_security_headers_and_cookie_flags(self):
        response = self.client.get("/session")
        cookie = response.headers["Set-Cookie"]
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Lax", cookie)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_denial_log_has_event_but_no_csrf_secret(self):
        token = self.login()
        with self.assertLogs(self.app.logger, level="WARNING") as logs:
            self.client.get("/safe/notes/2")
            self.client.post("/safe/status", data={"display_name": "bad"})
        text = "\n".join(logs.output)
        self.assertIn("object_access_denied", text)
        self.assertIn("csrf_denied", text)
        self.assertNotIn(token, text)

    def test_request_size_limit(self):
        self.assertEqual(self.client.post("/login", data={"username": "x" * 17000}).status_code, 413)


if __name__ == "__main__":
    unittest.main()
