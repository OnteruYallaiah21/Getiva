#!/usr/bin/env python3
"""Export OpenAPI/Swagger schema to JSON file."""

import json
import sys
from main import app

def export_openapi():
    """Export the OpenAPI schema to a JSON file."""
    try:
        # Get the OpenAPI schema
        openapi_schema = app.openapi()

        # Write to file
        output_file = "openapi.json"
        with open(output_file, "w") as f:
            json.dump(openapi_schema, f, indent=2)

        print(f"✓ OpenAPI schema exported to {output_file}")
        print(f"✓ Schema contains {len(openapi_schema.get('paths', {}))} endpoints")
        print(f"✓ OpenAPI version: {openapi_schema.get('openapi', 'N/A')}")

        return True
    except Exception as e:
        print(f"✗ Error exporting schema: {e}")
        return False

if __name__ == "__main__":
    success = export_openapi()
    sys.exit(0 if success else 1)
