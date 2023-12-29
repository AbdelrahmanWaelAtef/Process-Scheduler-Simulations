from process import *
from queue_ import Queue
from stack import Stack
from utils import *
from priority_queue import *

class STRF():
    def __init__(self, process_stack):
        self.process_stack = process_stack
        self.queue = PriorityQueue()
        self.waiting_processes = []

    def run(self):
        self.time_step = 0
        details = {"state": [], "level": []}
        while not (self.process_stack.isEmpty() and self.queue.isEmpty()):

            # Get arrived process
            arrived_processes = getArrivedProcesses(self.process_stack, self.time_step)
            for process in arrived_processes:
                self.queue.push(process)
            
            process = self.queue.pop()
            if process:
                details["state"].append(process.name)
                details["level"].append(0)
                process.decrementDuration()
                if process.duration:
                    self.queue.push(process)
            else:
                details["state"].append("idle")
                details["level"].append(0)
            self.time_step += 1
        return details

if __name__ == "__main__":
    stack = Stack()
    stack.push(Process(0, 10))
    stack.push(Process(4, 8))
    stack.push(Process(8, 7))
    stack.push(Process(12, 1))
    stack.sort()
    arrival_times = getProcessData(stack)
    strf = STRF(stack)  
    df = strf.run()
    plotGanttChart(df)