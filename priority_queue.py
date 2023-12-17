import heapq
from process import Process

class PriorityQueue:
    """
    Implementation of a priority queue

    Attributes:
        heap (list): The heap of the priority queue
        time_step (int): The time step of the priority queue
    """
    def __init__(self, time_step:int):
        self.heap = []
        self.time_step = time_step

    def push(self, process:Process):
        """
        Pushes a process into the priority queue

        Returns:
            None
        """
        heapq.heappush(self.heap, (process.duration, process))

    def pop(self):
        """
        Pops a process from the priority queue

        Returns:
            Process: Highest priority process in the priority queue
        """
        return heapq.heappop(self.heap)[1] if self.heap else None

    def peak(self):
        """
        Checks the highest priority process
        
        Returns:
            Process: Highest priority process in the priority queue
        """
        return self.heap[0][1] if self.heap else None