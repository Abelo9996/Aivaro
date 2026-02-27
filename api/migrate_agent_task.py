import sqlite3

conn = sqlite3.connect('aivaro.db')

# Add column
try:
    conn.execute('ALTER TABLE workflows ADD COLUMN is_agent_task BOOLEAN DEFAULT 0')
    conn.commit()
    print("Added is_agent_task column")
except Exception as e:
    print(f"Column might already exist: {e}")

# Mark existing agent-task workflows (empty nodes)
cur = conn.execute("SELECT id, name FROM workflows WHERE nodes = '[]'")
rows = cur.fetchall()
print(f"Found {len(rows)} agent-task workflows to mark")
for r in rows:
    conn.execute("UPDATE workflows SET is_agent_task = 1 WHERE id = ?", (r[0],))
    print(f"  Marked: {r[1]}")

conn.commit()
conn.close()
print("Done")
