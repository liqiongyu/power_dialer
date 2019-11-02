from peewee import CharField, SqliteDatabase, IntegerField
from playhouse.signals import Model
from enum import IntEnum

StatusEnum = IntEnum("StatusEnum", "LOGIN,IN_CALL,LOGOUT")
EventTypeEnum = IntEnum("EventTypeEnum", "LOGIN,LOGOUT,START,FAIL,END")


db = SqliteDatabase("dialer.db")


class Agent(Model):
    """
    table for agent status
    """

    agent_id = CharField(primary_key=True)
    status = IntegerField(
        choices=(
            (StatusEnum.LOGIN, "login"),
            (StatusEnum.IN_CALL, "in_call"),
            (StatusEnum.LOGOUT, "logout"),
        ),
        default=StatusEnum.LOGOUT,
    )

    class Meta:
        database = db
        db_table = "agent"


class EventQueue(Model):
    """
    table for simulating callback functions in testing
    """

    type = IntegerField(
        choices=(
            (EventTypeEnum.LOGIN, "login"),
            (EventTypeEnum.LOGOUT, "logout"),
            (EventTypeEnum.START, "start"),
            (EventTypeEnum.FAIL, "failed"),
            (EventTypeEnum.END, "end"),
        )
    )
    agent_id = CharField(default="")

    class Meta:
        database = db
        db_table = "event_queue"


Agent.create_table()
EventQueue.create_table()
