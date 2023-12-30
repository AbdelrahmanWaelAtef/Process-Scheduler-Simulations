from process import *
from queue_ import Queue
from stack import Stack
from utils import *
from priority_queue import *


class RoundRobin():
    #
    def __init__(self, process_stack, time_slice):
        self.process_stack = process_stack
        self.queue = Queue()
        self.time_slice = time_slice
        self.waiting_processes = []

    def run(self):
        self.time_step = 0
        details = {"state": [], "level": []}
        while not (self.process_stack.isEmpty() and self.queue.isEmpty()):

            # Get arrived process
            arrived_processes = getArrivedProcesses(self.process_stack, self.time_step)
            for process in arrived_processes:
                self.waiting_processes.append(process)

            if self.time_step == 0:
                for process in self.waiting_processes:
                    self.queue.enqueue(process)
                self.waiting_processes = []

            current_process = self.queue.dequeue()
            if current_process:
                details["state"].append(current_process.name)
                details["level"].append(0)
                if current_process.remaining_time > self.time_slice:
                    current_process.remaining_time -= self.time_slice
                    for process in self.waiting_processes:
                        self.queue.enqueue(process)
                    self.queue.enqueue(current_process)
                    self.waiting_processes = []
                else:
                    details["state"].append(current_process.name)
                    details["level"].append(0)
                    current_process.remaining_time = 0
            else:
                details["state"].append("idle")
                details["level"].append(0)
                for process in self.waiting_processes:
                    self.queue.enqueue(process)
                self.waiting_processes = []
            self.time_step += 1
        return details


if __name__ == "__main__":
    # Generating random processes
    stack = Stack()
    random.seed(42)  # Seed for reproducibility, change or remove for different random processes
    for _ in range(4):
        arrival_time = random.randint(0, 15)
        burst_time = random.randint(1, 15)
        stack.push(Process(arrival_time, burst_time))

    stack.sort()
    arrival_times = getProcessData(stack)
    rr = RoundRobin(stack, 3)  # Time slice set to 3 for example
    df = rr.run()
    plotGanttChart(df)
