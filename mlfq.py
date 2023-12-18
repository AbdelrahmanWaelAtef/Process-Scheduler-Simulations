from multi_level_priority_queue import MultiLevelPriorityQueue
from process import *
from stack import Stack
from utils import *

class MLFQ:
    """
    The MLFQ (Multi-Level Feedback Queue) class implements a scheduler using multiple levels of queues 
    with different priorities. It is designed to manage processes with varying resource requirements 
    and execution characteristics.

    Attributes:
        process_stack (Stack): A stack of all initialized processes.
        num_levels (int): Number of priority levels in the MLFQ.
        multi_level_priority_queue (MultiLevelPriorityQueue): The priority queues for each level.
        boost_time (int): Time interval for boosting process priority.
        time_step (int): Current time step in the scheduler.
        prev_level (int): Previous level from which a process was running.
        info (dict): Information about the current and finished processes, and other relevant data.
    """
    
    def __init__(self, num_processes: int = 50, max_arrival_time: int = 50, min_duration:int = 10, max_duration: int = 50,
                min_probability_io: float = 0.0,max_probability_io: float = 0.25, num_levels: int = 3, quanta: list = [2, 3, 4],
                boost_time: int = 150):
        """
        Initializes the MLFQ with the specified configuration.

        Args:
            num_processes (int): The number of processes to handle.
            max_arrival_time (int): Maximum arrival time of processes.
            min_duration (int): Minimum duration of processes.
            max_duration (int): Maximum duration of processes.
            min_probability_io (float): Minimum probability of a process requiring I/O.
            max_probability_io (float): Maximum probability of a process requiring I/O.
            num_levels (int): Number of priority levels in the queue.
            quanta (list[int]): Time quantum for each priority level.
            boost_time (int): Interval for boosting process priority.
        """
        self.process_stack = initializeProcessStack(num_processes, max_arrival_time, min_duration,
                                                     max_duration, min_probability_io, max_probability_io)
        self.num_levels = num_levels
        self.multi_level_priority_queue = MultiLevelPriorityQueue(num_levels, quanta)
        self.boost_time = boost_time
        self.time_step = 0
        self.prev_level = 0
        self.info = {'CurrentRunningProcess': '', 'CurrentLevel': '', 'finished': [], 'finish_time': []}
    
    def boost(self):
        """
        Boosts the priority of processes in the queue. This method is typically invoked periodically 
        to prevent starvation of lower priority processes.

        The method moves processes from lower priority levels to higher ones based on the boost interval.
        """
        for i in range(1, self.num_levels):
            while self.multi_level_priority_queue.peak(i) != None:
                process = self.multi_level_priority_queue.pop(i)
                self.multi_level_priority_queue.push(0, process)

    def getProcess(self):
        """
        Retrieves the next process to be run based on priority levels.

        Returns:
            tuple: A tuple containing the process and its current level, or (None, None) if no process is available.
        """
        for i in range(self.num_levels):
            process = self.multi_level_priority_queue.pop(i)
            if process != None:
                return process, i
        return None, None
        
    def step(self):
        """
        Executes a single time step in the MLFQ simulation. 
        This involves processing arrivals, handling I/O, and scheduling processes.

        Returns:
            bool: True if the simulation should continue, False otherwise.
        """
        self.arrived_processes = getArrivedProcesses(self.process_stack, self.time_step)
        self.stopped = []
        for process in self.arrived_processes:
            process.quantum = self.multi_level_priority_queue.queues[0].quantum
            self.multi_level_priority_queue.push(0, process)

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
                            self.multi_level_priority_queue.push(level, process)
                        else:
                            if level != self.num_levels - 1:
                                level += 1
                                process.quantum = self.multi_level_priority_queue.queues[level].quantum
                                self.multi_level_priority_queue.push(level, process)
                            else:
                                self.multi_level_priority_queue.push(level, process)
                    else:
                        self.info['finished'].append(process.name)
                        self.info['finish_time'].append(self.time_step)
                    for process, level in self.stopped:
                        self.multi_level_priority_queue.push(level, process)
            elif not self.process_stack.isEmpty():
                if len(self.stopped):
                    condition = False
                    self.info["CurrentRunningProcess"] = "I/O"
                    self.info["CurrentLevel"] = self.prev_level
                    for process, level in self.stopped:
                        self.multi_level_priority_queue.push(level, process)
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
    mlfq = MLFQ(20, 25)
    with open("logs.txt", "w") as file:
        file.write("Process Name\tProcess Arival Time\tProcess Duration\tProcess Probability I/O\n")
        for i in range(len(mlfq.process_stack.items)):
            process = mlfq.process_stack.items[i]
            file.write(f"{process.name}\t\t\t\t{process.arrival_time}\t\t\t\t\t{process.duration}\t\t\t\t\t{process.probability_io}\n")
        file.write("Time step\tCurrently running\tCurrent level\tFinished processes\tFinish times\n")
        while(mlfq.step()):
            file.write(f'{mlfq.time_step}\t\t\t{mlfq.info["CurrentRunningProcess"]}\t\t\t\t\t{mlfq.info["CurrentLevel"]}\t\t\t\t{mlfq.info["finished"]}\t\t\t\t\t{mlfq.info["finish_time"]}\n')