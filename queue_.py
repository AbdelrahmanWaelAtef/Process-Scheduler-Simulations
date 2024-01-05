from process import Process

class Queue:
    """
    Implementation of a queue

    Attributes:
        items (list): The items of the queue
    """
    def __init__(self) -> None:
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
    
    def changePeakProcess(self, process) -> None:
        """
        Changes the peak process with another process

        Returns:
            None
        """
        if self.items:
            self.items[0] = process
        return
    # added this for lottery to remove a process not at the top.
    def remove(self, process) -> None:
        """
        Removes a process from the queue

        Returns:
            None
        """
        if process in self.items:
            self.items.remove(process)
        return