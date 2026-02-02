import json
import os
from database import SessionLocal, Tool, init_db

def seed_tools():
    init_db()
    db = SessionLocal()
    
    if db.query(Tool).first():
        print("Tools already seeded.")
        db.close()
        return

    json_path = "tools_data.json"
    if not os.path.exists(json_path):
        print(f"File {json_path} not found.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        tools_data = json.load(f)

    for item in tools_data:
        tool = Tool(
            name=item.get("name"),
            category=item.get("category"),
            type=item.get("type"),
            url=item.get("url"),
            icon=item.get("icon"),
            description=item.get("description")
        )
        db.add(tool)
    
    db.commit()
    print(f"Seeded {len(tools_data)} tools into the database.")
    db.close()

if __name__ == "__main__":
    seed_tools()
