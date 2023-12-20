from process import Process
from stack import Stack
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

def plotGanttChart(data:dict) -> None:
    """
    Plots a gantt chart for the CPU process using data coming from a scheduler output

    Example usage:
        plotGanttChart({
            'state': ['idle', 'idle', 'idle', 'idle', 'idle', 'P1', 'P1', 'P1', 'P2', 'P2', 'P1', 'P1', 'P1', 'P1', 'P1',
            'P1', 'P1', 'P1', 'P1', 'P1', 'P1', 'idle', 'idle', 'idle', 'idle', 'P3', 'P3', 'P4', 'P4', 'P5', 'P5', 'P3',
            'P3', 'P3'],
            'level': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 1, 1, 1]})

    Arguments:
        data (dict[str, list]): Dictionary holding the data for plotting the gantt chart.
    
    Returns:
        None
    """
    # Convert the input data into a DataFrame for easier manipulation
    df = pd.DataFrame(data)

    # Create a new column for the start time of each state
    df['start_time'] = df.index

    # Create a list of unique states for color mapping
    unique_states = df['state'].unique()
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

        # Plot a bar for each state
        ax.broken_barh([(start, end - start)], (level - 0.4, 0.8), facecolors=state_colors[state])

    # Setting labels and title
    ax.set_xlabel('Time Steps')
    ax.set_ylabel('Level')
    ax.set_title('Gantt Chart of CPU Scheduler States')
    ax.set_yticks(range(max_level + 1))
    ax.set_yticklabels([y_ticks_labels[y] for y in range(max_level + 1)])
    ax.set_xticks(range(len(data['state']) + 1))
    ax.grid(True)

    # Add a legend for the states
    legend_elements = [plt.Line2D([0], [0], color=state_colors[state], lw=4, label=state) for state in unique_states]
    ax.legend(handles=legend_elements, loc='upper right')

    # Show the plot
    plt.show()

def getArrivalTimes(process_stack: Stack) -> dict:
    arrival_times = dict()
    for process in process_stack.items:
        arrival_times[process.name] = process.arrival_time
    return arrival_times

def calculateMetrics(data, arrival_times) -> dict:
    occurrences = {}
    details = {}

    for i, process in enumerate(data):
        if process != 'idle':
            if process not in occurrences:
                occurrences[process] = [i, None]
            occurrences[process][1] = i

    for process, (first_idx, last_idx) in occurrences.items():
        duration = last_idx - first_idx + 1
        start_time = first_idx - arrival_times[process]
        details[process] = [first_idx, last_idx + 1, duration, start_time]

    return details
        
# Debug
if __name__ == "__main__":
    stack = initializeProcessStack()
    print("Process Name\tProcess Arival Time\tProcess Duration\tProcess Probability I/O\t\tHave preformed I/O")

    for i in range(50):
        processes = getArrivedProcesses(stack, i)
        for process in processes:
            print(f"{process.name}\t\t{process.arrival_time}\t\t\t{process.duration}\t\t\t{process.probability_io}\t\t\t\t{checkIO(process)}")