from process import Process
import random

class Stack:
    """
    Implementation of a stack

    Attributes:
        items (list): The items of the stack
    """
    def __init__(self) -> None:
        self.items = []

    def push(self, item: Process) -> None:
        """
        Pushes a process into the stack

        Returns:
            None
        """
        self.items.append(item)

    def pop(self) -> Process:
        """
        Pops a process from the stack

        Returns:
            Process: The top most process in the stack
        """

        return self.items.pop() if self.items else None

    def peak(self) -> Process:
        """
        Checks the top most process from the stack

        Returns:
            Process: The top most process in the stack
        """
        return self.items[-1] if self.items else None

    def sort(self) -> None:
        """
        Sorts the processes in the stack by their arrival time in descending order, 
        meaning the top most element of the stack will be the process with the nearest
        arrival time

        Returns:
            None
        """
        self.items.sort(key=lambda p: p.arrival_time, reverse=True)

    def isEmpty(self) -> bool:
        """
        Checks if the stack is empty or not

        Returns:
            bool: True if it is empty, False if not
        """
        return not bool(self.items)
    
    def getRandom(self, rand_value, depends_on_probability) -> Process:
        """
        Get a random process in the stack from a random value and probability

        Returns:
            Process/None: If there is a process, None if not
        """
        if rand_value < depends_on_probability:
            if self.isEmpty():
                return None
            else:
                return random.choice(self.items)
        else:
            return None
        
    def searchForProcess(self, name: str) -> Process:
        """
        Search for a process in the stack using a name

        Returns:
            Process/None: If found, None if not
        """
        for process in self.items:
            if process.name == name:
                return process
        return None