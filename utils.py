from process import Process
from stack import Stack
import random

def initializeProcessStack(num_processes: int = 50, max_arrival_time: int = 50, min_duration:int = 10, max_duration: int = 50, min_probability_io: float = 0.0, max_probability_io: float = 0.25):
    """
    Initializes a stack of processes with random attributes.

    This function creates a stack of processes with random arrival times, durations, and probabilities of IO.
    The generated processes are sorted based on their arrival times.

    Arguments:
        num_processes (int): The number of processes to generate (default is 50).
        max_arrival_time (int): The maximum arrival time for generated processes (default is 50).
        min_duration (int): The minimum duration for generated processes (default is 10).
        max_duration (int): The maximum duration for generated processes (default is 50).
        min_probability_io (float): The minimum probability of IO for generated processes (default is 0.0).
        max_probability_io (float): The maximum probability of IO for generated processes (default is 0.25).

    Returns:
        Stack: A stack of Process objects representing the generated processes, sorted by arrival time.
    """
    stack = Stack()
    for _ in range(num_processes):
        rand_arrival_time = random.randint(0, max_arrival_time + 1)
        rand_duration = random.randint(min_duration, max_duration + 1)
        rand_probability_io = random.uniform(min_probability_io, max_probability_io)
        stack.push(Process(rand_arrival_time, rand_duration, rand_probability_io))
    stack.sort()
    return stack

# Debug
if __name__ == "__main__":
    stack = initializeProcessStack()
    print("Process Name\tProcess Arival Time\tProcess Duration\tProcess Probability I/O")
    for i in range(50):
        process = stack.pop()
        print(f"{process.name}\t\t{process.arrival_time}\t\t\t{process.duration}\t\t\t{process.probability_io}")