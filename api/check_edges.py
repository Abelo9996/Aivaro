import sqlite3, json
conn = sqlite3.connect('aivaro.db')
cur = conn.cursor()
cur.execute("SELECT e.workflow_id, w.name, w.edges FROM executions e JOIN workflows w ON e.workflow_id = w.id WHERE e.id = '39ee6b5d-39df-4e0a-ad93-96ffd9f1b6d4'")
row = cur.fetchone()
if row:
    edges = json.loads(row[2]) if row[2] else []
    print(f"WF: {row[1]}")
    for e in edges:
        print(f"  {e.get('source')} -> {e.get('target')}  sh={e.get('sourceHandle')!r}  lb={e.get('label')!r}")
else:
    # Check if prod DB
    print("Not found in local DB. Checking all workflow names...")
    cur.execute("SELECT id, name FROM workflows")
    for r in cur.fetchall():
        print(f"  {r[0][:8]}: {r[1]}")
conn.close()
