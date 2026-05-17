"""Set is_admin=True for a user by email."""
import asyncio
import sys
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User


async def main(email: str):
    async with AsyncSessionLocal() as db:
        r = await db.execute(select(User).where(User.email == email))
        user = r.scalar_one_or_none()
        if not user:
            print(f"Lietotajs nav atrasts: {email}")
            return
        user.is_admin = True
        await db.commit()
        print(f"OK: {user.username} ({user.email}) ir tagad admins.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Lietosana: python make_admin.py <email>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
