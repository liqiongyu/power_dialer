"""
simulator used for testing
"""
import random
import time
from power_dialer.database import EventQueue, EventTypeEnum


class Simulator:
    """
    simulator to generate different callback events
    """

    agent_id_list = [str(i) for i in range(10)]

    def simulate_login(self):
        for agent_id in self.agent_id_list:
            eq = EventQueue(type=1, agent_id=agent_id)
            eq.save()

    def simulate_logout(self):
        for agent_id in self.agent_id_list:
            eq = EventQueue(type=2, agent_id=agent_id)
            eq.save()

    def simulate_call_started(self):
        agent_id = random.choice(self.agent_id_list)
        eq = EventQueue(type=3, agent_id=agent_id)
        eq.save()

    def simulate_call_failed(self):
        agent_id = random.choice(self.agent_id_list)
        eq = EventQueue(type=4, agent_id=agent_id)
        eq.save()

    def simulate_call_ended(self):
        eq = EventQueue(type=5)
        eq.save()


if __name__ == "__main__":
    s = Simulator()
    s.simulate_login()
    time.sleep(2)
    while 1:
        try:
            event = random.choice(
                [EventTypeEnum.START, EventTypeEnum.FAIL, EventTypeEnum.END]
            )
            if event == EventTypeEnum.START:
                s.simulate_call_started()
            elif event == EventTypeEnum.FAIL:
                s.simulate_call_failed()
            elif event == EventTypeEnum.END:
                s.simulate_call_ended()

            time.sleep(1)
        except KeyboardInterrupt:
            s.simulate_logout()
