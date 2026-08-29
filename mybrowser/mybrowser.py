#!/usr/bin/env python3
"""mybrowser - en enkel, privat webbläsare i Python (PyQt6 + WebEngine).

- Adressfält
- Fram / tillbaka-knappar
- Inga spår kvar: lämna aldrig något om dig (permanent inkognito-profil i RAM)
"""

import sys
import os

# Stäng av Safe Browsing: inga URL-hash:er skickas till Google.
# Stäng av GPU-acceleration: förhindrar krascher p.g.a. GPU-kontextfel.
# Måste sättas innan QApplication/QtWebEngine startas.
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-safebrowsing --disable-gpu --disable-software-rasterizer"

from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtNetwork import QNetworkProxy, QNetworkProxyFactory, QNetworkAccessManager
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QWidget, QVBoxLayout,
    QLabel, QPushButton
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineSettings,
    QWebEngineScript, QWebEngineUrlRequestInterceptor
)

import random
import socket


# Kända spårnings-/annonsdomäner (substring-match): förfrågningar till dessa
# blockeras innan de skickas. Koncentrerad lista över de vanligaste aktörerna.
BLOCK_SUBSTRINGS = [
    # Google-spårare
    ".googletagmanager.com", "google-analytics.com", "googlesyndication.com",
    "doubleclick.net", "googleadservices.com", "googletagservices.com",
    "fonts.googleapis.com", "fonts.gstatic.com", "recaptcha.net",
    "google.com/recaptcha", "gstatic.com",".googleapis.com/",
    "googleusercontent.com/",
    # Meta / Facebook
    ".facebook.com/tr", "facebook.net/", "connect.facebook.net",
    ".fbcdn.net", "meta.com/",
    # Microsoft / LinkedIn / Bing
    ".bing.com/", ".clarity.ms", ".msn.com/", ".linkedin.com/",
    "licdn.com/",
    # Övriga stora nätverk
    ".amazon-adsystem.com", "adnxs.com", ".rubiconproject.com",
    "criteo.com", ".taboola.com", ".outbrain.com", ".quantserve.com",
    ".scorecardresearch.com", ".hotjar.com", ".mixpanel.com",
    ".segment.com/", ".amplitude.com", ".intercom.io", ".crisp.chat",
    ".zendesk.com/", ".fullstory.com", ".branch.io", ".adjust.com/",
    ".stripe.com/",
]


class TrackerBlocker(QWebEngineUrlRequestInterceptor):
    """Stoppar nätverksförfrågningar till kända spårare/annonsnätverk."""
    def __init__(self):
        super().__init__()
        self.blocked = 0

    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        if any(blk in url for blk in BLOCK_SUBSTRINGS):
            self.blocked += 1
            info.block(True)


