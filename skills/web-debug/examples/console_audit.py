from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Example: Multi-page console audit - walk a list of routes and report
# errors/warnings/failed requests per page, deduplicated and truncated.

BASE = 'http://localhost:5173'  # Confirm the actual port from server startup logs
ROUTES = ['/', '/about', '/settings']  # Replace with your routes

NOISE_TYPES = ('log', 'debug', 'info')  # Dev-server noise; signal is warning/error/pageerror
MAX_LEN = 500  # Truncate verbose framework warnings

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for route in ROUTES:
        msgs = []
        # Fresh page per route so logs don't mix between pages
        page = browser.new_page()
        # Bind msgs via default arg (m=msgs) - a plain closure would late-bind
        # and dump every page's events into the last route's list
        page.on('console', lambda msg, m=msgs: msg.type not in NOISE_TYPES
                and m.append(f'[console.{msg.type}] {msg.text[:MAX_LEN]}'))
        page.on('pageerror', lambda err, m=msgs: m.append(f'[pageerror] {str(err)[:MAX_LEN]}'))
        # requestfailed is a hint, not proof - see "Interpreting Failures" in SKILL.md
        page.on('requestfailed', lambda req, m=msgs: m.append(
            f'[requestfailed] {req.url[:MAX_LEN]} {req.failure or "unknown"}'))
        page.on('response', lambda res, m=msgs: res.status >= 400
                and m.append(f'[http {res.status}] {res.url[:MAX_LEN]}'))

        page.goto(BASE + route, wait_until='domcontentloaded')
        try:
            page.wait_for_function(
                "document.body.innerText.trim().length > 0", timeout=5000)
        except PlaywrightTimeoutError:
            pass  # text-free page - still collect whatever logs arrive
        # Fixed pause is legitimate here: hydration warnings and async errors
        # arrive after domcontentloaded
        page.wait_for_timeout(2500)
        page.close()

        # Deduplicate repeated messages (e.g. 94 identical Vue warnings)
        counts = {}
        for m in msgs:
            counts[m] = counts.get(m, 0) + 1
        results[route] = counts

    browser.close()

for route, counts in results.items():
    total = sum(counts.values())
    print(f"\n=== {route}: {total} messages, {len(counts)} unique ===")
    for m, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        prefix = f"{n}x " if n > 1 else ""
        print(f"  {prefix}{m}")
