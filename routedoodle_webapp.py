from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse


DEFAULT_PORT = 8765


INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RouteDoodle GNN v3</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css">
  <style>
    :root {
      color-scheme: light;
      --panel: #ffffff;
      --ink: #20242a;
      --muted: #667085;
      --line: #d0d7de;
      --accent: #2074b6;
      --gnn: #e84545;
      --dijkstra: #27ae60;
    }

    * {
      box-sizing: border-box;
    }

    html,
    body,
    #app,
    #map {
      height: 100%;
      margin: 0;
    }

    body {
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      overflow: hidden;
    }

    #app {
      display: grid;
      grid-template-columns: minmax(300px, 360px) minmax(0, 1fr);
      background: #eef1f4;
    }

    #panel {
      z-index: 500;
      display: flex;
      min-height: 0;
      flex-direction: column;
      gap: 14px;
      padding: 18px;
      border-right: 1px solid var(--line);
      background: var(--panel);
      box-shadow: 0 2px 18px rgba(16, 24, 40, 0.08);
    }

    .title {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    h1 {
      margin: 0;
      font-size: 20px;
      line-height: 1.2;
      font-weight: 720;
      letter-spacing: 0;
    }

    .subtitle {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }

    .actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    button {
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f8fafc;
      color: var(--ink);
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      font-weight: 650;
    }

    button:hover:not(:disabled) {
      background: #eef3f8;
    }

    button:disabled {
      cursor: wait;
      opacity: 0.65;
    }

    button[data-method="gnn"] {
      border-color: color-mix(in srgb, var(--gnn), #ffffff 58%);
      color: var(--gnn);
    }

    button[data-method="dijkstra"] {
      border-color: color-mix(in srgb, var(--dijkstra), #ffffff 54%);
      color: #16834a;
    }

    button[data-method="both"] {
      grid-column: span 2;
      background: #1f2937;
      color: #ffffff;
    }

    button[data-method="clear"] {
      grid-column: span 2;
    }

    .legend {
      display: grid;
      gap: 7px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfe;
      font-size: 13px;
    }

    .legend-row {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }

    .swatch {
      width: 34px;
      height: 0;
      flex: 0 0 auto;
      border-top: 4px solid currentColor;
      border-radius: 999px;
    }

    .swatch.dashed {
      border-top-style: dashed;
    }

    #status {
      min-height: 40px;
      padding: 10px 12px;
      border-left: 4px solid var(--accent);
      background: #f5f9fd;
      color: #374151;
      font-size: 13px;
      line-height: 1.45;
    }

    #results {
      display: grid;
      min-height: 0;
      gap: 10px;
      overflow: auto;
      padding-right: 2px;
    }

    .result {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      padding: 12px;
    }

    .result h2 {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin: 0 0 8px;
      font-size: 14px;
      letter-spacing: 0;
    }

    .metric-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 6px;
      font-size: 12px;
    }

    .metric {
      padding: 7px 8px;
      border-radius: 6px;
      background: #f7f8fa;
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 11px;
    }

    #map {
      width: 100%;
    }

    .leaflet-container {
      font: inherit;
    }

    .leaflet-draw-toolbar a {
      background-size: 300px 30px;
    }

    @media (max-width: 760px) {
      body {
        overflow: auto;
      }

      #app {
        min-height: 100%;
        grid-template-columns: 1fr;
        grid-template-rows: auto minmax(560px, 1fr);
      }

      #panel {
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }
    }
  </style>
