from process import Process
from stack import Stack
import random

def initializeProcessStack(num_processes: int = 50, max_arrival_time: int = 50, min_duration:int = 10, max_duration: int = 50, min_probability_io: float = 0.0, max_probability_io: float = 0.25) -> Stack:
    """
    Initializes a stack of processes with random attributes.

    This function creates a stack of processes with random arrival times, durations, and probabilities of IO.
    The generated processes are sorted based on their arrival times.

    Arguments:
        num_processes (int): The number of processes to generate (default is 50).
        max_arrival_time (int): The maximum arrival time for generated processes (default is 50).
        min_duration (int): The minimum duration for generated processes (default is 10).
        max_duration (int): The maximum duration for generated processes (default is 50).
        min_probability_io (float): The minimum probability of I/O for generated processes (default is 0.0).
        max_probability_io (float): The maximum probability of I/O for generated processes (default is 0.25).

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

def getArrivedProcesses(stack: Stack, time_step:int) -> list:
    """
    Gets the processes the arrives at the given time step, and removes the processes from the stack.

    Arguments:
        stack (Stack): Stack of initialized processes.
        time_step (int): The current the time step.

    Returns:
        List(Process): A list of the processes that arrives at that time step.
    """
    processes = []
    while not stack.isEmpty() and stack.peak().arrival_time == time_step:
        processes.append(stack.pop())
    return processes

def checkIO(process:Process) -> bool:
    """
    Checks if the process will perform an I/O operation or not.

    Arguments:
        process (Process): Examined process.

    Returns:
        bool: True if the process will perform I/O, False if not.
    """
    io = False
    rand_num = random.uniform(0, 1)
    if rand_num <= process.probability_io:
        io = True
    return io

# Debug
if __name__ == "__main__":
    stack = initializeProcessStack()
    print("Process Name\tProcess Arival Time\tProcess Duration\tProcess Probability I/O\t\tHave preformed I/O")

    for i in range(50):
        processes = getArrivedProcesses(stack, i)
        for process in processes:
            print(f"{process.name}\t\t{process.arrival_time}\t\t\t{process.duration}\t\t\t{process.probability_io}\t\t\t\t{checkIO(process)}")