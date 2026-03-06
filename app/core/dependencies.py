from typing import Generator

from app.core.config import settings


def get_settings():
    """Return application settings — useful for DI / testing overrides."""
    return settings


# Example: database session dependency (uncomment when DB is configured)
# from sqlalchemy.orm import Session
# from app.db.session import SessionLocal
#
# def get_db() -> Generator[Session, None, None]:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
