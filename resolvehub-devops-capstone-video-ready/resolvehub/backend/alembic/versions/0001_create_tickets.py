"""Create support tickets table."""
from alembic import op
import sqlalchemy as sa
revision = "0001_create_tickets"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("requester", sa.String(length=120), nullable=False, server_default="Unknown"),
        sa.Column("category", sa.String(length=60), nullable=False, server_default="General"),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="Medium"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="Open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_tickets_id", "tickets", ["id"])
    op.create_index("ix_tickets_title", "tickets", ["title"])
    op.create_index("ix_tickets_priority", "tickets", ["priority"])
    op.create_index("ix_tickets_status", "tickets", ["status"])

def downgrade():
    op.drop_index("ix_tickets_status", table_name="tickets")
    op.drop_index("ix_tickets_priority", table_name="tickets")
    op.drop_index("ix_tickets_title", table_name="tickets")
    op.drop_index("ix_tickets_id", table_name="tickets")
    op.drop_table("tickets")
