from process import Process
from stack import Stack
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def initializeProcessStack(num_processes: int = 8, max_arrival_time: int = 30, min_duration:int = 3, max_duration: int = 15, max_tickets: int = None, depends_on_probability: float = None) -> Stack:
    """
    Initializes a stack of processes with random attributes.

    This function creates a stack of processes with random arrival times, durations, and probabilities of IO.
    The generated processes are sorted based on their arrival times.

    Arguments:
        num_processes (int): The number of processes to generate (default is 50).
        max_arrival_time (int): The maximum arrival time for generated processes (default is 50).
        min_duration (int): The minimum duration for generated processes (default is 10).
        max_duration (int): The maximum duration for generated processes (default is 50).
        max_tickets (int): The maximum number of tickets a process can request.
        depends_on_probability (float): The probability of a process depending on another process.

    Example usage:
    >>> initializeProcessStack()
        Stack()

    Returns:
        Stack: A stack of Process objects representing the generated processes, sorted by arrival time.
    """
    stack = Stack()
    for _ in range(num_processes):
        rand_arrival_time = random.randint(0, max_arrival_time + 1)
        rand_duration = random.randint(min_duration, max_duration + 1)
        if max_tickets:
            rand_ticket = random.randint(1, max_tickets + 1)
            if depends_on_probability:
                rand_depends_on = random.uniform(0, 1)
                depends_on = stack.getRandom(rand_depends_on, depends_on_probability)
                stack.push(Process(rand_arrival_time, rand_duration, rand_ticket, depends_on))
            else:
                stack.push(Process(rand_arrival_time, rand_duration, rand_ticket))
        else:
            stack.push(Process(rand_arrival_time, rand_duration))
    stack.sort()
    return stack

def getArrivedProcesses(stack: Stack, time_step:int) -> list:
    """
    Gets the processes the arrives at the given time step, and removes the processes from the stack.

    Arguments:
    stack (Stack): Stack of initialized processes.
    time_step (int): The current the time step.

    Example usage:
    >>> getArrivedProcesses(stack, 1)
        [Process, Process]

    Returns:
        List(Process): A list of the processes that arrives at that time step.
    """
    processes = []
    while not stack.isEmpty() and stack.peak().arrival_time == time_step:
        processes.append(stack.pop())
    return processes

def plotGanttChart(data:dict) -> None:
    """
    Plots a gantt chart for the CPU process using data coming from a scheduler output

    Arguments:
    data (dict[str, list]): Dictionary holding the data for plotting the gantt chart.

    Example usage:
    >>> plotGanttChart({
            'state': ['idle', 'idle', 'idle', 'idle', 'idle', 'P1', 'P1', 'P1', 'P2', 'P2', 'P1', 'P1', 'P1', 'P1', 'P1',
            'P1', 'P1', 'P1', 'P1', 'P1', 'P1', 'idle', 'idle', 'idle', 'idle', 'P3', 'P3', 'P4', 'P4', 'P5', 'P5', 'P3',
            'P3', 'P3'],
            'level': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 1, 1, 1]})
    
    Returns:
        None
    """
    # Convert the input data into a DataFrame for easier manipulation
    df = pd.DataFrame(data)

    # Create a new column for the start time of each state
    df['start_time'] = df.index

    # Create a list of unique states for color mapping
    unique_states = df['state'].unique()
    unique_states = unique_states.tolist()
    unique_states.remove('idle')
    color_map = plt.cm.get_cmap('tab20', len(unique_states))
    state_colors = {state: color_map(i) for i, state in enumerate(unique_states)}

    # Determine the maximum level to flip the chart and adjust y-tick labels
    max_level = df['level'].max()
    y_ticks_labels = {level: str(max_level - level) for level in range(max_level + 1)}

    # Start plotting
    fig, ax = plt.subplots(figsize=(15, 8))

    # Iterate over the DataFrame and plot each block
    for index, row in df.iterrows():
        start = row['start_time']
        end = start + 1  # Each state lasts for 1 time step
        level = max_level - row['level']  # Flip the level
        state = row['state']

        if state == 'idle':
            continue

        # Plot a bar for each state
        ax.broken_barh([(start, end - start)], (level - 0.4, 0.8), facecolors=state_colors[state])

    # Setting labels and title
    ax.set_xlabel('Time Steps')
    ax.set_ylabel('Level')
    ax.set_title('Gantt Chart of CPU Scheduler States')
    ax.set_yticks(range(max_level + 1))
    ax.set_yticklabels([y_ticks_labels[y] for y in range(max_level + 1)])
    ax.set_xticks(range(len(data['state']) + 1))
    tick_labels = [str(i) for i in range(len(data['state']) + 1)]
    ax.set_xticklabels(tick_labels, rotation=45)
    ax.grid(True)

    # Add a legend for the states
    legend_elements = [plt.Line2D([0], [0], color=state_colors[state], lw=4, label=state) for state in unique_states]
    ax.legend(handles=legend_elements, loc='upper right')

    # Show the plot
    plt.show()

