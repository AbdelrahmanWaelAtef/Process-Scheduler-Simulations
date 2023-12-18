from enum import Enum

class ProcessState(Enum):
    """
    Describes the state of the process in ENUM format
    """
    RUNNING = 1
    STOPPED = 2
    READY = 3
    EMBRYO = 4

class Process_t:
    """
    Representation of a class

    Attributes:
        pid (int): The PID of the process
        name (str): The name of the process
        arrival_time(int): When will the process arrive
        duration(int): How long the process should run
        state(int): The state of the process
        probability_io(float): The probability of the process to perform an I/O operation
        ticket_count(int): The number of tickets the process has

    Static variable:
    pid_counter (int): Keeps track of how many processes there are and helps in giving names to each process
    """

    pid_counter = 0

    def __init__(self, arrival_time: int, duration: int, probability_io: float, depends_on: int, ticket_count: int = 0):
        Process_t.pid_counter += 1
        self.pid = Process_t.pid_counter
        self.name = f"P{self.pid}"
        self.arrival_time = arrival_time
        self.duration = duration
        self.state = ProcessState.EMBRYO
        self.probability_io = probability_io
        self.ticket_count = ticket_count
        self.depends_on = depends_on