
from flask import Flask, make_response, request, redirect, url_for, render_template
app = Flask(__name__)

AUTH_COOKIE = "auth"
AUTH_COOKIE_VALUE = "1"
SITE_DOMAIN = ".xsleak.test"


@app.route("/")
def index():
    return render_template('base.html')


@app.route("/login")
def login():
    resp = make_response(
        "<p>In theory, this would be a real login page! For demonstration purposes, this is just going to automatically log you in as an 'admin' and give you access to the Admin Panel at <code>/admin.js</code>. "
        "Return to the <a href='/'>home page</a>.</p>"
    )
    resp.set_cookie(
        AUTH_COOKIE,
        AUTH_COOKIE_VALUE,
        domain=SITE_DOMAIN,
        path="/",
        secure=False,
        httponly=True,
        samesite="Strict",
    )
    return resp


@app.route("/logout")
def logout():
    resp = make_response(
        "<p>Logged out. The auth cookie has been cleared. "
        "Return to the <a href='/'>home page</a>.</p>"
    )
    resp.set_cookie(AUTH_COOKIE, "", expires=0, domain=SITE_DOMAIN, path="/")
    return resp

@app.route("/admin.js")
def adminpanel():
    if request.cookies.get(AUTH_COOKIE) == AUTH_COOKIE_VALUE:
        resp = make_response('/* Valid auth, otherwise returns 404 */ window.__victimAuthed = true;', 200)
        resp.headers["Content-Type"] = "application/javascript"
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["Cross-Origin-Resource-Policy"] = "same-origin" 
        return resp
    else: 
        resp = make_response('/* stuff */ window.__victimAuthed = true;', 200)
        resp.headers["Content-Type"] = "application/javascript"
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["Cross-Origin-Resource-Policy"] = "same-origin" 
        return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)