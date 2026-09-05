from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.db.models.account import User, Device

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def seed_users(db: AsyncSession) -> None:
    seed_users_data = [
        {
            "email": "admin@aeromind.io",
            "password": "AdminPassword123!",
            "full_name": "System Administrator",
            "role": "admin",
            "is_active": True,
            "is_verified": True,
            "is_approved": True,
            "devices": ["admin-station-01"],
        },
        {
            "email": "pilot@aeromind.io",
            "password": "UserPassword123!",
            "full_name": "Drone Pilot",
            "role": "user",
            "is_active": True,
            "is_verified": True,
            "is_approved": True,
            "devices": ["controller-unit-alpha", "mobile-app-client"],
        },
        {
            "email": "pending@aeromind.io",
            "password": "UserPassword123!",
            "full_name": "Pending Approval User",
            "role": "user",
            "is_active": True,
            "is_verified": True,
            "is_approved": False,
            "devices": [],
        },
    ]

    for user_data in seed_users_data:
        result = await db.execute(select(User).where(User.email == user_data["email"]))
        existing_user = result.scalars().first()

        if not existing_user:
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=user_data["is_active"],
                is_verified=user_data["is_verified"],
                is_approved=user_data["is_approved"],
            )
            db.add(user)
            await db.flush()

            for dev_id in user_data["devices"]:
                device = Device(
                    user_id=user.id,
                    device_id=dev_id,
                    device_info=f"Seeded device {dev_id} for {user.full_name}",
                    is_active=True,
                )
                db.add(device)

            print(f"[SEED] Created user: {user.email} (Role: {user.role})")
        else:
            print(f"[SEED] Skipping existing user: {user_data['email']}")

    await db.commit()