</head>
<body>
  <div id="app">
    <aside id="panel">
      <div class="title">
        <h1>RouteDoodle GNN v3</h1>
        <div class="subtitle" id="profile">Ordered safety routing</div>
      </div>

      <div class="actions">
        <button type="button" data-method="gnn">GNN v3</button>
        <button type="button" data-method="dijkstra">Dijkstra</button>
        <button type="button" data-method="both">Compare Both</button>
        <button type="button" data-method="clear">Clear</button>
      </div>

      <div class="legend" aria-label="Map legend">
        <div class="legend-row" style="color: var(--gnn);"><span class="swatch"></span><span>GNN v3</span></div>
        <div class="legend-row" style="color: var(--dijkstra);"><span class="swatch"></span><span>Dijkstra</span></div>
        <div class="legend-row" style="color: var(--accent);"><span class="swatch dashed"></span><span>Doodle</span></div>
      </div>

      <div id="status">Draw a route shape on the map.</div>
      <div id="results" aria-live="polite"></div>
    </aside>

    <main>
      <div id="map" role="application" aria-label="Houston routing map"></div>
    </main>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
  <script>
    const map = L.map("map", {
      center: [29.7604, -95.3698],
      zoom: 12,
      preferCanvas: true
    });

    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      maxZoom: 20,
      attribution: "&copy; OpenStreetMap contributors &copy; CARTO"
    }).addTo(map);

    const drawnLayer = new L.FeatureGroup().addTo(map);
    const routeLayer = new L.FeatureGroup().addTo(map);
    const statusEl = document.getElementById("status");
    const resultsEl = document.getElementById("results");
    const profileEl = document.getElementById("profile");
    const buttons = [...document.querySelectorAll("button[data-method]")];
    let drawnCoords = [];

    fetch("/health")
      .then((res) => res.json())
      .then((data) => {
        profileEl.textContent = `Profile: ${data.run_profile || "unknown"} | Artifacts: ${data.artifact_version || "unknown"}`;
      })
      .catch(() => {
        profileEl.textContent = "Kernel route service unavailable";
      });

    const drawControl = new L.Control.Draw({
      edit: {
        featureGroup: drawnLayer,
        remove: true
      },
      draw: {
        polyline: {
          shapeOptions: {
            color: "#2074b6",
            dashArray: "8 7",
            weight: 4,
            opacity: 0.9
          }
        },
        polygon: false,
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false
      }
    });
    map.addControl(drawControl);

    function setStatus(message, tone = "info") {
      const color = tone === "error" ? "#e84545" : tone === "success" ? "#27ae60" : "#2074b6";
      statusEl.style.borderLeftColor = color;
      statusEl.textContent = message;
    }

    function setBusy(isBusy) {
      buttons.forEach((button) => {
        if (button.dataset.method !== "clear") button.disabled = isBusy;
      });
    }

    function updateDrawnCoords(layer) {
      const latlngs = layer.getLatLngs().flat(Infinity).filter((item) => item && typeof item.lat === "number");
      drawnCoords = latlngs.map((latlng) => [latlng.lat, latlng.lng]);
      routeLayer.clearLayers();
      resultsEl.innerHTML = "";
      setStatus(`Doodle captured: ${drawnCoords.length} points.`);
    }

    map.on(L.Draw.Event.CREATED, (event) => {
      drawnLayer.clearLayers();
      drawnLayer.addLayer(event.layer);
      updateDrawnCoords(event.layer);
    });

    map.on(L.Draw.Event.EDITED, (event) => {
      event.layers.eachLayer(updateDrawnCoords);
    });

    map.on(L.Draw.Event.DELETED, () => {
      drawnCoords = [];
      routeLayer.clearLayers();
      resultsEl.innerHTML = "";
      setStatus("Draw a route shape on the map.");
    });

    function routeColor(route) {
      return route.color || (route.name && route.name.includes("Dijkstra") ? "#27ae60" : "#e84545");
    }

    function addRoute(route) {
      if (!route.coords || route.coords.length < 2) return;
      const color = routeColor(route);
      const line = L.polyline(route.coords, {
        color,
        weight: route.name.includes("GNN") ? 6 : 5,
        opacity: 0.9
      }).addTo(routeLayer);

      const start = route.coords[0];
      const end = route.coords[route.coords.length - 1];
      L.circleMarker(start, {
        radius: 6,
        color: "#ffffff",
        fillColor: "#16834a",
        fillOpacity: 1,
        weight: 2
      }).addTo(routeLayer);
      L.circleMarker(end, {
        radius: 6,
        color: "#ffffff",
        fillColor: "#b42318",
        fillOpacity: 1,
        weight: 2
      }).addTo(routeLayer);

      return line;
    }

    function formatPct(value) {
      return `${(100 * Number(value || 0)).toFixed(1)}%`;
    }

    function renderResult(route) {
      const stats = route.stats || {};
      const item = document.createElement("section");
      item.className = "result";
      item.innerHTML = `
        <h2><span style="color:${routeColor(route)}">${route.name}</span><span>${Number(route.km || 0).toFixed(2)} km</span></h2>
        <div class="metric-grid">
          <div class="metric"><span>Time</span>${Number(route.seconds || 0).toFixed(2)} s</div>
          <div class="metric"><span>Crime</span>${Number(stats.crime_avg || 0).toFixed(4)}</div>
          <div class="metric"><span>Danger</span>${Number(stats.danger_avg || 0).toFixed(4)}</div>
          <div class="metric"><span>Exposed</span>${formatPct(stats.exposed_frac)}</div>
        </div>
      `;
      resultsEl.appendChild(item);
    }

    async function runRoute(method) {
      if (!drawnCoords || drawnCoords.length < 2) {
        setStatus("Draw a polyline first.", "error");
        return;
      }

      setBusy(true);
      routeLayer.clearLayers();
      resultsEl.innerHTML = "";
      setStatus("Routing...");

      try {
        const response = await fetch("/route", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ method, coords: drawnCoords })
        });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || "Routing failed");

        const layers = [];
        payload.routes.forEach((route) => {
          const layer = addRoute(route);
          if (layer) layers.push(layer);
          renderResult(route);
        });

        if (layers.length) {
          const bounds = routeLayer.getBounds();
          if (bounds.isValid()) map.fitBounds(bounds.pad(0.12));
          setStatus(`Done. ${payload.simplified_points} simplified doodle points, ${payload.subgraph.nodes} nodes, ${payload.subgraph.edges} edges.`, "success");
        } else {
          setStatus("No route was returned.", "error");
        }
      } catch (error) {
        setStatus(error.message || String(error), "error");
      } finally {
        setBusy(false);
      }
    }

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const method = button.dataset.method;
        if (method === "clear") {
          drawnCoords = [];
          drawnLayer.clearLayers();
          routeLayer.clearLayers();
          resultsEl.innerHTML = "";
          setStatus("Draw a route shape on the map.");
          return;
        }
        runRoute(method);
      });
    });
  </script>
