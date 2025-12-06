# XS‑Leak Error Event Lab

This repository contains a self‑contained lab environment that demonstrates a
simple **cross‑site leak (XS‑Leak)** using error events.  By loading a
cross‑origin resource and observing whether the browser fires an `onload` or
`error` event, an attacker can determine whether a victim is authenticated on
another website.  The lab uses two Docker containers:

* **victim** – a Flask application that simulates a protected resource at
  `/admin.js`.  When the user is authenticated (via a cookie), this endpoint
  returns a small JavaScript file with status `200 OK`.  Otherwise it
  returns a `404 Not Found` response.  According to the XS‑Leaks wiki,
  error events can be used to infer whether a protected resource exists and
  thereby reveal whether the user is logged in【601958408505051†L255-L279】.

* **attacker** – a static HTML page served by Nginx.  The page provides a
  button that, when clicked, creates a `<script>` element whose `src`
  attribute points to the victim’s `/admin.js` endpoint.  If the script
  loads successfully (`onload` event), the attacker knows the resource exists;
  if it triggers an `error` event, the attacker infers the resource does not
  exist【601958408505051†L255-L279】.  This difference leaks information about
  the victim’s state across origins.

The lab environment is intentionally simple so that you can easily
understand the attack mechanics and explore mitigations.  It is loosely
inspired by the XS‑Leaks wiki and MDN documentation【41433878019902†L56-L92】.

## Prerequisites

* **Docker** and **Docker Compose** must be installed.  Docker Desktop on
  Windows/macOS or the docker engine on Linux are sufficient.
* You need permission to edit your system’s `/etc/hosts` file (or the
  equivalent hosts configuration on your OS).  This allows us to assign
  distinct hostnames to each service so that cookies are not shared across
  ports (cookies are domain‑scoped, not port‑scoped).

## Quick start

Follow these steps to set up and run the lab.

### 1. Clone this repository

```bash
git clone <this‑repository> xsleak_lab
cd xsleak_lab
```

### 2. Map hostnames to localhost

Add the following entries to your hosts file (`/etc/hosts` on Unix/Linux,
`C:\\Windows\\System32\\drivers\\etc\\hosts` on Windows).  These mappings
ensure that cookies set by `victim.xsleak.test` are not sent to `attacker.xsleak.test` and
vice versa.  Without distinct hostnames, the cookie might be sent across
both services, undermining the cross‑origin property of the attack.

```
127.0.0.1 victim.xsleak.test
127.0.0.1 attacker.xsleak.test
```

After editing the file, save it.  You may need administrative privileges.

### 3. Build and start the environment

Use Docker Compose to build and run both services.  In the project root
(`xsleak_lab/`), run:

```bash
docker-compose up -d --build
```

This command:

* Builds the **victim** image from `xsleak_lab/victim`.  The Flask app
  listens on port `5000` inside the container and is published to the host
  on port `5000`.
* Builds the **attacker** image from `xsleak_lab/attacker`.  The Nginx
  server listens on port `80` inside the container and is published to the
  host on port `8080`.
* Creates a Docker network `xsleaknet` so the containers can talk to each
  other via their service names (`victim` and `attacker`) if needed.

Docker will download base images (python and nginx) and install Flask.
Subsequent runs will be faster because the images are cached.

### 4. Interact with the services

#### Victim service

Open your browser and visit **https://victim.xsleak.test:5000**.  The page
describes the victim site and links to **/login** and **/logout**.  Click
`/login` to set an authentication cookie (`auth=1` with `SameSite=Lax`).  You
can verify that the protected resource exists by visiting
`https://victim.xsleak.test:5000/admin.js` – when authenticated, the server returns
a small JavaScript file; otherwise it returns a 404.

#### Attacker page

In a new tab, visit **https://attacker.xsleak.test:8080**.  The page explains the
lab and includes a **Probe /admin.js** button.  When you click the
button, the page creates a `<script>` tag whose `src` points to
`https://victim.xsleak.test:5000/admin.js` (with a cache‑busting query
parameter).  It then registers event handlers for `onload` and
`onerror`:

