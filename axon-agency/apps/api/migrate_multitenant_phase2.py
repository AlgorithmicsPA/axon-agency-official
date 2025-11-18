"""
Database migration for FASE 7 - Phase 2: Auth + Tenant Context.

This script adds tenant_id column to users table.

Migration is idempotent - can be run multiple times safely.
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "axon.db"


def migrate():
    """Execute Phase 2 migration: add tenant_id to users."""
    logger.info(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        logger.info("Phase 2: Adding 'tenant_id' column to 'users' table...")
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tenant_id' in columns:
            logger.info("✓ Column 'tenant_id' already exists in 'users'")
        else:
            cursor.execute("ALTER TABLE users ADD COLUMN tenant_id VARCHAR")
            logger.info("✓ Column 'tenant_id' added to 'users'")
        
        # Create index on users.tenant_id
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id)")
        logger.info("✓ Index on 'users.tenant_id' created")
        
        # Commit changes
        conn.commit()
        logger.info("=" * 60)
        logger.info("✅ PHASE 2 MIGRATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info("Summary:")
        logger.info("  - Column 'users.tenant_id' ready (nullable)")
        logger.info("  - Index created")
        logger.info("  - Existing users have tenant_id = NULL (backward compatible)")
        logger.info("  - Users can now be assigned to tenant workspaces")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
