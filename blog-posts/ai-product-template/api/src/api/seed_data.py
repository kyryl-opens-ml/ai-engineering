from api.db.session import SessionLocal
from api.db.base import Base
from api.db.session import engine
from api.models.item import Item

MOCK_ITEMS = [
    {
        "title": "Build Dashboard",
        "description": "Create main dashboard with key metrics",
    },
    {"title": "User Authentication", "description": "Implement login and signup flows"},
    {"title": "API Integration", "description": "Connect frontend to backend services"},
    {
        "title": "Data Visualization",
        "description": "Add charts and graphs for analytics",
    },
    {
        "title": "Mobile Optimization",
        "description": "Ensure responsive design for mobile",
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Item).count() == 0:
            for item_data in MOCK_ITEMS:
                db.add(Item(**item_data))
            db.commit()
            print(f"Seeded {len(MOCK_ITEMS)} items")
        else:
            print("Database already has items, skipping seed")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
