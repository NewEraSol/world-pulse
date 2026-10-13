with open('/root/spravodajsky_tep/src/server.py', 'r') as f:
    content = f.read()

target = '''@app.get(/api/alert-hits)
def get_alert_hits(limit: int = 50):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
