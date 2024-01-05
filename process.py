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

    def __init__(self, arrival_time: int, duration: int, tickets: int = None, depends_on = None, name = None) -> None:
        Process.pid_counter += 1
        self.pid = Process.pid_counter
        if name:
            self.name = name
        else:
            self.name = f"P{self.pid}"
        self.arrival_time = arrival_time
        self.duration = duration
        self.state = ProcessState.EMBRYO
        self.tickets = tickets
        self.depends_on = depends_on
        self.quantum = 0

    def decrementDuration(self):
        self.duration -= 1
        if self.quantum:
            self.quantum -= 1     

    def __gt__(self, other):
        return self.name > other.name