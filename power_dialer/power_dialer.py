import random
import logging
from typing import Dict
from power_dialer.database import EventQueue, Agent, StatusEnum, EventTypeEnum

DIAL_RATIO = 2


class PowerDialer:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        Agent.get_or_create(agent_id=agent_id)
        Agent.update(status=StatusEnum.LOGOUT).where(
            Agent.agent_id == self.agent_id
        ).execute()

    @property
    def status(self):
        agent, _ = Agent.get_or_create(agent_id=self.agent_id)
        return agent.status

    def on_agent_login(self):
        logging.info(f"[{self.agent_id}] login")
        Agent.update(status=StatusEnum.LOGIN).where(
            Agent.agent_id == self.agent_id
        ).execute()

        for _ in range(DIAL_RATIO):
            dial(self.agent_id, get_lead_phone_number_to_dial())

    def on_agent_logout(self):
        Agent.update(status="logout").where(Agent.agent_id == self.agent_id).execute()

    def on_call_started(self, lead_phone_number: str):
        logging.info(
            f"call started: agent_id [{self.agent_id}], lead_phone_number [{lead_phone_number}]"
        )
        if self.status == StatusEnum.LOGIN:
            Agent.update(status=StatusEnum.IN_CALL).where(
                Agent.agent_id == self.agent_id
            ).execute()

            connect(self.agent_id, lead_phone_number)
        else:  # redirect call either the agent is in call or logged out
            # Intention Locks for mysql
            # agent = Agent.select().where(Agent.status == StatusEnum.LOGIN).for_update().first()
            agent = Agent.select().where(Agent.status == StatusEnum.LOGIN).first()
            if agent:
                Agent.update(status=StatusEnum.IN_CALL).where(
                    Agent.agent_id == agent.agent_id
                ).execute()
                connect(agent.agent_id, lead_phone_number)

    def on_call_failed(self, lead_phone_number: str):
        logging.info(
            f"call failed: agent_id [{self.agent_id}], lead_phone_number [{lead_phone_number}]"
        )
        dial(self.agent_id, get_lead_phone_number_to_dial())

    def on_call_ended(self, lead_phone_number: str):
        logging.info(
            f"call ended: agent_id [{self.agent_id}], lead_phone_number [{lead_phone_number}]"
        )
        dial(self.agent_id, get_lead_phone_number_to_dial())
        Agent.update(status="login").where(Agent.agent_id == self.agent_id).execute()


# mock functions for testing


def dial(agent_id: str, lead_phone_number: str):
    logging.info(f"agent [{agent_id}] 呼叫 [{lead_phone_number}]")


def connect(agent_id: str, lead_phone_number: str):
    # new service to allow transfer to different agents
    logging.info(f"connect [{agent_id}] and [{lead_phone_number}]")


def get_lead_phone_number_to_dial() -> str:
    return str(random.randint(10000000, 99999999))


def monitor():
    """
    subscribe to EventQueue，mock callback functions。
    :return:
    """
    dialer_dict: Dict[str, PowerDialer] = {
        agent.agent_id: PowerDialer(agent.agent_id) for agent in Agent.select()
    }
    while 1:
        eq: EventQueue = EventQueue.select().order_by(EventQueue.id).first()
        if eq:
            if eq.type == EventTypeEnum.LOGIN.value:
                pd = PowerDialer(agent_id=eq.agent_id)
                dialer_dict[pd.agent_id] = pd
                pd.on_agent_login()
            elif eq.type == EventTypeEnum.LOGOUT.value:
                pd = dialer_dict[eq.agent_id]
                if pd:
                    pd.on_agent_logout()
            elif eq.type == EventTypeEnum.START.value:
                pd = dialer_dict[eq.agent_id]
                if pd:
                    number = str(random.randint(10000000, 99999999))
                    pd.on_call_started(number)
            elif eq.type == EventTypeEnum.FAIL.value:
                pd = dialer_dict[eq.agent_id]
                if pd:
                    number = str(random.randint(10000000, 99999999))
                    pd.on_call_failed(number)
            elif eq.type == EventTypeEnum.END.value:
                candidate_agent_list = list(
                    Agent.select().where(Agent.status == StatusEnum.IN_CALL)
                )
                if candidate_agent_list:
                    agent = random.choice(candidate_agent_list)
                    pd = dialer_dict[agent.agent_id]
                    number = str(random.randint(10000000, 99999999))
                    pd.on_call_ended(number)

            eq.delete_instance()


if __name__ == "__main__":
    monitor()