def _spoof_script():
    """Bygger ett JS-skript som överlagrar fingeravtryckssignaler med
    slumpvalda värden, så att du ser annorlunda ut varje gång.

    Körs före allt annat på sidan (DocumentCreation, main world).
    """
    # Slumpa en "profil" av tekniska egenskaper
    ua_brands = ["Chrome", "Chromium", "Edg", "Firefox", "Safari", "Brave"]
    pick = lambda seq: random.choice(seq)

    os_platforms = [
        ("Win32", "Windows NT 10.0; Win64; x64", "Windows"),
        ("Linux x86_64", "X11; Linux x86_64", "Linux"),
        ("MacIntel", "Macintosh; Intel Mac OS X 10_15_7", "MacIntel"),
    ]
    platform, ua_os, nav_platform = pick(os_platforms)
    language = pick(["en-US", "en-GB", "de-DE", "nb-NO", "sv-SE", "fr-FR"])
    cores = pick([2, 4, 6, 8, 12, 16])
    mem = pick([4, 8, 16, 32, 64])
    tz = pick(["Europe/Oslo", "Europe/Stockholm", "Europe/Berlin", "UTC", "America/New_York"])
    screen_w = pick([1366, 1536, 1600, 1920, 2560])
    screen_h = pick([768, 864, 900, 1080, 1440])
    ua_extra = pick(["", " Mobile; Android 13"])

    brand = pick(ua_brands)
    major = pick(range(90, 132))
    ua = (
        f"Mozilla/5.0 ({ua_os}{ua_extra}) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) {brand}/{major}.0.0.0 Safari/537.36"
    )

    return f"""
(() => {{
  const override = (prop, val) => {{
    try {{ Object.defineProperty(navigator, prop, {{ get: () => val, configurable: true }}); }} catch(e) {{}}
  }};
  try {{ Object.defineProperty(navigator, 'userAgent', {{ get: () => '{ua}', configurable: true }}); }} catch(e) {{}}
  try {{ Object.defineProperty(navigator, 'platform', {{ get: () => '{nav_platform}', configurable: true }}); }} catch(e) {{}}
  try {{ Object.defineProperty(navigator, 'language', {{ get: () => '{language}', configurable: true }}); }} catch(e) {{}}
  try {{ Object.defineProperty(navigator, 'languages', {{ get: () => ['{language}'], configurable: true }}); }} catch(e) {{}}
  override('hardwareConcurrency', {cores});
  override('deviceMemory', {mem});
  override('maxTouchPoints', 0);
  try {{ Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined, configurable: true }}); }} catch(e) {{}}
  try {{ Intl.DateTimeFormat = new Proxy(Intl.DateTimeFormat, {{ construct: () => new (class{{ }})(), apply: () => ({{ resolvedOptions: () => ({{ timeZone: '{tz}' }}) }}) }}); }} catch(e) {{}}
  try {{ screen.width = {screen_w}; screen.height = {screen_h}; screen.availWidth = {screen_w}; screen.availHeight = {screen_h}; }} catch(e) {{}}
  try {{ Object.defineProperty(window, 'outerWidth', {{ get: () => {screen_w}, configurable: true }}); }} catch(e) {{}}
  try {{ Object.defineProperty(window, 'outerHeight', {{ get: () => {screen_h}, configurable: true }}); }} catch(e) {{}}
  // Dölj WebGL-renderaren: rapportera som "SwiftShader" (mjukvarurenderare)
  const noop = () => {{ return 'SwiftShader' }};
  try {{
    const getExt = WebGLRenderingContext.prototype.getExtension;
    const getParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getExtension = function(name) {{
      if (name === 'WEBGL_debug_renderer_info') return {{ UNMASKED_VENDOR_WEBGL: noop, UNMASKED_RENDERER_WEBGL: noop }};
      return getExt.call(this, name);
    }};
    WebGLRenderingContext.prototype.getParameter = function(p) {{
      const r = getParam.call(this, p);
      try {{ if (r === p) return 'SwiftShader'; }} catch(e) {{}}
      return r;
    }};
  }} catch(e) {{}}
  window.navigator.spoof = 'mybrowser-fp';
}})();
"""


