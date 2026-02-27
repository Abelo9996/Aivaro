import sqlite3
conn = sqlite3.connect('aivaro.db')
for sql in [
    "ALTER TABLE users ADD COLUMN plan VARCHAR DEFAULT 'trial'",
    "ALTER TABLE users ADD COLUMN trial_started_at TIMESTAMP",
    "ALTER TABLE users ADD COLUMN total_runs_used INTEGER DEFAULT 0",
]:
    try:
        conn.execute(sql)
    except Exception as e:
        print(f"  skip: {e}")
conn.commit()
conn.execute("UPDATE users SET trial_started_at = datetime('now') WHERE trial_started_at IS NULL")
conn.execute("UPDATE users SET plan = 'growth' WHERE email = 'test@aivaro.com'")
conn.commit()
cur = conn.execute('SELECT email, plan, total_runs_used FROM users')
for r in cur.fetchall():
    print(r)
conn.close()
print("Done")
