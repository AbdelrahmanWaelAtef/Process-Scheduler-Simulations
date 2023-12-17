from process import Process

class Stack:
    """
    Implementation of a queue

    Attributes:
        items (list): The items of the stack
    """
    def __init__(self):
        self.items = []

    def push(self, item: Process):
        """
        Pushes a process into the stack

        Returns:
            None
        """
        self.items.append(item)

    def pop(self):
        """
        Pops a process from the stack

        Returns:
            Process: The top most process in the stack
        """
        return self.items.pop() if self.items else None

    def peak(self):
        """
        Checks the top most process from the stack

        Returns:
            Process: The top most process in the stack
        """
        return self.items[-1] if self.items else None

    def sort(self):
        """
        Sorts the processes in the stack by their arrival time in descending order, 
        meaning the top most element of the stack will be the process with the nearest
        arrival time

        Returns:
            None
        """
        self.items.sort(key=lambda p: p.arrival_time, reverse=True)