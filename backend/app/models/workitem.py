import sqlalchemy
from app.core.database import metadata
import enum

class StatusEnum(str, enum.Enum):
    OPEN         = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED     = "RESOLVED"
    CLOSED       = "CLOSED"

class PriorityEnum(str, enum.Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

workitems = sqlalchemy.Table(
    "workitems",
    metadata,
    sqlalchemy.Column("id",           sqlalchemy.String,  primary_key=True),
    sqlalchemy.Column("component_id", sqlalchemy.String,  nullable=False),
    sqlalchemy.Column("title",        sqlalchemy.String,  nullable=False),
    sqlalchemy.Column("status",       sqlalchemy.String,  default="OPEN"),
    sqlalchemy.Column("priority",     sqlalchemy.String,  default="P2"),
    sqlalchemy.Column("signal_count", sqlalchemy.Integer, default=1),
    sqlalchemy.Column("start_time",   sqlalchemy.DateTime),
    sqlalchemy.Column("end_time",     sqlalchemy.DateTime, nullable=True),
    sqlalchemy.Column("mttr_minutes", sqlalchemy.Float,   nullable=True),
    sqlalchemy.Column("created_at",   sqlalchemy.DateTime),
)

rca_records = sqlalchemy.Table(
    "rca_records",
    metadata,
    sqlalchemy.Column("id",               sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("workitem_id",      sqlalchemy.String, sqlalchemy.ForeignKey("workitems.id")),
    sqlalchemy.Column("root_cause",       sqlalchemy.String, nullable=False),
    sqlalchemy.Column("category",         sqlalchemy.String, nullable=False),
    sqlalchemy.Column("fix_applied",      sqlalchemy.Text,   nullable=False),
    sqlalchemy.Column("prevention_steps", sqlalchemy.Text,   nullable=False),
    sqlalchemy.Column("incident_start",   sqlalchemy.DateTime),
    sqlalchemy.Column("incident_end",     sqlalchemy.DateTime),
    sqlalchemy.Column("submitted_at",     sqlalchemy.DateTime),
)