from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey, update
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TEXT, DATETIME, TINYINT
import settings

from datetime import datetime, timezone

global engine
global conn
global meta
global userdata
global mod_event
global mod_event_type
global name_change_type
global name_change_event
global past_streaks


def init():
    global engine
    global conn
    global meta
    global userdata
    global mod_event
    global mod_event_type
    global name_change_type
    global name_change_event
    global past_streaks
    engine = create_engine(settings.config["databaseUrl"], echo=True)
    conn = engine.connect()
    meta = MetaData()
    userdata = Table(
        'userdata', meta,
        Column('id', BIGINT, primary_key=True, nullable=False),
        Column('last_relapse', BIGINT),
        Column('lynch_count', INTEGER, nullable=False, default=0),
        Column('successful_lynch_count', INTEGER, nullable=False, default=0),
        Column('lynch_expiration_time', BIGINT, nullable=False, default=0),
        Column('mute', TINYINT, nullable=False, default=0),
        Column('double_mute', TINYINT, nullable=False, default=0),
        Column('cooldown', TINYINT, nullable=False, default=0),
        Column('member', TINYINT, nullable=0, default=0),
        Column('kicked', TINYINT, nullable=0, default=0),
        Column('banned', TINYINT, nullable=0, default=0),
        Column('noperms', TINYINT, nullable=0, default=0),
        Column('member_activation_date', BIGINT, nullable=False, default=0),
    )

    mod_event_type = Table(
        'mod_event_type', meta,
        Column("mod_type_id", INTEGER, primary_key=True, nullable=False, autoincrement=True),
        Column("mod_action_type", TEXT, nullable=False)
    )

    mod_event = Table(
        'mod_event', meta,
        Column('event_id', BIGINT, primary_key=True, nullable=False, autoincrement=True),
        Column('recipient_id', BIGINT, ForeignKey("userdata.id"), nullable=False),
        Column('event_type', INTEGER, ForeignKey("mod_event_type.mod_type_id"), nullable=False),
        Column('reason', TEXT),
        Column('event_time', DATETIME, nullable=False),
        Column('issuer_id', BIGINT, ForeignKey("userdata.id"), nullable=False),
        Column('historical', TINYINT, nullable=False, default=0)
    )

    name_change_type = Table(
        'name_change_type', meta,
        Column('change_type_id', INTEGER, primary_key=True, nullable=False, autoincrement=True),
        Column('change_type', TEXT, nullable=False)
    )

    name_change_event = Table(
        'name_change_event', meta,
        Column('name_change_event_id', BIGINT, primary_key=True, nullable=False, autoincrement=True),
        Column('user_id', BIGINT, ForeignKey("userdata.id"), nullable=False),
        Column('previous_name', TEXT, nullable=False),
        Column('change_type', INTEGER, ForeignKey('name_change_type.change_type_id'), nullable=False),
        Column('new_name', TEXT, nullable=False),
        Column('event_time', DATETIME, nullable=False)
    )

    past_streaks = Table(
        'past_streaks', meta,
        Column('event_id', BIGINT, primary_key=True, nullable=False, autoincrement=True),
        Column('user_id', BIGINT, ForeignKey("userdata.id"), nullable=False),
        Column('streak_length', BIGINT, nullable=False),
        Column('event_time', DATETIME, nullable=False)
    )

    meta.create_all(engine)

# Userdata

async def userdata_update_query(id, params: dict):
    user_data_query = update(userdata).where(userdata.c.id == id) \
        .values(params)
    conn.execute(user_data_query)

async def userdata_select_query(id, all: bool = True):
    query = userdata.select().where(userdata.c.id == id)
    if all:
        rows = conn.execute(query).fetchall()
    else:
        rows = conn.execute(query).fetchone()
    return rows

# Modevent

async def mod_event_insert(recipient_id, event_type, event_time, reason, issuer_id, historical):
    mod_query = mod_event.insert(). \
        values(recipient_id=recipient_id, event_type=event_type, reason=reason, event_time=event_time,
            issuer_id=issuer_id, historical=historical)
    conn.execute(mod_query)

# Past streaks

async def past_insert_query(user_id, streak_length):
    query = past_streaks.insert().values(
        user_id=user_id,
        streak_length=streak_length,
        event_time=datetime.utcnow()
    )
    conn.execute(query)

async def past_select_query(id):
    query = past_streaks.select().where(past_streaks.c.user_id == id)
    rows = conn.execute(query).fetchall()
    return rows

# Nickname change event

async def name_change_event_insert(user_id, previous_name, change_type, new_name):
    username_query = name_change_event.insert(). \
        values(user_id=user_id, previous_name=previous_name, change_type=change_type, new_name=new_name, event_time=datetime.utcnow())
    conn.execute(username_query)
