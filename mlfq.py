from multi_level_priority_queue import MultiLevelPriorityQueue
from process import *
from queue_ import Queue
from stack import Stack
from utils import *

class MLFQ:
    """
    The MLFQ (Multi-Level Feedback Queue) class implements a scheduler using multiple levels of queues 
    with different priorities. It is designed to manage processes with varying resource requirements 
    and execution characteristics.

    Attributes:
        process_stack (Stack): A stack of all initialized processes.
        structure (list): A list of each level structure
        num_levels (int): Number of priority levels in the MLFQ.
        quanta (list): A list of quanta of each level
        boost_time (int): Time interval for boosting process priority.
        time_step (int): Current time step in the scheduler.
        prev_level (int): Previous level from which a process was running.
        info (dict): Information about the current and finished processes, and other relevant data.
    """
    def __init__(self, process_stack: Stack, structure: list = [Queue(), Queue(), Queue()],
                 quanta: list = [2, 5, 100000], boost_time: int = 10000) -> None:
        """
        Initializes the MLFQ with the specified configuration.

        Args:
            process_stack (Stack): A stack of all initialized processes.
            structure (list): A list of each level structure
            quanta (list): A list of quanta of each level
            boost_time (int): Time interval for boosting process priority.
        """
        self.process_stack = process_stack
        self.structure = structure
        self.num_levels = len(structure)
        self.quanta = quanta
        self.boost_time = boost_time
        self.time_step = 0
        self.prev_level = 0
        self.info = {'CurrentRunningProcess': '', 'CurrentLevel': '', 'finished': [], 'finish_time': []}
    
    def boost(self) -> None:
        """
        Boosts the priority of processes in the queue. This method is typically invoked periodically 
        to prevent starvation of lower priority processes.

        The method moves processes from lower priority levels to higher ones based on the boost interval.
        """
        for i in range(1, self.num_levels):
            while self.structure[i].peak() != None:
                process = self.structure[i].pop()
                process.quantum = self.quanta[0]
                self.structure[0].push(process)

    def getProcess(self) -> (Process, int):
        """
        Retrieves the next process to be run based on priority levels.

        Returns:
            tuple: A tuple containing the process and its current level, or (None, None) if no process is available.
        """
        for i in range(self.num_levels):
            process = self.structure[i].peak()
            if process != None:
                return process, i
        return None, None
        
    def step(self) -> bool:
        """
        Executes a single time step in the MLFQ simulation. 
        This involves processing arrivals, handling I/O, and scheduling processes.

        Returns:
            bool: True if the simulation should continue, False otherwise.
        """
        self.arrived_processes = getArrivedProcesses(self.process_stack, self.time_step)
        self.stopped = []
        for process in self.arrived_processes:
            process.quantum = self.quanta[0]
            self.structure[0].push(process)

        if self.time_step % self.boost_time == 0:
            self.boost()

        condition = True
        while condition:
            process, level = self.getProcess()

            if process:
                if checkIO(process):
                    process.state = ProcessState.STOPPED
                    self.stopped.append((process, level))
                else:
                    condition = False
                    self.info["CurrentRunningProcess"] = process.name
                    process.state = ProcessState.RUNNING
                    process.duration -= 1
                    process.quantum -= 1
                    self.info["CurrentLevel"] = level
                    self.prev_level = level
                    if process.duration:
                        if process.quantum:
                            self.structure[level].changePeakProcess(process)
                        else:
                            if level != self.num_levels - 1:
                                self.structure[level].pop()
                                level += 1
                                process.quantum = self.quanta[level]
                                self.structure[level].push(process)
                            else:
                                self.structure[level].push(process)
                    else:
                        self.info['finished'].append(process.name)
                        self.info['finish_time'].append(self.time_step)
                        self.structure[level].pop()
                    for process, level in self.stopped:
                        self.structure[level].push(process)
            elif not self.process_stack.isEmpty():
                if len(self.stopped):
                    condition = False
                    self.info["CurrentRunningProcess"] = "I/O"
                    self.info["CurrentLevel"] = self.prev_level
                    for process, level in self.stopped:
                        self.structure[level].push(process)
                else:
                    condition = False
                    self.info["CurrentRunningProcess"] = "idle"
                    self.info["CurrentLevel"] = self.prev_level
            else:
                return False
        self.time_step += 1
        return True   
    
# Debug    
if __name__ == "__main__":
    stack = Stack()
    stack.push(Process(3, 8, 0))
    stack.push(Process(4, 7, 0))
    stack.push(Process(8, 7, 0))
    stack.push(Process(12, 1, 0))
    stack.sort()
    mlfq = MLFQ(stack, boost_time=1e3, quanta=[2, 4, 1e3])
    df = {"state":[], "level":[]}
    while(mlfq.step()):
        df["state"].append(mlfq.info["CurrentRunningProcess"])
        df["level"].append(mlfq.info["CurrentLevel"])
    plotGanttChart(df)