def getProcessData(process_stack: Stack) -> dict:
    """
    Takes a stack of processes and returns a dictionary of all processes as keys
    with their arrival time and duration in a list as values

    Arguments:
    process_stack (Stack): Stack of processes

    Example usage:
    >>> getProcessData(process_stack)
    {'P4': [12, 1], 'P3': [8, 7], 'P2': [4, 7], 'P1': [3, 8]}
    
    returns:
    dict(str, list)
    """
    details = dict()
    for process in process_stack.items:
        details[process.name] = [process.arrival_time, process.duration]
    return details

def calculateMetrics(data: list, processes_details:dict) -> dict:
    """
    Takes run-time data of a scheduler and process details,
    and calculates: response time, waiting time and turnaround time

    Arguments:
    data (dict): Dictionary containing all the run-time data of a scheduler
    process_details (dict): Dictionary containing details about the processes themselves before running

    Example usage:
    >>> calculateMetrics(['idle', 'idle', 'idle', 'P1', 'P1', 'P2', 'P2', 'P1', 'P1', 'P1', 'P1', 'P1', 'P3', 'P3',
                          'P4', 'P2', 'P2', 'P2', 'P2', 'P2', 'P3', 'P3', 'P3', 'P3', 'P3', 'P1'],
                         {'P4': [12, 1], 'P3': [8, 7], 'P2': [4, 7], 'P1': [3, 8]})
        {'P1': [3, 3, 26, 8, 15, 0, 23], 'P2': [4, 5, 20, 7, 9, 1, 16], 'P3': [8, 12, 25, 7, 10, 4, 17], 'P4': [12, 14, 15, 1, 2, 2, 3]}

    Returns:
    dict(str, list): A dictionary with processes as keys, and list of all calculated time scheduling metrics
    for the process in a list as values
    """
    occurrences = {}
    details = {}

    for i, process in enumerate(data):
        if process != 'idle':
            if process not in occurrences:
                occurrences[process] = [i, None]
            occurrences[process][1] = i

    for process, (first_idx, last_idx) in occurrences.items():
        turnaround_time = last_idx - processes_details[process][0] + 1
        response_time = first_idx - processes_details[process][0]
        waiting_time = turnaround_time - processes_details[process][1]
        details[process] = [processes_details[process][0], first_idx, last_idx + 1, processes_details[process][1], waiting_time, response_time, turnaround_time]

    return details
        
# Debug
if __name__ == "__main__":
    stack = initializeProcessStack()
    print("Process Name\tProcess Arival Time\tProcess Duration")

    for i in range(50):
        processes = getArrivedProcesses(stack, i)
        for process in processes:
            print(f"{process.name}\t\t{process.arrival_time}\t\t\t{process.duration}")