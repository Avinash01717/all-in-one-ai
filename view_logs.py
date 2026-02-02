from database import SessionLocal, User, UserLog
from sqlalchemy.orm import joinedload

def view_logs():
    db = SessionLocal()
    # Query logs and join with user info
    logs = db.query(UserLog).options(joinedload(UserLog.user)).all()
    
    if not logs:
        print("No activity logs found.")
        db.close()
        return

    print(f"{'Email':<30} {'Hashed Password':<20} {'Login Time':<25} {'Logout Time'}")
    print("-" * 100)
    
    for log in logs:
        user = log.user
        email = user.email if user else "Unknown"
        # Truncate hash
        pwd = user.hashed_password[:15] + "..." if user and user.hashed_password else "None"
        login_t = log.login_time.strftime("%Y-%m-%d %H:%M:%S") if log.login_time else "N/A"
        logout_t = log.logout_time.strftime("%Y-%m-%d %H:%M:%S") if log.logout_time else "Active"
        
        print(f"{email:<30} {pwd:<20} {login_t:<25} {logout_t}")
    
    db.close()

if __name__ == "__main__":
    view_logs()
