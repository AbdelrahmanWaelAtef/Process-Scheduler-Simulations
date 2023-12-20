import heapq
from process import Process

class PriorityQueue:
    """
    Implementation of a priority queue

    Attributes:
        heap (list): The heap of the priority queue
        quantum (int): The time step of the priority queue
    """
    def __init__(self, quantum:int) -> None:
        self.heap = []
        self.quantum = quantum

    def push(self, process:Process) -> None:
        """
        Pushes a process into the priority queue

        Returns:
            None
        """
        heapq.heappush(self.heap, (process.duration, process))

    def pop(self) -> Process:
        """
        Pops a process from the priority queue

        Returns:
            Process: Highest priority process in the priority queue
        """
        return heapq.heappop(self.heap)[1] if self.heap else None

    def peak(self) -> Process:
        """
        Checks the highest priority process
        
        Returns:
            Process: Highest priority process in the priority queue
        """
        return self.heap[0][1] if self.heap else None
    
    def isEmpty(self) -> bool:
        """
        Checks if the priority queue is empty or not

        Returns:
            bool: True if it is empty, False if not
        """
        return len(self.heap) == 0

# Debug
if __name__ == "__main__":
    process_1 = Process(1, 4, 0.2)
    process_2 = Process(1, 2, 0.2)
    process_3 = Process(1, 2, 0.2)

    myQueue = PriorityQueue(1)
    myQueue.push(process_1)
    myQueue.push(process_2)
    myQueue.push(process_3)

    print(myQueue.pop().name)