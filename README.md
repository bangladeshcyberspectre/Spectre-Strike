<div align="center">

```
   ██████╗  ██████╗   ███████╗  ██████╗ ████████╗ ██████╗   ███████╗
  ██╔════╝  ██╔══██╗  ██╔════╝ ██╔════╝ ╚══██╔══╝ ██╔══██╗  ██╔════╝
  ╚█████╗   ██████╔╝  █████╗   ██║         ██║    ██████╔╝  █████╗
   ╚════██╗ ██╔═══╝   ██╔══╝   ██║         ██║    ██╔══██╗  ██╔══╝
  ██████╔╝  ██║       ███████╗ ╚██████╗    ██║    ██║  ██║  ███████╗
  ╚═════╝   ╚═╝       ╚══════╝  ╚═════╝    ╚═╝    ╚═╝  ╚═╝  ╚══════╝
```

# Spectre Strike v3.0

**Advanced Multi-Vector Network Stress Testing Tool**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)
![Version](https://img.shields.io/badge/Version-3.0-cyan?style=flat-square)
![Team](https://img.shields.io/badge/Team-Bangladesh%20Cyber%20Spectre-red?style=flat-square)
![Author](https://img.shields.io/badge/Author-Ochena%20Gamer-orange?style=flat-square)

> Built by **Ochena Gamer** | Team **Bangladesh Cyber Spectre (BCS)**

</div>

---

## Overview

Spectre Strike is a Python-based network stress testing tool with a live terminal display. It supports three attack vectors — HTTP Flood, UDP Flood, and TCP Flood — with real-time scrolling logs, live packet rate counter, power control, and unlimited thread support.

Designed for **network load testing**, **server stress analysis**, and **cybersecurity research**.

---

## Features

- **3 Attack Modes** — HTTP Flood, UDP Flood, TCP Flood
- **Live Scrolling Display** — requests scroll upward in real time
- **Live Stats Bar** — total sent, errors, packets/sec, power bar
- **Unlimited Threads** — no thread cap, limited only by system resources
- **Power Control (1–10)** — fine-grained speed control
- **Random User-Agent Rotation** — bypass simple filters
- **X-Forwarded-For Spoofing** — randomized source IP headers (HTTP)
- **Random Path Generation** — avoid cache hits and WAF fingerprinting
- **Proxy Support** — route through Tor or Burp Suite
- **Flicker-free Terminal UI** — ANSI cursor-based redraw
- **Cross-platform** — Windows, Linux, macOS

---

## Attack Modes

### [1] HTTP Flood — Layer 7
Sends real HTTP GET requests mimicking browser traffic. Hits the web application layer directly — forces the server to generate pages, query databases, and allocate memory per request.

**Best against:** Unprotected websites, shared hosting, weak VPS, custom web panels.

### [2] UDP Flood — Layer 4
Sends raw UDP packets at maximum speed. No handshake required — purely bandwidth and processing exhaustion.

**Best against:** Game servers, DNS servers, unprotected network infrastructure.

### [3] TCP Flood — Layer 4
Opens TCP connections rapidly, exhausting the server's connection table. New legitimate connections cannot be established.

**Best against:** Services with limited connection pools, exposed TCP ports.

---

## Requirements

```
Python 3.8+
requests
```

```bash
pip install requests
```

---

## Installation

```bash
git clone https://github.com/bangladeshcyberspectre/Spectre-Strike.git
cd spectre-strike
pip install -r requirements.txt
python spectre_strike.py
```

---

## Usage

Run the tool:

```bash
python spectre_strike.py
```

Main menu appears:

```
  [1]  HTTP Flood   (Website / Layer 7)
  [2]  UDP Flood    (Layer 4 — raw packets)
  [3]  TCP Flood    (Layer 4 — connection flood)
  [4]  Exit
```

### HTTP Flood Example

```
Website URL : http://target.com
Power       : 8
Threads     : 100
```

### UDP Flood Example

```
IP or Domain : 192.168.1.1
Port         : 0  (random)
Power        : 10
Threads      : 200
```

### TCP Flood Example

```
IP or Domain : 192.168.1.1
Port         : 80
Power        : 9
Threads      : 150
```

---

## Live Display

```
──────────────────────────────────────────────────────
│      Spectre Strike v3.0  |  HTTP FLOOD  |  BCS   │
──────────────────────────────────────────────────────
 [14:23:01] GET http://target.com/?cache=58291  [200]
 [14:23:01] GET http://target.com/api/v1/?38821 [200]
 [14:23:02] GET http://target.com/?id=92011     [200]
 [14:23:02] ERR connection timeout
 [14:23:02] GET http://target.com/wp-login.php  [403]
 [14:23:03] GET http://target.com/?cache=71823  [200]
 [14:23:03] GET http://target.com/search?q=4421 [200]
──────────────────────────────────────────────────────
 TARGET   http://target.com        THREADS  100
 SENT     14829         ERRORS  12       RATE  487/s
 POWER    ████████████░░░░░░░░  8/10
──────────────────────────────────────────────────────
 Press Ctrl+C to stop
```

---

## Power Levels

| Power | Delay | Use Case |
|-------|-------|----------|
| 1–3 | 150–500ms | Low and slow, stealth testing |
| 4–6 | 20–80ms | Medium load test |
| 7–8 | 3–20ms | High intensity |
| 9 | 1ms | Near maximum |
| 10 | 0 | Maximum — no delay |

---

## Performance Reference

| Mode | Threads | Power | Approx Rate |
|------|---------|-------|-------------|
| UDP | 100 | 10 | 50K–200K pkt/s |
| UDP | 500 | 10 | 200K–500K+ pkt/s |
| TCP | 100 | 10 | 5K–20K conn/s |
| HTTP | 100 | 10 | 500–3K req/s |
| HTTP | 500 | 10 | 2K–10K req/s |

*Actual numbers depend on your connection speed, CPU, and target response time.*

---

## File Structure

```
spectre-strike/
├── spectre_strike.py     # Main tool
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── LICENSE               # MIT License
└── .gitignore            # Git ignore rules
```

---

## Author & Team

| | |
|--|--|
| **Author** | Ochena Gamer |
| **Team** | Bangladesh Cyber Spectre (BCS) |
| **Version** | 3.0 |
| **Language** | Python 3 |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Bangladesh Cyber Spectre (BCS)**
*Built for research. Tested in the Storm.*

</div>
