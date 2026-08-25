"""initial_schema

Revision ID: 8a01c39e1ded
Revises: 
Create Date: 2026-08-25 14:48:46.406657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8a01c39e1ded'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Tables
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('role', postgresql.ENUM('OPERATOR', 'VERIFIER', 'ADMIN', 'SYSTEM_ADMIN', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table('documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('storage_key', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('checksum', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM('UPLOADED', 'PROCESSING', 'PROCESSED', 'REVIEW_REQUIRED', 'VERIFIED', 'REJECTED', 'FAILED', name='documentstatus'), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('storage_key')
    )

    op.create_table('processing_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', name='jobstatus'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('land_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('record_identifier', sa.String(), nullable=True),
        sa.Column('owner_name', sa.String(), nullable=True),
        sa.Column('khasra_number', sa.String(), nullable=True),
        sa.Column('khata_number', sa.String(), nullable=True),
        sa.Column('village', sa.String(), nullable=True),
        sa.Column('district', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('land_area', sa.String(), nullable=True),
        sa.Column('land_classification', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING_VERIFICATION', 'VERIFIED', 'REJECTED', 'CONFLICT', name='recordstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_land_records_owner_name'), 'land_records', ['owner_name'], unique=False)
    op.create_index(op.f('ix_land_records_khasra_number'), 'land_records', ['khasra_number'], unique=False)
    op.create_index(op.f('ix_land_records_khata_number'), 'land_records', ['khata_number'], unique=False)
    op.create_index(op.f('ix_land_records_village'), 'land_records', ['village'], unique=False)
    op.create_index(op.f('ix_land_records_status'), 'land_records', ['status'], unique=False)
    op.create_index(op.f('ix_land_records_record_identifier'), 'land_records', ['record_identifier'], unique=False)

    op.create_table('extracted_fields',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('land_record_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_name', sa.String(), nullable=False),
        sa.Column('extracted_value', sa.String(), nullable=True),
        sa.Column('normalized_value', sa.String(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('source_reference', sa.String(), nullable=True),
        sa.Column('bounding_box', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('extraction_method', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['land_record_id'], ['land_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('validation_findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('land_record_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_name', sa.String(), nullable=True),
        sa.Column('finding_type', sa.String(), nullable=False),
        sa.Column('severity', postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='findingseverity'), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('expected_value', sa.String(), nullable=True),
        sa.Column('actual_value', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM('OPEN', 'RESOLVED', 'DISMISSED', name='findingstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['land_record_id'], ['land_records.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('field_corrections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('land_record_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('extracted_field_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('old_value', sa.String(), nullable=True),
        sa.Column('new_value', sa.String(), nullable=True),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('corrected_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['corrected_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['extracted_field_id'], ['extracted_fields.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['land_record_id'], ['land_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('audit_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('actor_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('old_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('request_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('audit_events')
    op.drop_table('field_corrections')
    op.drop_table('validation_findings')
    op.drop_table('extracted_fields')
    
    op.drop_index(op.f('ix_land_records_record_identifier'), table_name='land_records')
    op.drop_index(op.f('ix_land_records_status'), table_name='land_records')
    op.drop_index(op.f('ix_land_records_village'), table_name='land_records')
    op.drop_index(op.f('ix_land_records_khata_number'), table_name='land_records')
    op.drop_index(op.f('ix_land_records_khasra_number'), table_name='land_records')
    op.drop_index(op.f('ix_land_records_owner_name'), table_name='land_records')
    op.drop_table('land_records')
    
    op.drop_table('processing_jobs')
    op.drop_table('documents')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')

    op.execute("DROP TYPE findingseverity")
    op.execute("DROP TYPE findingstatus")
    op.execute("DROP TYPE recordstatus")
    op.execute("DROP TYPE jobstatus")
    op.execute("DROP TYPE documentstatus")
    op.execute("DROP TYPE userrole")
