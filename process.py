from enum import Enum


class ProcessState(Enum):
    """
    Describes the state of the process in ENUM format
    """
    RUNNING = 1
    STOPPED = 2
    READY = 3
    EMBRYO = 4


class Process:
    """
    Representation of a class

    Attributes:
        pid (int): The PID of the process
        name (str): The name of the process
        arrival_time(int): When will the process arrive
        duration(int): How long the process should run
        state(int): The state of the process
        probability_io(float): The probability of the process to perform an I/O operation

    Static variable:
    pid_counter (int): Keeps track of how many processes there are and helps in giving names to each process
    """

    pid_counter = 0

    def __init__(self, arrival_time: int, duration: int, probability_io: float):
        Process.pid_counter += 1
        self.pid = Process.pid_counter
        self.name = f"P{self.pid}"
        self.arrival_time = arrival_time
        self.duration = duration
        self.state = ProcessState.EMBRYO
        self.probability_io = probability_io
        self.quantum = 0

    def __gt__(self, other):
        return self.name > other.name