</body>
</html>
"""


@dataclass
class RouteDoodleWebApp:
    server: ThreadingHTTPServer
    thread: threading.Thread
    host: str
    port: int

    @property
    def url(self) -> str:
        display_host = "127.0.0.1" if self.host in {"0.0.0.0", ""} else self.host
        return f"http://{display_host}:{self.port}/"

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


@dataclass
class PublishedRouteDoodleURL:
    url: str
    mode: str
    detail: str = ""


def start_routedoodle_webapp(namespace: dict[str, Any], host: str = "127.0.0.1", port: int | None = None) -> RouteDoodleWebApp:
    """Start a full-page browser UI backed by the live notebook namespace."""
    existing = namespace.get("_routedoodle_webapp")
    if isinstance(existing, RouteDoodleWebApp) and existing.thread.is_alive():
        return existing

    selected_port = _find_available_port(host, port or DEFAULT_PORT)
    route_lock = threading.Lock()

    class RouteDoodleHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path in {"/", "/index.html"}:
                self._send_html(INDEX_HTML)
            elif path == "/health":
                self._send_json(
                    {
                        "ok": True,
                        "run_profile": namespace.get("RUN_PROFILE"),
                        "artifact_version": namespace.get("ARTIFACT_VERSION"),
                    }
                )
            elif path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.end_headers()
            else:
                self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            if path != "/route":
                self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                coords = _parse_coords(payload.get("coords"))
                method = str(payload.get("method", "both")).lower()
                if method not in {"gnn", "dijkstra", "both"}:
                    raise ValueError("method must be one of: gnn, dijkstra, both")

                with route_lock:
                    result = _route_payload(namespace, coords, method)
                self._send_json(result)
            except Exception as exc:
                self._send_json(
                    {
                        "error": str(exc),
                        "traceback": traceback.format_exc(limit=8),
                    },
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("x-colab-notebook-cache-control", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(_json_safe(payload)).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("x-colab-notebook-cache-control", "no-cache")
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer((host, selected_port), RouteDoodleHandler)
    thread = threading.Thread(target=server.serve_forever, name="routedoodle-webapp", daemon=True)
    thread.start()

    app = RouteDoodleWebApp(server=server, thread=thread, host=host, port=selected_port)
    namespace["_routedoodle_webapp"] = app
    return app


def start_static_webpage(
    page: Any,
    namespace: dict[str, Any] | None = None,
    host: str = "127.0.0.1",
    port: int | None = None,
    cache_key: str = "_routedoodle_static_webpage",
) -> RouteDoodleWebApp:
    """Serve a Folium map or HTML string as a normal browser page."""
    if namespace is not None:
        existing = namespace.get(cache_key)
        if isinstance(existing, RouteDoodleWebApp) and existing.thread.is_alive():
            existing.stop()

    html = _render_page_html(page)
    selected_port = _find_available_port(host, port or (DEFAULT_PORT + 1))

    class StaticPageHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path in {"/", "/index.html"}:
                body = html.encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("x-colab-notebook-cache-control", "no-cache")
                self.end_headers()
                self.wfile.write(body)
            elif path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.end_headers()
            else:
                body = b'{"error": "Not found"}'
                self.send_response(HTTPStatus.NOT_FOUND)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("x-colab-notebook-cache-control", "no-cache")
                self.end_headers()
                self.wfile.write(body)

    server = ThreadingHTTPServer((host, selected_port), StaticPageHandler)
    thread = threading.Thread(target=server.serve_forever, name="routedoodle-static-page", daemon=True)
    thread.start()

    app = RouteDoodleWebApp(server=server, thread=thread, host=host, port=selected_port)
    if namespace is not None:
        namespace[cache_key] = app
    return app


def get_accessible_url(
    app: RouteDoodleWebApp,
    namespace: dict[str, Any] | None = None,
    in_colab: bool = False,
    prefer_public: bool = True,
    cache_key: str | None = None,
) -> PublishedRouteDoodleURL:
    """Return the best browser URL for a kernel-hosted web app.

    Public sharing is opt-in/config-driven. Set ROUTEDOODLE_TUNNEL=ngrok or
    ROUTEDOODLE_TUNNEL=cloudflared to require a public tunnel. With the default
    ROUTEDOODLE_TUNNEL=auto, installed/configured tunnel providers are tried
    first, then Colab proxy/local URLs are used as fallbacks.
    """
    cache_key = cache_key or f"_routedoodle_published_url_{app.port}"
    if namespace is not None:
        existing = namespace.get(cache_key)
        if isinstance(existing, PublishedRouteDoodleURL):
            return existing

    explicit_url = _explicit_public_url(app.port)
    if explicit_url:
        return _remember_published_url(
            PublishedRouteDoodleURL(explicit_url, "explicit", "ROUTEDOODLE_PUBLIC_URL"),
            namespace,
            cache_key,
        )

    tunnel_pref = os.environ.get("ROUTEDOODLE_TUNNEL", "auto" if prefer_public else "none").strip().lower()
    if tunnel_pref in {"public", "share"}:
        tunnel_pref = "auto"

    if tunnel_pref not in {"", "0", "false", "no", "none", "local", "colab", "proxy"}:
        errors: list[str] = []
        providers = ["ngrok", "cloudflared"] if tunnel_pref == "auto" else [tunnel_pref]
        for provider in providers:
            try:
                published = _start_public_tunnel(provider, app, namespace, cache_key)
            except Exception as exc:
                errors.append(f"{provider}: {exc}")
                continue
            if published:
                return _remember_published_url(published, namespace, cache_key)

        if tunnel_pref != "auto":
            raise RuntimeError(
                f"ROUTEDOODLE_TUNNEL={tunnel_pref!r} was requested, but no tunnel could be started. "
                + " | ".join(errors)
            )

    if in_colab:
        try:
            from google.colab.output import eval_js

            return _remember_published_url(
                PublishedRouteDoodleURL(
                    eval_js(f"google.colab.kernel.proxyPort({app.port})"),
                    "colab-proxy",
                    "Accessible to the current Colab executor while the notebook is open.",
                ),
                namespace,
                cache_key,
            )
        except Exception as exc:
            if tunnel_pref == "colab":
                raise RuntimeError(f"Could not create a Colab proxy URL for port {app.port}") from exc

    return _remember_published_url(
        PublishedRouteDoodleURL(app.url, "local", "Only reachable from the machine running the notebook."),
        namespace,
        cache_key,
    )


def _remember_published_url(
    published: PublishedRouteDoodleURL,
    namespace: dict[str, Any] | None,
    cache_key: str,
) -> PublishedRouteDoodleURL:
    if namespace is not None:
        namespace[cache_key] = published
    return published


def _explicit_public_url(port: int) -> str | None:
    for key in (f"ROUTEDOODLE_PUBLIC_URL_{port}", "ROUTEDOODLE_PUBLIC_URL"):
        raw = os.environ.get(key)
        if raw:
            return raw.rstrip("/") + "/"
    return None


def _start_public_tunnel(
    provider: str,
    app: RouteDoodleWebApp,
    namespace: dict[str, Any] | None,
    cache_key: str,
) -> PublishedRouteDoodleURL | None:
    if provider == "ngrok":
        return _start_pyngrok_tunnel(app, namespace, cache_key)
    if provider == "cloudflared":
        return _start_cloudflared_tunnel(app, namespace, cache_key)
    raise ValueError(f"Unsupported tunnel provider: {provider}")


def _start_pyngrok_tunnel(
    app: RouteDoodleWebApp,
    namespace: dict[str, Any] | None,
    cache_key: str,
) -> PublishedRouteDoodleURL | None:
    try:
        from pyngrok import ngrok
    except ImportError:
        has_ngrok_token = bool(os.environ.get("ROUTEDOODLE_NGROK_AUTHTOKEN") or os.environ.get("NGROK_AUTHTOKEN"))
        if not _env_flag("ROUTEDOODLE_AUTO_INSTALL_TUNNEL", has_ngrok_token):
            return None
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pyngrok"])
        from pyngrok import ngrok

    token = os.environ.get("ROUTEDOODLE_NGROK_AUTHTOKEN") or os.environ.get("NGROK_AUTHTOKEN")
    if token:
        ngrok.set_auth_token(token)

    tunnel = ngrok.connect(addr=app.port, proto="http", bind_tls=True)
    if namespace is not None:
        namespace[f"{cache_key}_pyngrok_tunnel"] = tunnel

    return PublishedRouteDoodleURL(
        tunnel.public_url.rstrip("/") + "/",
        "ngrok",
        "Public tunnel. Anyone with the URL can reach this notebook-backed app while the tunnel is running.",
    )


def _start_cloudflared_tunnel(
    app: RouteDoodleWebApp,
    namespace: dict[str, Any] | None,
    cache_key: str,
) -> PublishedRouteDoodleURL | None:
    cloudflared_bin = os.environ.get("ROUTEDOODLE_CLOUDFLARED_BIN") or shutil.which("cloudflared")
    if not cloudflared_bin:
        return None

    proc = subprocess.Popen(
        [
            cloudflared_bin,
            "tunnel",
            "--url",
            f"http://127.0.0.1:{app.port}",
            "--no-autoupdate",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    lines: list[str] = []

    def collect_output() -> None:
        if proc.stdout is None:
            return
        for line in proc.stdout:
            lines.append(line)

    reader = threading.Thread(target=collect_output, name=f"cloudflared-{app.port}-reader", daemon=True)
    reader.start()

    pattern = re.compile(r"https://[-a-zA-Z0-9.]+\.trycloudflare\.com")
    deadline = time.time() + 25
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("cloudflared exited before a tunnel URL was created: " + "".join(lines[-8:]))

        for line in lines:
            match = pattern.search(line)
            if match:
                if namespace is not None:
                    namespace[f"{cache_key}_cloudflared_proc"] = proc
                    namespace[f"{cache_key}_cloudflared_reader"] = reader
                return PublishedRouteDoodleURL(
                    match.group(0).rstrip("/") + "/",
                    "cloudflared",
                    "Public tunnel. Anyone with the URL can reach this notebook-backed app while the tunnel is running.",
                )
        time.sleep(0.25)

    proc.terminate()
    raise TimeoutError("Timed out waiting for cloudflared to report a trycloudflare.com URL")


def _env_flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _find_available_port(host: str, start_port: int) -> int:
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    raise OSError(f"No available port found from {start_port} to {start_port + 49}")


def _render_page_html(page: Any) -> str:
    if hasattr(page, "get_root"):
        return page.get_root().render()
    if isinstance(page, bytes):
        return page.decode("utf-8")
    return str(page)


def _parse_coords(raw_coords: Any) -> list[tuple[float, float]]:
    if not isinstance(raw_coords, list):
        raise ValueError("coords must be a list of [lat, lon] pairs")

    coords: list[tuple[float, float]] = []
    for item in raw_coords:
        if not isinstance(item, list | tuple) or len(item) != 2:
            raise ValueError("coords must contain [lat, lon] pairs")
        lat = float(item[0])
        lon = float(item[1])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("coords contains an invalid latitude or longitude")
        coords.append((lat, lon))

    if len(coords) < 2:
        raise ValueError("Draw at least two points before routing")
    return coords


def _route_payload(namespace: dict[str, Any], coords: list[tuple[float, float]], method: str) -> dict[str, Any]:
    _require(namespace, "rdp_simplify")
    _require(namespace, "extract_subgraph")
    _require(namespace, "G_houston")
    _require(namespace, "route_km")
    _require(namespace, "route_safety_stats")

    simplified = namespace["rdp_simplify"](coords, eps_m=20.0)
    if len(simplified) < 2:
        raise ValueError("Drawing too short after simplification")

    graph = namespace["extract_subgraph"](namespace["G_houston"], coords, padding_m=800)
    routes: list[dict[str, Any]] = []

    if method in {"gnn", "both"}:
        _require(namespace, "gnn_neural_impedance_route")
        _require(namespace, "model")
        start = time.time()
        route_coords = namespace["gnn_neural_impedance_route"](namespace["model"], graph, simplified)
        if route_coords:
            routes.append(_route_result(namespace, graph, route_coords, "GNN v3", "#E84545", start))

    if method in {"dijkstra", "both"}:
        _require(namespace, "dijkstra_route")
        start = time.time()
        route_coords = namespace["dijkstra_route"](graph, simplified)
        if route_coords:
            routes.append(_route_result(namespace, graph, route_coords, "Dijkstra", "#27ae60", start))

    return {
        "run_profile": namespace.get("RUN_PROFILE"),
        "artifact_version": namespace.get("ARTIFACT_VERSION"),
        "input_points": len(coords),
        "simplified_points": len(simplified),
        "subgraph": {
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
        },
        "routes": routes,
    }


def _route_result(
    namespace: dict[str, Any],
    graph: Any,
    route_coords: list[tuple[float, float]],
    name: str,
    color: str,
    start_time: float,
) -> dict[str, Any]:
    return {
        "name": name,
        "color": color,
        "coords": [[float(lat), float(lon)] for lat, lon in route_coords],
        "km": float(namespace["route_km"](route_coords)),
        "seconds": time.time() - start_time,
        "stats": namespace["route_safety_stats"](graph, route_coords),
    }


def _require(namespace: dict[str, Any], name: str) -> None:
    if name not in namespace:
        raise RuntimeError(f"Notebook variable/function {name!r} is not available. Run the earlier notebook sections first.")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return _json_safe(value.item())
    return value
