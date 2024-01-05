from queue_ import Queue
from utils import *
from stack import Stack
from process import Process

class FCFS:
    def __init__(self, process_stack):
        self.process_stack = process_stack
        self.queue = Queue()
        self.details = {"state": [], "level":[]}
        self.time_step = 0
    
    def step(self):   
        if not ( self.process_stack.isEmpty() and self.queue.isEmpty() ):
        
            # Get arrived process
            arrived_processes = getArrivedProcesses(self.process_stack, self.time_step)
            for process in arrived_processes:
                self.queue.push(process)
            
            process = self.queue.peak()
            if process:
                self.details["state"].append(process.name)
                self.details["level"].append(0)
                process.duration -= 1
                if process.duration:
                    self.queue.changePeakProcess(process)
                else:
                    self.queue.pop()
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

if __name__ == "__main__":
    process_stack = Stack()
    process_stack.push(Process(0, 5))
    process_stack.push(Process(3, 10))
    process_stack.push(Process(4, 9))
    process_stack.push(Process(7, 2))
    process_stack.push(Process(8, 3))
    process_stack.sort()
    fcfs = FCFS(process_stack=process_stack)
    details = fcfs.run()
    plotGanttChart(details)