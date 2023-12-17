from priority_queue import PriorityQueue
from process import Process

class MultiLevelPriorityQueue:
    """
    Implementation of a multi-level priority queue

    Attributes:
        queues (PriorityQueue): The list of all priorit queues that corresponds to each level
    """
    def __init__(self, levels: int):
        self.queues = [PriorityQueue() for _ in range(levels)]

    def push(self, level: int, process: Process):
        """
        Pushes a process into the priority queue of a given level

        Returns:
            None
        """
        if 0 <= level < len(self.queues):
            self.queues[level].push(process)

    def pop(self, level: int):
        """
        Pops a process from a priority queue in a given level

        Returns:
            Process: Highest priority process in the priority queue of a given level
        """
        if 0 <= level < len(self.queues):
            return self.queues[level].pop()

    def peak(self, level: int):
        """
        Checks the highest priority process from a priority queue in a given level

        Returns:
            Process: Highest priority process in the priority queue of a given level
        """
        if 0 <= level < len(self.queues):
            return self.queues[level].peak()