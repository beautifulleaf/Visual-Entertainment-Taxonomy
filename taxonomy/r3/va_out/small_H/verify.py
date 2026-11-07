import json, os, subprocess, time, sys
H = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(H, "urlcheck.json")
done = json.load(open(P)) if os.path.exists(P) else {}
urls = [u for u in open(os.path.join(H, "urls_needed.txt")).read().split("\n") if u and u not in done]
for i, u in enumerate(urls):
    for attempt in range(3):
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-A", "VETaxonomyBot/0.1 (taxonomy research)", u], capture_output=True, text=True)
        code = r.stdout.strip()
        if code in ("200", "404", "301", "302"): break
        time.sleep(3)
    done[u] = code in ("200", "301", "302")
    if i % 25 == 0:
        json.dump(done, open(P, "w")); print(i, len(urls), u, code, flush=True)
    time.sleep(0.4)
json.dump(done, open(P, "w"))
print("done", sum(done.values()), len(done))