* If you are **logged in**, the victim responds with status `200` and
  `Content‑Type: application/javascript`.  The browser executes the
  script and fires an **onload** event.  The attacker page displays a
  message indicating that `/admin.js` exists.
* If you are **not logged in**, the victim responds with status `404` and
  no body.  The browser cannot find the script and fires an
  **error** event.  The attacker page displays a message indicating that
  `/admin.js` does not exist.

This difference in event type leaks information across origins.  According
to MDN, such attacks can reveal whether a user is logged in or even
identify user IDs by probing URL patterns【601958408505051†L255-L279】.  The
XS‑Leaks wiki notes that error events can be thrown from many HTML tags and
that the behavior varies by browser【41433878019902†L56-L92】.

### 5. Experiment with log in and log out

Try the following sequence:

1. Ensure you are **logged out** by visiting `https://victim.xsleak.test:5000/logout`.
2. On the attacker page, click **Probe**.  The result should say the
   script does not exist (error event).
3. Log in via `https://victim.xsleak.test:5000/login` to set the cookie.
4. Without closing the attacker page, click **Probe** again.  Now the
   result should indicate that the script exists (onload event).

This demonstrates how simply loading a resource can leak information about
the victim’s state.

### 6. Explore mitigations

The simple victim implementation intentionally returns a 404 when the user
is not authenticated.  This difference in response status and body is what
makes the leak possible.  Real‑world applications can mitigate such
leaks by:

* **Uniform responses**: always return the same status code and similar
  response size/content type for both authenticated and unauthenticated
  cases.  For example, return a generic JavaScript file that does not
  reveal anything, regardless of auth state.
* **Resource isolation policies**: use headers such as
  `Cross‑Origin‑Resource‑Policy: cross-origin` or `Cross‑Origin‑Opener‑Policy`
  to prevent cross‑site resource loads from being interpreted【41433878019902†L86-L103】.
* **SameSite cookies**: set cookies with `SameSite=Strict` so they are not
  sent with cross‑site subresource requests.  In our victim app, you can
  change the `samesite` attribute in `victim_app.py` from `Lax` to
  `Strict` and rebuild the container.
* **Partitioned caches**: avoid returning cacheable sensitive resources or rely
  on partitioned HTTP caches so that an attacker cannot infer presence via
  cache probing.

To experiment with these defenses, edit `victim/victim_app.py` and rebuild
the `victim` service:

```bash
docker-compose build victim
docker-compose up -d
```

Observe how changing the status code or headers affects the attacker’s
ability to distinguish between logged‑in and logged‑out states.

### 7. Stopping the environment

When finished, stop and remove the containers:

```bash
docker-compose down
```

This command stops the services and frees the ports.

## Additional notes

* The lab uses distinct ports and hostnames to ensure cross‑origin
  isolation.  Cookies set by `victim.xsleak.test` will not be sent to
  `attacker.xsleak.test`, which is essential for the XS‑Leak to work.
* The `SameSite=Lax` cookie in `victim_app.py` will be sent with
  navigations but not with top‑level cross‑site requests.  You can modify
  this to `Strict` to strengthen the defense.
* The lab uses self‑signed HTTP (not HTTPS) because TLS is not required
  for the demonstration.  If your browser enforces mixed‑content rules,
  you can add `http://` instead of `https://` in the URLs, or configure
  TLS in the Docker Compose file.

## References

* MDN Web Docs – Cross‑site leaks (XS‑Leaks): the article describes sample
  XS‑Leak attacks including leaking page existence using error events【601958408505051†L255-L279】.
* XS‑Leaks Wiki – Error Events: explains how error events can reveal
  differences in cross‑origin requests and provides a code snippet for
  detection【41433878019902†L56-L92】.
* XS‑Leaks Wiki – Introduction: describes oracles and cross‑site
  interactions that enable XS‑Leaks【672113468730227†L75-L97】.
