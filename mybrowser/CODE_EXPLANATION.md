# mybrowser.py — Line-by-line code explanation

**Total:** 318 lines of Python code  
**Purpose:** A private, secure browser with Tor integration

---

## 📦 Imports (Lines 1-13)

```python
import sys
import os
import socket
import time
import random

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
```

**What it does:**
- `sys`, `os` — System operations, environment variables
- `socket` — Network detection (for Tor auto-detect)
- `time` — Delays for Tor detection retry logic
- `random` — Random values for fingerprint spoofing
- `PyQt6` — GUI framework and web engine (Chromium-based)
- `QNetworkProxy` — Forces traffic through Tor proxy

---

## 🌍 Environment setup (Lines 15-19)

```python
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-safebrowsing --disable-gpu --disable-software-rasterizer"
```

**What it does:**
- Disables Google Safe Browsing (no URL data sent to Google)
- Disables GPU acceleration (prevents crashes on some systems)
- Must be set BEFORE QApplication starts

---

## 🚫 Tracker blocking (Lines 22-58)

```python
BLOCK_SUBSTRINGS = [
    ".googletagmanager.com", "google-analytics.com", "googlesyndication.com",
    "doubleclick.net", "googleadservices.com", "googletagservices.com",
    "fonts.googleapis.com", "fonts.gstatic.com", "recaptcha.net",
    ".facebook.com/tr", "facebook.net/", "connect.facebook.net",
    # ... 40+ more tracker domains
]

class TrackerBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.blocked = 0

    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        if any(blk in url for blk in BLOCK_SUBSTRINGS):
            self.blocked += 1
            info.block(True)
```

**What it does:**
- `BLOCK_SUBSTRINGS` — List of 40+ known tracker/ad domains
- `TrackerBlocker` class — Intercepts every network request
- If URL contains a blocked domain → request is blocked before it leaves
- `self.blocked` — Counter for live display in toolbar

**Security:** No external data is sent to these trackers.

---

## 🎭 Fingerprint spoofing (Lines 61-127)

```python
def _spoof_script():
    # Randomizes: User-Agent, OS, screen resolution, language,
    # CPU cores, memory, timezone, touch support, WebGL renderer
    # Returns JavaScript code that overrides navigator properties
    
def _inject_spoof(page):
    script = QWebEngineScript()
    script.setName("fingerprint_spoof")
    script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
    script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
    script.setRunsOnSubFrames(True)
    script.setSourceCode(_spoof_script())
    page.scripts().insert(script)
```

**What it does:**
- Generates random values for: OS (Windows/Linux/Mac), screen size, language, CPU cores, memory, timezone
- Injects JavaScript into every page BEFORE the page loads
- Overrides `navigator.userAgent`, `navigator.platform`, `screen.width`, etc.
- WebGL renderer faked as "SwiftShader" (software renderer)
- **New random profile every browser start** — looks different each time

**Security:** Websites can't build a stable fingerprint of your device.

---

## 🧱 Browser class (Lines 130-280)

### Constructor (Lines 133-175)

```python
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mybrowser")
        self.resize(1280, 820)

        # Permanent incognito profile
        self.profile = QWebEngineProfile()
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies
        )

        # Tracker blocker
        self.blocker = TrackerBlocker()
        self.profile.setUrlRequestInterceptor(self.blocker)

        # Tor integration
        self.tor_active = False
        self.tor_port = self._detect_tor()
        if self.tor_port:
            self._enable_tor_proxy(self.tor_port)
            self.tor_active = True

        # Web view
        page = QWebEnginePage(self.profile)
        _inject_spoof(page)
        self.view = QWebEngineView()
        self.view.setPage(page)
```

**What it does:**
- Creates window (1280x820)
- Creates incognito profile (everything in RAM, nothing on disk)
- Enables tracker blocker
- Auto-detects Tor and enables proxy if found
- Creates web view with spoofing injected

---

### Tor detection (Lines 177-200)

```python
def _detect_tor(self):
    for port in [9150, 9050]:  # Tor Browser / Tor daemon
        for attempt in range(3):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                if result == 0:
                    return port  # Tor found!
            except Exception:
                pass
            if attempt < 2:
                time.sleep(0.5)  # Retry after 0.5s
    return None  # No Tor found
```

**What it does:**
- Tries to connect to `127.0.0.1:9150` (Tor Browser default)
- If fails, tries `127.0.0.1:9050` (Tor daemon default)
- Retries 3 times with 0.5s delay (handles race conditions)
- Returns port number if Tor is running, `None` otherwise

**Security:** Only checks localhost — no external network calls.

---

### Tor proxy enforcement (Lines 202-212)

