import subprocess, json, sys, time
def sparql(q):
    for a in range(5):
        out = subprocess.run(["curl", "-s", "-m", "90", "-G", "https://query.wikidata.org/sparql", "--data-urlencode", "query=" + q,
                              "-H", "Accept: application/sparql-results+json"], capture_output=True, text=True).stdout
        try: return json.loads(out)["results"]["bindings"]
        except Exception: time.sleep(10 * (a + 1))
    raise SystemExit("sparql failed: " + out[:300])
if __name__ == "__main__":
    print(json.dumps(sparql(sys.argv[1]), ensure_ascii=False, indent=0)[:3000])
