"""migrate_user_tech_stack_json_format

Revision ID: f5424627a4e4
Revises: 2665cc9cc20b
Create Date: 2026-05-24 14:41:54.543849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# revision identifiers, used by Alembic.
revision: str = 'f5424627a4e4'
down_revision: Union[str, Sequence[str], None] = '2665cc9cc20b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

Base = declarative_base()

# Minimalistic Model definition for data migration targeting rows
class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.String, primary_key=True)
    tech_stack = sa.Column(sa.JSON)


def upgrade() -> None:
    # Bind an active session context directly onto the migration connection pipeline
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    users = session.query(User).all()
    
    for user in users:
        # Avoid processing uninitialized rows or data already migrated
        if not user.tech_stack:
            continue
            
        # Check if row is currently in the legacy shape: {"interests": [...], "level": "..."}
        if "interests" in user.tech_stack and "level" in user.tech_stack:
            legacy_interests = user.tech_stack.get("interests") or []
            legacy_level = user.tech_stack.get("level") or "Beginner"
            
            # Map old values to the new shape: {"React": "Beginner", "Python": "Beginner"}
            new_stack = {tech: legacy_level for tech in legacy_interests}
            
            # Commit mutations directly back onto the row reference
            user.tech_stack = new_stack
            
    session.commit()
    session.close()


def downgrade() -> None:
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    users = session.query(User).all()
    
    for user in users:
        if not user.tech_stack:
            continue
            
        # Revert back to legacy shape if data does not match the old keys
        if "interests" not in user.tech_stack:
            # Gather keys as interest nodes, assign a median blanket tier parameter
            legacy_interests = list(user.tech_stack.keys())
            legacy_level = "Intermediate" if legacy_interests else "Beginner"
            
            user.tech_stack = {
                "interests": legacy_interests,
                "level": legacy_level
            }
            
    session.commit()
    session.close()
