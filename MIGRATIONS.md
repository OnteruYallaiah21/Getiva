# GETIVA Database Migrations Guide

This guide explains how to use Alembic for managing database schema changes in the GETIVA project.

## Overview

Alembic is a lightweight database migration tool that works with SQLAlchemy. It allows you to:
- Version control your database schema
- Track schema changes over time
- Upgrade and downgrade database schema
- Share schema changes across team members

## Setup

Alembic is already configured for the GETIVA project. The configuration files are:
- `alembic.ini` - Main Alembic configuration
- `alembic/env.py` - Environment script that connects to the database
- `alembic/script.py.mako` - Template for generating new migration files
- `alembic/versions/` - Directory containing all migration files

## Applying Migrations

### Initial Setup
Before running the application for the first time, apply all migrations to set up the database:

```bash
alembic upgrade head
```

This command:
- Reads all migration files in `alembic/versions/`
- Applies them in order
- Updates the `alembic_version` table to track applied migrations

### Applying Specific Migrations
To apply migrations up to a specific revision:

```bash
alembic upgrade <revision_id>
```

Example:
```bash
alembic upgrade 001
```

## Creating New Migrations

### Automatic Migration Generation
When you modify SQLAlchemy models, generate migrations automatically:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Example:
```bash
alembic revision --autogenerate -m "Add phone field to students"
```

**Important:** Review the generated migration file before applying it. Autogenerate may not catch all changes correctly.

### Manual Migration Creation
For more complex changes or when autogenerate doesn't work:

```bash
alembic revision -m "Description of changes"
```

This creates an empty migration file where you can manually write the upgrade/downgrade logic.

## Rollback Migrations

### Rollback One Migration
To undo the last applied migration:

```bash
alembic downgrade -1
```

### Rollback to Specific Version
To rollback to a specific revision:

```bash
alembic downgrade <revision_id>
```

Example:
```bash
alembic downgrade 001
```

### Full Rollback
To remove all migrations and revert to initial state:

```bash
alembic downgrade base
```

## Migration File Structure

Each migration file in `alembic/versions/` contains:

```python
# Metadata
revision = '002'  # Unique revision ID
down_revision = '001'  # Previous revision
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Apply this migration"""
    pass

def downgrade() -> None:
    """Undo this migration"""
    pass
```

### Example Migration: Adding a Column

```python
def upgrade() -> None:
    op.add_column('students', sa.Column('graduation_date', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('students', 'graduation_date')
```

### Example Migration: Creating a Table

```python
def upgrade() -> None:
    op.create_table(
        'new_table',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('new_table')
```

## Checking Migration Status

### View Current Database Version
```bash
alembic current
```

### View All Migrations
```bash
alembic history
```

### View Detailed History
```bash
alembic history --verbose
```

## Best Practices

### 1. One Change Per Migration
Create separate migrations for different types of changes:
- ✅ Good: Add column, Rename column, Create table
- ❌ Bad: Add column AND rename table in same migration

### 2. Write Both Upgrade and Downgrade
Always ensure the `downgrade()` function properly reverses changes:
- Drop columns added in upgrade
- Drop tables created in upgrade
- Restore original default values

### 3. Review Auto-Generated Migrations
The `--autogenerate` flag is helpful but not perfect:
- Review the generated file for accuracy
- Check for correct column types and constraints
- Verify downgrade logic

### 4. Test Migrations Locally
Before applying to production:
```bash
# Apply migration
alembic upgrade head

# Test application behavior
# ...

# Rollback to verify downgrade works
alembic downgrade -1

# Re-apply
alembic upgrade head
```

### 5. Descriptive Revision Messages
Use clear messages that describe the change:
- ✅ "Add phone field to students table"
- ❌ "Update database"
- ✅ "Create applications table with indexes"
- ❌ "Add tables"

### 6. Handle Enum Types Carefully
For PostgreSQL ENUM columns:

```python
# Create enum
myenum = postgresql.ENUM('value1', 'value2', name='myenum')
myenum.create(op.get_bind(), checkfirst=True)

# Add column with enum
op.add_column('table_name', sa.Column('status', myenum, nullable=False))

# Drop enum (in downgrade)
postgresql.ENUM(name='myenum').drop(op.get_bind(), checkfirst=True)
```

### 7. Handle UUID Columns
GETIVA uses PostgreSQL UUID columns:

```python
op.create_table(
    'new_table',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
)
```

## Workflow Example

### Scenario: Add email notification preference to recruiters

1. **Update the model** (`models.py`):
```python
class Recruiter(Base):
    # ... existing fields ...
    email_notifications = Column(Integer, default=1)
```

2. **Generate migration**:
```bash
alembic revision --autogenerate -m "Add email notifications preference to recruiters"
```

3. **Review generated file** in `alembic/versions/`:
```python
def upgrade() -> None:
    op.add_column('recruiters', sa.Column('email_notifications', sa.Integer(), nullable=False, server_default='1'))

def downgrade() -> None:
    op.drop_column('recruiters', 'email_notifications')
```

4. **Test locally**:
```bash
alembic upgrade head
# Test the new field works
alembic downgrade -1
alembic upgrade head
```

5. **Commit the migration**:
```bash
git add alembic/versions/002_*.py
git commit -m "Add email notifications preference to recruiters"
```

6. **Deploy**: Push to production, then:
```bash
alembic upgrade head
```

## Troubleshooting

### Migration Won't Apply
```
Error: can't drop column that is referenced by a foreign key
```

Solution: Create a migration that removes the foreign key first, then drops the column.

### Conflicting Revision IDs
```
Error: Multiple heads exist in this branch
```

Solution: Use `alembic branches` to see conflicts, resolve by editing down_revision in conflicting migrations.

### Autogenerate Detects Too Many Changes
If autogenerate creates a migration with unwanted changes:
1. Delete the migration file
2. Manually create a new migration with only desired changes
3. Use `alembic revision -m "description"` to start fresh

### Database Already Contains Changes
If the database has manual changes not captured in migrations:
1. Stamp the current version: `alembic stamp head`
2. Create new migration for remaining changes: `alembic revision --autogenerate`

## Integration with CI/CD

For automated deployments, add to your CI/CD pipeline:

```bash
# Before starting application
alembic upgrade head

# Run tests
pytest

# On deployment
# Migrations applied before app start ensures schema is ready
```

## Migration Naming Convention

GETIVA uses numeric revision IDs:
- `001_initial_schema.py` - Initial database setup
- `002_add_something.py` - Second migration
- `003_modify_something.py` - Third migration

This makes it easy to understand the order and history.

## Resources

- [Alembic Official Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM Documentation](https://docs.sqlalchemy.org/en/20/)
- [PostgreSQL with SQLAlchemy](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)

## Summary

Key commands for daily use:

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration (autogenerate)
alembic revision --autogenerate -m "Description"

# Rollback one migration
alembic downgrade -1

# Check current migration version
alembic current

# View migration history
alembic history
```

---

**GETIVA Database Migrations** | Alembic v1.13+
