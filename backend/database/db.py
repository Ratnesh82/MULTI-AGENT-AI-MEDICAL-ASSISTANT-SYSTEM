"""
MongoDB async connection using Motor.
Provides a single database client shared across the app.
"""
import motor.motor_asyncio
from config import settings

# Motor async client — re-used across the app lifecycle
client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
db = client[settings.db_name]

# Collection references
patients_col = db["patients"]
doctors_col = db["doctors"]
appointments_col = db["appointments"]
wellness_logs_col = db["wellness_logs"]


async def init_db():
    """Create indexes on startup for performance."""
    await patients_col.create_index("email", unique=True)
    await appointments_col.create_index("patient_id")
    await appointments_col.create_index("slot_time")
    await doctors_col.create_index("specialty")
