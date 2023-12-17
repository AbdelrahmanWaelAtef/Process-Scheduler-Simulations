from process import Process

class Queue:
    """
    Implementation of a queue

    Attributes:
        items (list): The items of the queue
    """
    def __init__(self):
        self.items = []

    def push(self, item: Process):
        """
        Pushes a process into the queue

        Returns:
            None
        """
        self.items.append(item)

    def pop(self):
        """
        Pops a process from the queue

        Returns:
            Process: First process in the queue
        """
        return self.items.pop(0) if self.items else None

    def peak(self):
        """
        Checks the first process in the queue
        
        Returns:
            Process: The first process in the queue
        """
        return self.items[0] if self.items else None