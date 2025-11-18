#!/usr/bin/env python3
"""
Script to generate a development JWT token.
Only use in development environments.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.security import create_access_token
from app.core.types import Role
from app.config import settings

if __name__ == "__main__":
    if not settings.dev_mode:
        print("ERROR: DEV_MODE is disabled. This script only works in development.")
        sys.exit(1)
    
    username = sys.argv[1] if len(sys.argv) > 1 else "dev-admin"
    role = Role.ADMIN
    
    token = create_access_token(username, role)
    
    print("=" * 60)
    print(f"Development Token for: {username}")
    print(f"Role: {role.value}")
    print("=" * 60)
    print(token)
    print("=" * 60)
    print(f"\nExport as environment variable:")
    print(f'export TOKEN="{token}"')
    print(f"\nUse in curl:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:{settings.port}/api/catalog')
    print("=" * 60)
