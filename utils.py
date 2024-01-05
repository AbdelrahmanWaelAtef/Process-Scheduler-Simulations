from process import Process
from stack import Stack
import matplotlib.colors as mcolors
import random
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pandas as pd
from io import BytesIO
random.seed(10)

def initializeProcessStack(num_processes: int = 8, min_arrival_time: int = 0, max_arrival_time: int = 30, min_duration:int = 3, max_duration: int = 15, max_tickets: int = None, depends_on_probability: float = None) -> Stack:
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
        rand_arrival_time = random.randint(min_arrival_time, max_arrival_time + 1)
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

def generate_color(process_name: str) -> tuple:
    """
    Generates a dim and relaxing RGBA color code based on the number in the process name.

    Arguments:
    process_name (str): Name of the process (e.g., 'P1', 'P2').

    Returns:
    tuple: RGBA color.
    """
    if process_name.startswith('P'):
        number = int(process_name[1:])  # Extract number from process name
        hue = number / 10.0 % 1  # Ensure hue is between 0 and 1
        saturation = 0.5  # Reduced saturation for a more muted color
        value = 0.7  # Reduced brightness for a dimmer color
        rgb_color = mcolors.hsv_to_rgb([hue, saturation, value])
        return rgb_color  # Returns a RGB color, Matplotlib automatically considers alpha as 1
    return '#808080'  # Default color for non-process states

def plotGanttChart(data: dict) -> None:
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
    df = pd.DataFrame(data)
    df['start_time'] = df.index

    unique_states = df['state'].unique()
    unique_states = unique_states.tolist()
    try:
        unique_states.remove('idle')
    except ValueError:
        pass

    # Use the generate_color function to create color mapping
    state_colors = {state: generate_color(state) for state in unique_states}

    max_level = df['level'].max()
    y_ticks_labels = {level: str(max_level - level) for level in range(max_level + 1)}

    fig, ax = plt.subplots(figsize=(15, 8))

    for index, row in df.iterrows():
        start = row['start_time']
        end = start + 1
        level = max_level - row['level']
        state = row['state']

        if state == 'idle':
            continue

        ax.broken_barh([(start, end - start)], (level - 0.4, 0.8), facecolors=state_colors[state])

    ax.set_xlabel('Time Steps')
    ax.set_ylabel('Level')
    ax.set_title('Gantt Chart of CPU Scheduler States')
    ax.set_yticks(range(max_level + 1))
    ax.set_yticklabels([y_ticks_labels[y] for y in range(max_level + 1)])
    ax.set_xticks(range(len(data['state']) + 1))
    tick_labels = [str(i) for i in range(len(data['state']) + 1)]
    ax.set_xticklabels(tick_labels, rotation=45)
    ax.grid(True)

    legend_elements = [plt.Line2D([0], [0], color=state_colors[state], lw=4, label=state) for state in unique_states]
    ax.legend(handles=legend_elements, loc='upper right')
    plt.show()

def saveGanttChart(data:dict, ax, canvas):
    """
    Saves a gantt chart for the CPU process using data coming from a scheduler output

    Arguments:
    data (dict[str, list]): Dictionary holding the data for plotting the gantt chart.

    Example usage:
    >>> saveGanttChart({
            'state': ['idle', 'idle', 'idle', 'idle', 'idle', 'P1', 'P1', 'P1', 'P2', 'P2', 'P1', 'P1', 'P1', 'P1', 'P1',
            'P1', 'P1', 'P1', 'P1', 'P1', 'P1', 'idle', 'idle', 'idle', 'idle', 'P3', 'P3', 'P4', 'P4', 'P5', 'P5', 'P3',
            'P3', 'P3'],
            'level': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 1, 1, 1]})
    
    Returns:
        PIL.Image
    """
    # Convert the input data into a DataFrame for easier manipulation
    df = pd.DataFrame(data)
    df['start_time'] = df.index

    unique_states = df['state'].unique()
    unique_states = unique_states.tolist()
    try:
        unique_states.remove('idle')
    except ValueError:
        pass

    # Use the generate_color function to create color mapping
    state_colors = {state: generate_color(state) for state in unique_states}

    max_level = df['level'].max()
    y_ticks_labels = {level: str(max_level - level) for level in range(max_level + 1)}

    ax.clear()
    for index, row in df.iterrows():
        start = row['start_time']
        end = start + 1
        level = max_level - row['level']
        state = row['state']

        if state == 'idle':
            continue

        ax.broken_barh([(start, end - start)], (level - 0.4, 0.8), facecolors=state_colors[state])

    ax.set_xlabel('Time Steps')
    ax.set_ylabel('Level')
    ax.set_title('Gantt Chart of CPU Scheduler States')
    ax.set_yticks(range(max_level + 1))
    ax.set_yticklabels([y_ticks_labels[y] for y in range(max_level + 1)])
    ax.set_xticks(range(len(data['state']) + 1))
    tick_labels = [str(i) for i in range(len(data['state']) + 1)]
    ax.set_xticklabels(tick_labels, rotation=45)
    ax.grid(True)

    legend_elements = [plt.Line2D([0], [0], color=state_colors[state], lw=4, label=state) for state in unique_states]
    ax.legend(handles=legend_elements, loc='upper right')
    canvas.draw()
    plt.close()
    

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

def calculatePerformance(data: dict):
    waiting_time = 0
    response_time = 0
    count = 0
    for key in data:
        count += 1
        waiting_time += data[key][-3]
        response_time += data[key][-2]
    return waiting_time/count, response_time/count

def savePerformancePlot(names, average_waiting_times, average_response_times, ax, canvas):
    X_axis = np.arange(len(names)) 
    
    bars1 = ax.bar(X_axis - 0.2, average_waiting_times, 0.4, label='Average Waiting Time')
    bars2 = ax.bar(X_axis + 0.2, average_response_times, 0.4, label='Average Response Time')
    
    # Adding the text on top of the bars
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    ax.set_xticks(X_axis, names) 
    ax.set_xlabel("Schedules") 
    ax.set_ylabel("Time") 
    ax.set_title("Performance of Each Scheduler Running on 100 Random Processes") 
    ax.legend() 
    canvas.draw()
    plt.close()

        
# Debug
if __name__ == "__main__":
    stack = initializeProcessStack()
    print("Process Name\tProcess Arival Time\tProcess Duration")

    for i in range(50):
        processes = getArrivedProcesses(stack, i)
        for process in processes:
            print(f"{process.name}\t\t{process.arrival_time}\t\t\t{process.duration}")