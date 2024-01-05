from process import *
from queue_ import Queue
from stack import Stack
from utils import *
from priority_queue import *

class RoundRobin():
    counter = 0
    def __init__(self, process_stack, quantum):
        RoundRobin.counter += 1
        self.name = f"RoundRobin: {RoundRobin.counter}"
        self.process_stack = process_stack
        self.queue = Queue()
        self.quantum = quantum
        self.waiting_processes = []
        self.time_step = 0
        self.details = {"state": [], "level": []}
    
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

            current_process = self.queue.peak()
            if current_process:
                current_process.decrementDuration()
                self.details["state"].append(current_process.name)
                self.details["level"].append(0)
                if current_process.duration:
                    if current_process.quantum:
                        self.queue.changePeakProcess(current_process)
                    else:
                        self.queue.pop()
                        self.waiting_processes.append(current_process)
                else:
                    self.queue.pop()
            else:
                self.details["state"].append("idle")
                self.details["level"].append(0)
            self.time_step += 1
            return True
        return False

    def run(self):
        while(self.step()):
            continue
        return self.details

if __name__ == "__main__":
    stack = Stack()
    stack.push(Process(0, 3))
    stack.push(Process(2, 5))
    stack.push(Process(4, 3))
    stack.push(Process(6, 6))
    stack.sort()
    arrival_times = getProcessData(stack)
    rr = RoundRobin(stack, 1)
    df = rr.run()
    plotGanttChart(df)
