"""
Database migration for FASE 7 - Multi-Tenant Support.

This script:
1. Creates the 'tenants' table if it doesn't exist
2. Adds 'tenant_id' column to 'orders' table if it doesn't exist

Migration is idempotent - can be run multiple times safely.
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "axon.db"


def migrate():
    """Execute multi-tenant migration."""
    logger.info(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # STEP 1: Create tenants table
        logger.info("Step 1: Creating 'tenants' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id VARCHAR PRIMARY KEY,
                slug VARCHAR UNIQUE NOT NULL,
                name VARCHAR NOT NULL,
                business_type VARCHAR DEFAULT 'general',
                contact_email VARCHAR NOT NULL,
                contact_phone VARCHAR,
                contact_name VARCHAR,
                branding JSON,
                settings JSON DEFAULT '{}',
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                notes TEXT DEFAULT ''
            )
        """)
        logger.info("✓ Table 'tenants' created or already exists")
        
        # Create indexes on tenants
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tenants_active ON tenants(active)")
        logger.info("✓ Indexes on 'tenants' created")
        
        # STEP 2: Add tenant_id column to orders
        logger.info("Step 2: Adding 'tenant_id' column to 'orders' table...")
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(orders)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tenant_id' in columns:
            logger.info("✓ Column 'tenant_id' already exists in 'orders'")
        else:
            cursor.execute("ALTER TABLE orders ADD COLUMN tenant_id VARCHAR")
            logger.info("✓ Column 'tenant_id' added to 'orders'")
        
        # Create index on orders.tenant_id
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_tenant_id ON orders(tenant_id)")
        logger.info("✓ Index on 'orders.tenant_id' created")
        
        # Commit changes
        conn.commit()
        logger.info("=" * 60)
        logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info("Summary:")
        logger.info("  - Table 'tenants' ready")
        logger.info("  - Column 'orders.tenant_id' ready (nullable)")
        logger.info("  - All indexes created")
        logger.info("  - System is backward compatible (tenant_id = NULL for existing orders)")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
