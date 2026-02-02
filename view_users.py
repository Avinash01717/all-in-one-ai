from database import SessionLocal, User
import sys

def view_users():
    db = SessionLocal()
    users = db.query(User).all()
    
    if not users:
        print("No users found in the database.")
        return

    print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Hashed Password'}")
    print("-" * 80)
    for user in users:
        # Truncate hash for display
        hash_display = user.hashed_password[:20] + "..." if user.hashed_password else "None"
        print(f"{user.id:<5} {user.full_name:<20} {user.email:<30} {hash_display}")
    
    db.close()

if __name__ == "__main__":
    view_users()
