import json
from app.database import SessionLocal
from app.models import Workflow
db = SessionLocal()
workflows = db.query(Workflow).filter(Workflow.is_agent_task == False).all()
print(f"Found {len(workflows)} workflows")
for w in workflows:
    print(f"\nWorkflow: {w.name} (id={w.id}, active={w.is_active})")
    for n in (w.nodes or []):
        ntype = n.get("type", "")
        if "schedule" in ntype or "start" in ntype:
            print(f"  type: {ntype}")
            print(f"  keys: {list(n.keys())}")
            for k in n.keys():
                if k not in ("id", "type", "label", "position"):
                    print(f"  {k}: {json.dumps(n[k], indent=2)}")
db.close()
