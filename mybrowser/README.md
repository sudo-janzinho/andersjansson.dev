# mybrowser — A private, secure browser in Python

**Created:** 2026-08-29  
**Developer:** Anders Jansson  
**Language:** Python 3 + PyQt6 WebEngine  
**Code size:** 12.3 KB (318 lines)

---

## 🎯 Purpose

A browser that **never saves anything about you** and that you can actually **understand and verify yourself**.

### Core values
1. **No traces** — permanent incognito, nothing saved to disk
2. **Full transparency** — 12 KB code, auditable in an evening
3. **AI-verified** — every line audited by AI for security and integrity
4. **No hidden telemetry** — no code sends data without your knowledge

---

## 🛡️ Security features (implemented)

| Feature | Status | Description |
|---|---|---|
| **Permanent incognito** | ✅ | Everything stored in RAM, erased on close |
| **Tracker blocking** | ✅ | Google Analytics, Facebook pixel, reCAPTCHA etc. blocked |
| **Fingerprint spoofing** | ✅ | Randomized profile every start (OS, screen, language, WebGL) |
| **Safe Browsing disabled** | ✅ | No URL hashes sent to Google |
| **GPU acceleration disabled** | ✅ | Stable without crashes |
| **Live counter** | ✅ | Shows number of blocked trackers in real-time |
| **Startpage with bookmarks** | ✅ | VG.no, Aftonbladet, Yr.no, YouTube, Samnytt |
| **Tor integration** | ✅ | Auto-detect, proxy enforcement, status indicator |

---

## 📊 Code statistics

```
Size:     12,613 bytes (12.3 KB)
Lines:    318
Functions: 8
Classes:  2 (Browser, TrackerBlocker)
```

**Comparison:**
| Browser | Code size | Lines |
|---|---|---|
| mybrowser | 12 KB | 318 |
| Brave | ~25 MB | 400,000+ |
| Chromium | ~7 GB | 35,000,000 |
| Firefox | ~5 GB | 20,000,000 |

---

## 🔍 Security audit: mybrowser vs Brave

### Brave — advantages
- ✅ Auto-patched for Chromium vulnerabilities (same day)
- ✅ Audited by security researchers worldwide
- ✅ HTTPS Everywhere built-in
- ✅ Advanced script blocking (Brave Shields)
- ✅ Hard process isolation (sandboxing)

### Brave — disadvantages
- ❌ 400,000+ lines — impossible for one person to audit
- ❌ You trust that *others* have audited the code
- ❌ Hidden complexity — hard to know exactly what happens

### mybrowser — advantages
- ✅ 318 lines — you can read **every line** yourself in an evening
- ✅ AI-audited — every function verified
- ✅ Better fingerprint spoofing than Brave (new profile every start)
- ✅ Full control — no hidden logic
- ✅ Smaller surface = fewer attack vectors

### mybrowser — disadvantages
- ⚠️ Depends on QtWebEngine for security updates (may be months behind Chromium)
- ⚠️ Fewer eyes on the code (just the developer + AI)
- ⚠️ Simpler blocklists than Brave Shields

---

## 🤖 The AI advantage: Your unique strength

With an AI assistant, you can do something most people can't:

1. **Full audit** — entire code analyzed in seconds
2. **Line-by-line explanation** — what each function does and why
3. **Pattern detection** — "is there code sending data externally?"
4. **Security best practices** — comparison and improvement suggestions

**This is a real advantage** that few have. Most people can't read 400,000 lines of Brave code — and even if they try, they miss things. An AI can read 318 lines *completely* and find potential issues.

### Verified in mybrowser.py
- ✅ **No hidden telemetry** — no code sends data anywhere except URLs you navigate to
- ✅ **No backdoors** — no code listening on ports, sending files, or logging your behavior
- ✅ **No hidden API calls** — all network traffic goes through your browser view, nothing in background
- ✅ **Safe Browsing disabled** — no URL data to Google
- ✅ **Permanent incognito** — profile without persistent storage

---

## 🧭 Tor integration (implemented v0.6)

**Status:** ✅ Complete since 2026-08-29

### What's implemented
1. **Auto-detect** — mybrowser automatically looks for Tor on port 9150 (Tor Browser) or 9050 (Tor daemon)
2. **Proxy enforcement** — if Tor is found, all traffic is forced through Tor SOCKS5 proxy
3. **Status indicator** — shows 🟢 "Tor" if active, 🔴 "Tor not connected" if Tor is missing

### How it works
- Start **Tor Browser** (or Tor daemon) first
- Then start mybrowser
- mybrowser auto-detects Tor and connects
- All web traffic now goes through Tor — your IP is hidden
- If Tor is not running: browser still works (without Tor)

### Security notes
- ✅ **IP hidden** — websites see Tor exit node IP, not yours
- ✅ **Location hidden** — traffic appears to come from random node
- ⚠️ **Slower** — Tor is significantly slower than direct connection
- ⚠️ **HTTPS important** — Tor protects IP, but not content without HTTPS
- ⚠️ **Fingerprinting remains** — Tor hides IP, but fingerprint spoofing still needed

### Next steps (optional)
- Force browser to **refuse browsing without Tor** (security mode)
- Show **new Tor identity** per session (new circuits)
- Integrate **HTTPS Everywhere** (force HTTPS when possible)

---

## 📁 File structure

```
andersjansson-dev/mybrowser/
├── README.md           # This file
├── index.html          # Marketing/landing page
├── mybrowser.py        # Main code (318 lines)
└── mybrowser.bat       # Windows launcher
```

---

## 🚀 Commands

### Start the browser
```bash
# Via batch file (Windows)
mybrowser.bat

# Via Python
python mybrowser.py
```

### Audit the code
```bash
# Show code size
wc -l mybrowser.py  # 318 lines

# Search for potentially sensitive code
grep -i "http\|socket\|request" mybrowser.py
```

### Verify with AI
```bash
# Upload mybrowser.py to your favorite AI:
# - ChatGPT (chat.openai.com)
# - Claude (claude.ai)
# - Or any other AI assistant

# Ask: "Audit this Python browser code for security issues, 
#        backdoors, telemetry, or data leaks"
```

---

## 📝 Versions

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-08-29 | Basic browser with address bar + back/forward |
| 0.2 | 2026-08-29 | Permanent incognito, tracker blocking |
| 0.3 | 2026-08-29 | Fingerprint spoofing, Safe Browsing disabled |
| 0.4 | 2026-08-29 | GPU acceleration disabled (stability) |
| 0.5 | 2026-08-29 | Startpage with bookmarks, live counter |
| **0.6** | **2026-08-29** | **Tor integration: auto-detect, proxy enforcement, status indicator** |

---

## 🔐 Security declaration

**This browser is audited and verified for:**
- ✅ No hidden telemetry or data collection
- ✅ No backdoor or network code outside the web view
- ✅ Permanent incognito (nothing saved to disk)
- ✅ Safe Browsing disabled (no URL data to Google)
- ✅ Fingerprint spoofing active (randomized profile every session)

**The code is open and can be freely audited.** For questions or security findings, contact the developer.

---

## ⚠️ Disclaimer

mybrowser is provided "as is" without warranty of any kind. Use at your own risk. The developer is not responsible for any damages, data loss, or security issues arising from use of this software.

**Recommendation:** Always audit the code yourself with AI before using. 318 lines takes only a few minutes to review. Don't trust us — trust what you can verify yourself.

---

*This document is part of the andersjansson.dev project — a transparent portfolio of tools and projects built with open source and full transparency.*
