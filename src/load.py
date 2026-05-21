import logging
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base, Session
from config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

Base = declarative_base()


class WeatherRecord(Base):
    __tablename__ = "weather_records"
    __table_args__ = (
        UniqueConstraint("location", "timestamp", name="uq_location_timestamp"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    wind_speed_kmh = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)


def get_engine():
    return create_engine(DATABASE_URL, echo=False)


def init_db(engine=None):
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
    logger.info("Database schema initialised")
    return engine


def load_records(records: list[dict], engine=None) -> int:
    if not records:
        logger.info("No records to load")
        return 0

    if engine is None:
        engine = get_engine()

    inserted = 0
    skipped = 0

    with Session(engine) as session:
        for rec in records:
            existing = (
                session.query(WeatherRecord)
                .filter_by(location=rec["location"], timestamp=rec["timestamp"])
                .first()
            )
            if existing:
                skipped += 1
                continue

            session.add(WeatherRecord(**rec))
            inserted += 1

        session.commit()

    logger.info("Loaded %d new records, skipped %d duplicates", inserted, skipped)
    return inserted
