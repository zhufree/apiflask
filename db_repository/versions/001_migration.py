from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
student = Table('student', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('stuname', VARCHAR(length=64)),
    Column('stupwd', VARCHAR(length=64)),
)

student = Table('student', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('stuid', String(length=64)),
    Column('stupwd', String(length=64)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['student'].columns['stuname'].drop()
    post_meta.tables['student'].columns['stuid'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['student'].columns['stuname'].create()
    post_meta.tables['student'].columns['stuid'].drop()