```python
def _enable_tor_proxy(self, port):
    proxy = QNetworkProxy()
    proxy.setType(QNetworkProxy.ProxyType.Socks5Proxy)
    proxy.setHostName("127.0.0.1")
    proxy.setPort(port)
    QNetworkProxy.setApplicationProxy(proxy)
    # QtWebEngine automatically uses application proxy
```

**What it does:**
- Creates SOCKS5 proxy configuration
- Points to Tor on localhost (port 9150 or 9050)
- Forces ALL application traffic through Tor
- QtWebEngine inherits this proxy automatically

**Security:** All web traffic is routed through Tor network — IP is hidden.

---

### Toolbar setup (Lines 214-245)

```python
toolbar = QToolBar()
self.btn_back = toolbar.addAction("◀", self.view.back)
self.btn_fwd = toolbar.addAction("▶", self.view.forward)

# Tracker counter
self.blocker_label = QLabel("🛡 0")
self.blocker_label.setStyleSheet("...")
toolbar.addWidget(self.blocker_label)

# Tor status
if self.tor_active:
    self.tor_label = QLabel("🟢 Tor")
else:
    self.tor_label = QLabel("🔴 Tor not connected")
toolbar.addWidget(self.tor_label)

# Address bar
self.address = QLineEdit()
self.address.setPlaceholderText("Enter a web address...")
self.address.returnPressed.connect(self._navigate)
toolbar.addWidget(self.address)
```

**What it does:**
- Back/forward buttons
- Live tracker counter (updates every 0.5s)
- Tor status indicator (green if active, red if not)
- Address bar for URL input

---

### Startpage (Lines 247-300)

```python
def _show_startpage(self):
    bookmarks = [
        ("VG.no", "https://www.vg.no"),
        ("Aftonbladet.se", "https://www.aftonbladet.se"),
        ("Yr.no", "https://www.yr.no"),
        ("YouTube.com", "https://www.youtube.com"),
        ("Samnytt.se", "https://www.samnytt.se"),
    ]
    # Creates buttons for each bookmark
    # On click: loads URL in web view
```

**What it does:**
- Shows startpage with 5 bookmark buttons
- Clicking a button loads the URL
- After first navigation, switches to normal browser view

---

### Navigation (Lines 302-320)

```python
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
```

**What it does:**
- If text contains spaces → treats as search query (DuckDuckGo)
- If no protocol → adds `https://`
- Otherwise uses URL as-is
- Loads the URL in web view

---

### Helper functions (Lines 322-340)

```python
def _on_url_changed(self, url):
    self.address.setText(url.toString())

def _on_first_navigation(self, url):
    # Switches from startpage to browser view

def _update_buttons(self):
    self.btn_back.setEnabled(self.view.history().canGoBack())
    self.btn_fwd.setEnabled(self.view.history().canGoForward())

def _update_blocker_count(self):
    self.blocker_label.setText(f"🛡 {self.blocker.blocked}")
```

**What it does:**
- Updates address bar when URL changes
- Enables/disables back/forward buttons based on history
- Updates tracker counter every 0.5 seconds

---

## 🚀 Main function (Lines 343-355)

```python
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("mybrowser")
    app.setOrganizationName("mybrowser")

    win = Browser()
    win.show()
    sys.exit(app.exec())
```

**What it does:**
- Creates Qt application
- Creates browser window
- Shows window
- Starts event loop (waits for user actions)

---

## 🏁 Entry point (Lines 357-358)

```python
if __name__ == "__main__":
    main()
```

**What it does:**
- Standard Python entry point
- Runs `main()` when script is executed

---

## 🔍 Security summary

### What the code does NOT do:
- ❌ No telemetry or data collection
- ❌ No external API calls (except URLs you navigate to)
- ❌ No file system access (except temporary cache in RAM)
- ❌ No network sockets (except through web view)
- ❌ No keylogging or behavior tracking

### What the code DOES do:
- ✅ Blocks 40+ known tracker domains
- ✅ Spoofs fingerprint (random profile every start)
- ✅ Forces traffic through Tor (if available)
- ✅ Stores everything in RAM (nothing on disk)
- ✅ Disables Google Safe Browsing
- ✅ Shows live tracker counter

---

## 📊 Code breakdown by category

| Category | Lines | Percentage |
|---|---|---|
| Imports + setup | 19 | 6% |
| Tracker blocking | 37 | 12% |
| Fingerprint spoofing | 67 | 21% |
| Browser class (UI) | 150 | 47% |
| Tor integration | 35 | 11% |
| Main + entry | 10 | 3% |
| **Total** | **318** | **100%** |

---

*This explanation is part of the mybrowser documentation. Audit the code yourself with AI before using.*
