from process import *
from queue_ import Queue
from stack import Stack
from utils import *
from priority_queue import *

class SRTF():
    counter = 0
    def __init__(self, process_stack):
        SRTF.counter += 1
        self.name = f"SRTF: {SRTF.counter}"
        self.process_stack = process_stack
        self.queue = PriorityQueue()
        self.waiting_processes = []
        self.time_step = 0
        self.details = {"state": [], "level": []}

    def step(self):
        if not (self.process_stack.isEmpty() and self.queue.isEmpty() and not self.waiting_processes):

            # Get arrived process
            arrived_processes = getArrivedProcesses(self.process_stack, self.time_step)
            for process in arrived_processes:
                self.queue.push(process)
            
            process = self.queue.pop()
            if process:
                self.details["state"].append(process.name)
                self.details["level"].append(0)
                process.decrementDuration()
                if process.duration:
                    self.queue.push(process)
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
    stack.push(Process(0, 10))
    stack.push(Process(4, 8))
    stack.push(Process(8, 7))
    stack.push(Process(12, 1))
    stack.sort()
    arrival_times = getProcessData(stack)
    srtf = SRTF(stack)  
    df = srtf.run()
    plotGanttChart(df)