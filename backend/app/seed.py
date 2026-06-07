# seed.py
from app.core.database import SessionLocal
from app.domain.models import User
from app.domain.constants import RoleEnum

def seed_users():
    db = SessionLocal()

    if db.query(User).count() == 0:
        test_users = [
            User(email="angajat@test.com", hashed_password="password", role=RoleEnum.REQUESTER),
            User(email="manager@test.com", hashed_password="password", role=RoleEnum.MANAGER),
            User(email="it@test.com", hashed_password="password", role=RoleEnum.IT_REP),
            User(email="finance@test.com", hashed_password="password", role=RoleEnum.FINANCE),
        ]
        db.add_all(test_users)
        db.commit()
        print("Useri de test adaugati cu succes!")
    else:
        print("Baza de date contine deja useri.")
    db.close()

if __name__ == "__main__":
    seed_users()