from process import *
from queue_ import Queue
from stack import Stack
from utils import *
from priority_queue import *

from random import randint

class Lottery:
    def __init__(self, process_stack, quantum, pre_emptive):
        self.process_stack = process_stack
        self.queue = Queue()
        self.quantum = quantum
        self.pre_emptive = pre_emptive
        self.waiting_processes = []
        self.time_step = 0
        self.details = {"state": [], "level": []}
        self.pick_next = None
        # print(self.pre_emptive)

    def step(self):
        if not (self.process_stack.isEmpty() and self.queue.isEmpty() and not self.waiting_processes):

            # Get arrived process
            arrived_processes = getArrivedProcesses(self.process_stack, self.time_step)
            for process in arrived_processes:
                process.quantum = self.quantum
                self.queue.push(process)

            for process in self.waiting_processes:
                process.quantum = self.quantum
                self.queue.push(process)
            self.waiting_processes = []
            
            
            current_max_tickets = sum(process.tickets for process in self.queue.items)
            
            if current_max_tickets > 0:
                # determine winning ticket
                random_ticket = randint(0, current_max_tickets - 1)
                chosen_process = None
                ticket_sum = 0
                for process in self.queue.items:
                    ticket_sum += process.tickets
                    if ticket_sum > random_ticket:
                        chosen_process = process
                        break

                if self.pre_emptive:
                    # Preemptive behavior
                    # print('pre')
                    if chosen_process:
                        chosen_process = self.pick_next if self.pick_next != None else chosen_process 
                        chosen_process.decrementDuration()
                        self.details["state"].append(chosen_process.name)
                        self.details["level"].append(0)
                        if chosen_process.duration:
                            if chosen_process.quantum:
                                self.pick_next = chosen_process
                                # self.queue.changePeakProcess(chosen_process)
                                pass
                            else:
                                self.pick_next = None
                                self.queue.remove(chosen_process)
                                self.waiting_processes.append(chosen_process)
                        else:
                            self.pick_next = None
                            self.queue.remove(chosen_process)
                    else:
                        self.details["state"].append("idle")
                        self.details["level"].append(0)

                else:
                    # Non-preemptive behavior
                    # print('non-pre')
                    if chosen_process:
                        current_process = chosen_process
                        if current_process:
                            current_process = self.pick_next if self.pick_next != None else chosen_process 
                            current_process.decrementDuration()
                            self.details["state"].append(current_process.name)
                            self.details["level"].append(0)
                            if current_process.duration:
                                self.pick_next = current_process
                                # self.queue.changePeakProcess(current_process)
                                # process.quantum = 2 # workaround for crashing, non-preemptive behavior ignores quantum value
                                pass
                            else:
                                self.pick_next = None
                                self.queue.remove(current_process)
                        else:
                            self.details["state"].append("idle")
                            self.details["level"].append(0)
                    else:
                        self.details["state"].append("idle")
                        self.details["level"].append(0)

            else:
                self.details["state"].append("idle")
                self.details["level"].append(0)
            
            self.time_step += 1
            return True
        
        return False

    def run(self):
        while self.step():
            continue
        return self.details