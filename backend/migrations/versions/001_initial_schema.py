"""Initial schema setup for GETIVA

Revision ID: 001
Revises:
Create Date: 2025-02-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def _create_enum_idempotent(op, name: str, values: tuple[str, ...]) -> None:
    """Create a PostgreSQL ENUM if missing. Safe after partial migrations or manual DDL."""
    labels = ", ".join("'" + v.replace("'", "''") + "'" for v in values)
    op.execute(
        text(
            f"""
            DO $$ BEGIN
                CREATE TYPE {name} AS ENUM ({labels});
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
            """
        )
    )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # ENUMs are global in PostgreSQL; create once without failing if they already exist.
    _create_enum_idempotent(op, "userrole", ("admin", "recruiter", "student"))
    _create_enum_idempotent(
        op,
        "applicationstatus",
        ("applied", "interview", "offer", "rejected", "withdrawn"),
    )
    _create_enum_idempotent(op, "paymentstatus", ("pending", "completed", "failed", "refunded"))

    # Tell SQLAlchemy not to emit CREATE TYPE again inside create_table (avoids duplicate_object).
    userRole = postgresql.ENUM(
        "admin", "recruiter", "student", name="userrole", create_type=False
    )
    applicationStatus = postgresql.ENUM(
        "applied",
        "interview",
        "offer",
        "rejected",
        "withdrawn",
        name="applicationstatus",
        create_type=False,
    )
    paymentStatus = postgresql.ENUM(
        "pending", "completed", "failed", "refunded", name="paymentstatus", create_type=False
    )

    # Skip tables that already exist (partial runs or missing alembic_version row).
    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("username", sa.String(255), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("password_hash", sa.String(255), nullable=False),
            sa.Column("role", userRole, nullable=False, server_default="student"),
            sa.Column("is_active", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
        op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    if "students" not in existing_tables:
        op.create_table(
            "students",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("full_name", sa.String(255), nullable=False),
            sa.Column("phone", sa.String(20), nullable=True),
            sa.Column("resume_url", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "recruiters" not in existing_tables:
        op.create_table(
            "recruiters",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("phone", sa.String(20), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "applications" not in existing_tables:
        op.create_table(
            "applications",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("recruiter_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("company_name", sa.String(255), nullable=False),
            sa.Column("job_title", sa.String(255), nullable=False),
            sa.Column("job_description", sa.Text(), nullable=True),
            sa.Column("job_url", sa.Text(), nullable=True),
            sa.Column("resume_url", sa.Text(), nullable=True),
            sa.Column("status", applicationStatus, nullable=False, server_default="applied"),
            sa.Column("applied_date", sa.DateTime(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
            sa.ForeignKeyConstraint(["recruiter_id"], ["recruiters.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "student_payments" not in existing_tables:
        op.create_table(
            "student_payments",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("payment_type", sa.String(50), nullable=False),
            sa.Column("status", paymentStatus, nullable=False, server_default="pending"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("payment_date", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "recruiter_payments" not in existing_tables:
        op.create_table(
            "recruiter_payments",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("recruiter_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("salary_month", sa.String(7), nullable=False),
            sa.Column("status", paymentStatus, nullable=False, server_default="pending"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("payment_date", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["recruiter_id"], ["recruiters.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    op.drop_table('recruiter_payments')
    op.drop_table('student_payments')
    op.drop_table('applications')
    op.drop_table('recruiters')
    op.drop_table('students')
    op.drop_table('users')

    postgresql.ENUM(name='paymentstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='applicationstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='userrole').drop(op.get_bind(), checkfirst=True)
