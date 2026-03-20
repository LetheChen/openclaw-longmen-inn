from app.db.session import SessionLocal
from app.db import models

db = SessionLocal()

# 检查任务状态
tasks = db.query(models.Task).all()
print("=== 任务状态 ===")
for t in tasks[:5]:
    print(f"{t.task_no}: status={t.status.value}, creator_id={t.creator_agent_id}")

# 检查Agent
agents = db.query(models.Agent).all()
print("\n=== Agent列表 ===")
for a in agents:
    print(f"{a.agent_id}: {a.name}")

db.close()
