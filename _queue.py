from process import Process

class Queue:
    """
    Implementation of a queue

    Attributes:
        items (list): The items of the queue
    """
    def __init__(self):
        self.items = []

    def push(self, item: Process) -> None:
        """
        Pushes a process into the queue

        Returns:
            None
        """
        self.items.append(item)

    def pop(self) -> Process:
        """
        Pops a process from the queue

        Returns:
            Process: First process in the queue
        """
        return self.items.pop(0) if self.items else None

    def peak(self) -> Process:
        """
        Checks the first process in the queue
        
        Returns:
            Process: The first process in the queue
        """
        return self.items[0] if self.items else None
    
    def isEmpty(self) -> bool:
        """
        Checks if the queue is empty or not

        Returns:
            bool: True if it is empty, False if not
        """
        return not bool(self.items)