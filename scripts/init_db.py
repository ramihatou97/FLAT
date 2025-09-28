#!/usr/bin/env python3
"""
Database initialization script
Creates tables and sets up the database for the Medical Knowledge Platform
"""

import asyncio
import logging
from sqlalchemy import text

from src.core.database import db_manager, Base
from src.core.config import settings
from src.models import Chapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_database():
    """Create database if it doesn't exist"""
    try:
        # Extract database name from URL
        db_url_parts = settings.database_url.split('/')
        db_name = db_url_parts[-1]
        base_url = '/'.join(db_url_parts[:-1])

        # Connect to postgres database to create our database
        from sqlalchemy.ext.asyncio import create_async_engine
        postgres_engine = create_async_engine(f"{base_url}/postgres")

        async with postgres_engine.begin() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )

            if not result.fetchone():
                logger.info(f"Creating database: {db_name}")
                await conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database {db_name} created successfully")
            else:
                logger.info(f"Database {db_name} already exists")

        await postgres_engine.dispose()

    except Exception as e:
        logger.warning(f"Could not create database (may already exist): {e}")

async def create_tables():
    """Create all tables"""
    try:
        logger.info("Creating database tables...")

        async with db_manager.engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

async def seed_sample_data():
    """Add some sample data for testing"""
    try:
        logger.info("Adding sample data...")

        async with db_manager.get_session() as session:
            # Check if we already have data
            from sqlalchemy import select
            result = await session.execute(select(Chapter))
            existing_chapters = result.scalars().all()

            if existing_chapters:
                logger.info("Sample data already exists, skipping...")
                return

            # Create sample chapters
            sample_chapters = [
                Chapter(
                    title="Introduction to Neurosurgery",
                    content="Neurosurgery is a medical specialty dealing with the diagnosis and treatment of disorders of the nervous system...",
                    summary="Basic introduction to neurosurgical principles and practice",
                    specialty="neurosurgery",
                    status="published",
                    metadata={"word_count": 15, "version": "1.0", "sample": True}
                ),
                Chapter(
                    title="Brain Tumor Classification",
                    content="Brain tumors are classified according to the World Health Organization (WHO) classification system...",
                    summary="Comprehensive overview of brain tumor types and classification",
                    specialty="neurosurgery",
                    status="published",
                    metadata={"word_count": 12, "version": "1.0", "sample": True}
                ),
                Chapter(
                    title="Spinal Surgical Techniques",
                    content="Modern spinal surgery encompasses a wide range of techniques for treating spinal disorders...",
                    summary="Overview of contemporary spinal surgical approaches",
                    specialty="neurosurgery",
                    status="draft",
                    metadata={"word_count": 13, "version": "1.0", "sample": True}
                )
            ]

            for chapter in sample_chapters:
                session.add(chapter)

            await session.commit()
            logger.info(f"Added {len(sample_chapters)} sample chapters")

    except Exception as e:
        logger.error(f"Failed to seed sample data: {e}")
        raise

async def test_database():
    """Test database connectivity and basic operations"""
    try:
        logger.info("Testing database connectivity...")

        # Test health check
        is_healthy = await db_manager.health_check()
        if not is_healthy:
            raise Exception("Database health check failed")

        # Test basic query
        async with db_manager.get_session() as session:
            from sqlalchemy import select, func
            result = await session.execute(select(func.count(Chapter.id)))
            chapter_count = result.scalar()

        logger.info(f"Database test successful. Found {chapter_count} chapters.")

    except Exception as e:
        logger.error(f"Database test failed: {e}")
        raise

async def main():
    """Main initialization function"""
    logger.info("🚀 Initializing Medical Knowledge Platform Database...")

    try:
        # Step 1: Create database (if needed)
        await create_database()

        # Step 2: Create tables
        await create_tables()

        # Step 3: Add sample data
        await seed_sample_data()

        # Step 4: Test database
        await test_database()

        logger.info("✅ Database initialization completed successfully!")
        logger.info(f"Database URL: {settings.database_url}")
        logger.info("You can now start the application with: python simple_main.py")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return 1

    finally:
        await db_manager.close()

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())