def _inject_spoof(page):
    script = QWebEngineScript()
    script.setName("fingerprint_spoof")
    script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
    script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
    script.setRunsOnSubFrames(True)
    script.setSourceCode(_spoof_script())
    page.scripts().insert(script)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mybrowser")
        self.resize(1280, 820)

        # ---- Permanent inkognito: inget sparas på disk ----
        # En fristående QWebEngineProfile (utan namn) är off-the-record:
        # allt lagras i RAM och raderas vid stängning.
        self.profile = QWebEngineProfile()
        self.profile.setHttpCacheType(
            QWebEngineProfile.HttpCacheType.MemoryHttpCache
        )
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies
        )
        self.blocker = TrackerBlocker()
        self.profile.setUrlRequestInterceptor(self.blocker)

        # ---- Tor-integration: auto-detekt + proxy-tvång ----
        self.tor_active = False
        self.tor_port = self._detect_tor()
        print(f"[Tor] Detekterad port: {self.tor_port}")
        if self.tor_port:
            self._enable_tor_proxy(self.tor_port)
            self.tor_active = True
            print(f"[Tor] Aktiverad på port {self.tor_port}")
        else:
            print("[Tor] Ingen Tor-instans hittad - kör utan Tor")

        # ---- WebEngineView (själva webbsidan) ----
        page = QWebEnginePage(self.profile)
        _inject_spoof(page)
        self.view = QWebEngineView()
        self.view.setPage(page)
        self.view.urlChanged.connect(self._on_url_changed)
        self.view.titleChanged.connect(self.setWindowTitle)

        # ---- Verktygsrad: fram/bak + adressfält ----
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.btn_back = toolbar.addAction("◀", self.view.back)
        self.btn_fwd = toolbar.addAction("▶", self.view.forward)
        toolbar.addSeparator()

        # Live-räknare för blockerade spårare, bredvid fram/bak-knapparna
        self.blocker_label = QLabel("🛡 0")
        self.blocker_label.setToolTip("Antal spårare blockerade i denna session")
        self.blocker_label.setStyleSheet(
            "color:#7C8695; padding:0 8px; font-family:'JetBrains Mono',monospace;"
        )
        toolbar.addWidget(self.blocker_label)
        toolbar.addSeparator()

        # Tor-statusindikator
        if self.tor_active:
            self.tor_label = QLabel("🟢 Tor")
            self.tor_label.setToolTip(f"Tor aktiv via port {self.tor_port} — din IP är dold")
        else:
            self.tor_label = QLabel("🔴 Tor ej ansluten")
            self.tor_label.setToolTip("Tor körs inte. Starta Tor Browser för anonym surf.")
        self.tor_label.setStyleSheet(
            "color:#7C8695; padding:0 8px; font-family:'JetBrains Mono',monospace; font-weight:bold;"
        )
        toolbar.addWidget(self.tor_label)
        toolbar.addSeparator()

        self.address = QLineEdit()
        self.address.setPlaceholderText("Skriv en webbadress…")
        self.address.returnPressed.connect(self._navigate)
        toolbar.addWidget(self.address)

        # ---- Startsida med bokmärken ----
        self._show_startpage()

        # Håll fram/bak-knapparna synkade med vad som går att göra
        self.view.loadStarted.connect(self._update_buttons)
        self.view.loadFinished.connect(lambda _: self._update_buttons())

        # Uppdatera räknaren live
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_blocker_count)
        self._timer.start(500)

    def _update_blocker_count(self):
        self.blocker_label.setText(f"🛡 {self.blocker.blocked}")

    def _detect_tor(self):
        """Letar efter Tor SOCKS5-proxy på vanliga portar.
        
        Returnerar portnummer om Tor hittas, annars None.
        Port 9150 = Tor Browser (Windows/Mac)
        Port 9050 = Tor Expert/daemon (Linux)
        
        Försöker 3 gånger med 0.5s fördröjning för att hantera race conditions.
        """
        import time
        for port in [9150, 9050]:
            for attempt in range(3):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2.0)  # Ökad timeout
                    result = sock.connect_ex(('127.0.0.1', port))
                    sock.close()
                    if result == 0:
                        return port
                except Exception as e:
                    pass
                if attempt < 2:
                    time.sleep(0.5)  # Vänta lite innan nästa försök
        return None

    def _enable_tor_proxy(self, port):
        """Tvingar all trafik genom Tor SOCKS5-proxy."""
        proxy = QNetworkProxy()
        proxy.setType(QNetworkProxy.ProxyType.Socks5Proxy)
        proxy.setHostName("127.0.0.1")
        proxy.setPort(port)
        QNetworkProxy.setApplicationProxy(proxy)
        
        # QtWebEngine använder automatiskt applikationens proxy
        # när den är satt via QNetworkProxy.setApplicationProxy()

    def _show_startpage(self):
        """Visar en ren startsida bara med titeln."""
        start_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        # Titel
        title = QLabel("mybrowser")
        title.setStyleSheet(
            "font-size: 48px; font-weight: bold; color: #E6E9EE;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Private browser with Tor integration")
        subtitle.setStyleSheet(
            "font-size: 16px; color: #7C8695; margin-top: 10px;"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        start_widget.setLayout(layout)
        self.setCentralWidget(start_widget)

        # Byt tillbaka till webbläsarvyn när man börjar navigera
        self.view.urlChanged.connect(self._on_first_navigation)
        self._first_nav = True

    def _on_first_navigation(self, url):
        """Byter från startsida till webbläsarvy vid första navigeringen."""
        if self._first_nav:
            self._first_nav = False
            central = QWidget()
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.view)
            central.setLayout(layout)
            self.setCentralWidget(central)
            self.view.urlChanged.disconnect(self._on_first_navigation)

    def _navigate(self):
        text = self.address.text().strip()
        if not text:
            return
        if " " in text or "." not in text:
            url = QUrl("https://duckduckgo.com/?q=" + text.replace(" ", "+"))
        elif not text.startswith(("http://", "https://")):
            url = QUrl("https://" + text)
        else:
            url = QUrl(text)
        self.view.setUrl(url)

    def _on_url_changed(self, url):
        self.address.setText(url.toString())

    def _update_buttons(self):
        self.btn_back.setEnabled(self.view.history().canGoBack())
        self.btn_fwd.setEnabled(self.view.history().canGoForward())


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("mybrowser")
    app.setOrganizationName("mybrowser")

    win = Browser()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
