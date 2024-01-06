import tkinter as tk
import os
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from queue_ import Queue
from utils import *
from mlfq import MLFQ
from sjf import SJF
from fcfs import FCFS
from srtf import SRTF
from rr import RoundRobin
from lottery import Lottery
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
import traceback

class SchedulerApp(tk.Tk):
    """ Main application class for the scheduler simulation.

    This class initializes the main application window and manages the different frames used in the application.
    """
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the SchedulerApp.

        Sets up the main window properties, frame container, and initializes the frames for the application.
        """
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Scheduler Simulation")
        self.geometry("400x150")

        # Define the container frame
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.iconbitmap('schedule.ico')

        # Initialize a dictionary to hold the frames
        self.frames = {}

        self.scheduler_name = ""
        self.configurations = dict()
        self.processes = Stack()
        self.waiting_processes = []
        self.queue = Queue()
        self.processes_IO = None
        self.time_step = -1
        self.process_data = None
        self.prev_details = {'state': [], 'level': []}
        self.past_details = []
        self.finished = False
        self.results = None
        self.schedulers = []

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Iterate over the frame classes and add them to the container
        for F in (StartFrame, RoundRobinFrame, ProcessConfigFrame,
                  MLFQFrame, MLFQConfigFrame, LotteryFrame,
                  CustomProcessConfigFrame, CustomProcessCreationFrame,
                  CustomProcessCreationFrameTickets, FinalFrame, REStartFrame,
                  RELotteryFrame, REMLFQConfigFrame, REMLFQFrame, RERoundRobinFrame,
                  RECustomProcessCreationFrame, REProcessConfigFrame, ModifyProcessFrame,
                  RemoveProcesses, InitialFrame, SCMLFQConfigFrame, SCMLFQFrame, SCRoundRobinFrame,
                  SCStartFrame, SCFinalFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Display the initial frame
        self.showFrame(InitialFrame)

    def showFrame(self, cont) -> None:
        """Show a specified frame in the application.

        Args:
            cont (class): The class of the frame to be displayed.
        """
        # Raise the selected frame to the top
        frame = self.frames[cont]
        frame.tkraise()

        # Special handling for EncodeDecodeSelection frame
        if cont == CustomProcessConfigFrame or cont == ProcessConfigFrame or cont == REProcessConfigFrame:
            self.geometry("400x230")  # Set a custom size that fits the contents of this frame
        elif cont == LotteryFrame:
            self.geometry("400x250")
        elif cont == RoundRobinFrame or cont == RERoundRobinFrame or cont == SCRoundRobinFrame:
            self.geometry("400x150")
        elif cont == MLFQFrame or cont == REMLFQFrame or cont == SCMLFQFrame:
            self.geometry("400x320")
        elif cont == MLFQConfigFrame or cont == REMLFQConfigFrame or cont ==SCMLFQConfigFrame:
            self.geometry("800x200")
        elif cont == CustomProcessCreationFrame or cont == RECustomProcessCreationFrame:
            self.geometry("500x200")
        elif cont == CustomProcessCreationFrameTickets:
            self.geometry("820x200")
        elif cont == FinalFrame or cont == SCFinalFrame:
            self.geometry(f"1620x800")
        elif cont == ModifyProcessFrame:
            self.geometry("400x100")
        elif cont == SCStartFrame:
            self.geometry("400x200")
        elif cont == RemoveProcesses:
            self.geometry(f"400x{200+ 25*len(self.frames[RemoveProcesses].names)}")
        else:
            self.geometry("400x150") # Resize window to fit the frame

    def setupScheduler(self):
        self.total_duration = 0
        self.process_data = getProcessData(self.processes)
        for process in self.processes.items:
            self.total_duration += process.duration
        self.details = {"state":['idle']*self.total_duration, "level":[0]*self.total_duration}
        self.past_details.append(self.details)
        if self.scheduler_name == "MLFQ":
            self.scheduler = MLFQ(process_stack=self.processes,
                                    boost_time=self.configurations["boost_time"],
                                    pre_emptive=self.configurations["pre-emptive"],
                                    quanta=self.configurations["quanta"],
                                    structure=self.configurations["structure"])
        if self.scheduler_name == "SJF":
            self.scheduler = SJF(process_stack=self.processes)
        if self.scheduler_name == "FCFS":
            self.scheduler = FCFS(process_stack=self.processes)
        if self.scheduler_name == "SRTF":
            self.scheduler = SRTF(process_stack=self.processes)
        if self.scheduler_name == "Round-Robin":
            self.scheduler = RoundRobin(process_stack=self.processes, quantum=self.configurations["quantum"])
        if self.scheduler_name == "Lottery":
            self.scheduler = Lottery(process_stack=self.processes, quantum=self.configurations["quantum"], pre_emptive=self.configurations["pre-emptive"])


    def calculateAllMetrics(self):
        self.results = calculateMetrics(self.details["state"], self.process_data)
        return

    def reSetupScheduler(self):
        if self.scheduler_name == "MLFQ":
            self.scheduler = MLFQ(process_stack=self.processes,
                                    boost_time=self.configurations["boost_time"],
                                    pre_emptive=self.configurations["pre-emptive"],
                                    quanta=self.configurations["quanta"],
                                    structure=self.configurations["structure"])
            while self.queue.peak():
                self.scheduler.structure[0].push(self.queue.pop())
            for process in self.waiting_processes:
                self.scheduler.structure[0].push(process)
            self.scheduler.details = self.prev_details
        if self.scheduler_name == "SJF":
            self.scheduler = SJF(process_stack=self.processes)
            while self.queue.peak():
                self.scheduler.queue.push(self.queue.pop())
            for process in self.waiting_processes:
                self.scheduler.queue.push(process)
            self.scheduler.details = self.prev_details
        if self.scheduler_name == "FCFS":
            self.scheduler = FCFS(process_stack=self.processes)
            while self.queue.peak():
                self.scheduler.queue.push(self.queue.pop())
            for process in self.waiting_processes:
                self.scheduler.queue.push(process)
            self.scheduler.details = self.prev_details
        if self.scheduler_name == "SRTF":
            self.scheduler = SRTF(process_stack=self.processes)
            while self.queue.peak():
                self.scheduler.queue.push(self.queue.pop())
            for process in self.waiting_processes:
                self.scheduler.queue.push(process)
            self.scheduler.details = self.prev_details
        if self.scheduler_name == "Round-Robin":
            self.scheduler = RoundRobin(process_stack=self.processes, quantum=self.configurations["quantum"])
            while self.queue.peak():
                self.scheduler.queue.push(self.queue.pop()) 
            for process in self.waiting_processes:
                self.scheduler.queue.push(process)
            self.scheduler.details = self.prev_details
        if self.scheduler_name == "Lottery":
            self.scheduler = Lottery(process_stack=self.processes, quantum=self.configurations["quantum"], pre_emptive=self.configurations["pre-emptive"])
            while self.queue.peak():
                self.scheduler.queue.push(self.queue.pop())
            for process in self.waiting_processes:
                self.scheduler.queue.push(process)
            self.scheduler.details = self.prev_details

    def on_close(self):
        # You can perform any cleanup or confirmation here
        if messagebox.askokcancel("Quit", "Do you want to close the window?"):
            self.delete_files_in_directory()
            self.destroy()

    def delete_files_in_directory(self):
        try:
            files = os.listdir("image_cache")
            for file in files:
                file_path = os.path.join("image_cache", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except OSError:
            print("Error occurred while deleting files.")

    def step(self):
        if self.scheduler.step():
            self.time_step += 1
            if self.time_step >= len(self.details['state']):
                self.details['state'].append(self.scheduler.details['state'][self.time_step])
                self.details['level'].append(self.scheduler.details['level'][self.time_step])
            else:
                self.details['state'][self.time_step] = self.scheduler.details['state'][self.time_step]
                self.details['level'][self.time_step] = self.scheduler.details['level'][self.time_step]
            self.processes = self.scheduler.process_stack
            details = {'state': [], 'level': []}
            for i in range(len(self.details['state'])):
                details['state'].append(self.details['state'][i])
                details['level'].append(self.details['level'][i])
            self.past_details.append(details)
            self.finished = False
            return True
        self.finished = True
        return False
    
    def computePerformance(self):
        self.scheduler_names = []
        self.average_waiting_times = []
        self.average_response_times = []
        for scheduler in self.schedulers:
            self.scheduler_names.append(scheduler.name)
            details = scheduler.run()
            results = calculateMetrics(details["state"], self.process_data)
            average_waiting_time, average_response_time = calculatePerformance(results)
            self.average_waiting_times.append(average_waiting_time)
            self.average_response_times.append(average_response_time)
    
class InitialFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Choose what do you want to do")
        label.pack(pady=10, padx=10)
        
        statistical_comparison_button = ttk.Button(self, text="Statistical Comparison",
                                    command=lambda: self.goToStatsFrame(controller))
        statistical_comparison_button.pack(pady=10, padx=10)
        
        simulation_button = ttk.Button(self, text="Simulation",
                                    command=lambda: self.goToSimFrame(controller))
        simulation_button.pack(pady=10, padx=10)

    def goToStatsFrame(self, controller) -> None:
        stack = Stack()
        stack.push(Process(0, 10, name="P1"))
        stack.push(Process(1, 10, name="P2"))
        stack.sort()
        controller.processes = customProcessStack()
        controller.process_data = getProcessData(controller.processes)
        controller.showFrame(SCStartFrame)

    def goToSimFrame(self, controller) -> None:
        controller.showFrame(StartFrame)

class StartFrame(tk.Frame):
    """Class for the StartFrame.

    This class represents a frame in the scheduler application, specifically for startframe.
    """
    def __init__(self, parent, controller) -> None:
        """Initialize the StartFrame frame.

        Sets up the UI elements and functionality specific to the startframe.
        """
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Choose the scheduling algorithm")
        label.pack(pady=10, padx=10)

        # Dropdown menu for scheduling algorithms
        self.algorithm = tk.StringVar()
        self.algorithm.set("FCFS") # default value
        dropdown = ttk.Combobox(self, textvariable=self.algorithm, 
                                values=["FCFS", "SJF", "SRTF", "Round-Robin", "MLFQ", "Lottery"])
        dropdown.pack(pady=10, padx=10)

        # Button to proceed to the corresponding frame
        proceed_button = ttk.Button(self, text="Proceed",
                                    command=lambda: self.goToFrame(controller))
        proceed_button.pack(pady=10, padx=10)

    def goToFrame(self, controller) -> None:
            selection = self.algorithm.get()
            if selection == "FCFS":
                controller.scheduler_name = "FCFS"
                controller.showFrame(ProcessConfigFrame)
            elif selection == "SJF":
                controller.scheduler_name = "SJF"
                controller.showFrame(ProcessConfigFrame)
            elif selection == "SRTF":
                controller.scheduler_name = "SRTF"
                controller.showFrame(ProcessConfigFrame)
            elif selection == "Round-Robin":
                controller.scheduler_name = "Round-Robin"
                controller.showFrame(RoundRobinFrame)
            elif selection == "MLFQ":
                controller.scheduler_name = "MLFQ"
                controller.showFrame(MLFQFrame)
                messagebox.showinfo("MLFQ", "If you do not want boosting, do not put a value in the boost time box")
            elif selection == "Lottery":
                controller.scheduler_name = "Lottery"
                controller.showFrame(LotteryFrame)

class RoundRobinFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        quanta_label = tk.Label(self, text="Quantum size")
        quanta_label.pack(pady=10, padx=10)

        self.quantum = tk.Entry(self)
        self.quantum.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        try:
            self.controller.configurations["quantum"] = int(self.quantum.get())
            self.controller.showFrame(ProcessConfigFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")


class ProcessConfigFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.num_processes = 30

        label = tk.Label(self, text="Number of processes")
        label.pack(pady=10, padx=10)

        self.num_processes_entry = tk.Entry(self)
        self.num_processes_entry.pack(pady=10, padx=10)

        process_creation_label = tk.Label(self, text="Process Creation")
        process_creation_label.pack(pady=10, padx=10)

        self.process_creation = tk.StringVar()
        self.process_creation.set("Random")  # default value
        self.process_creation_dropdown = ttk.Combobox(self, textvariable=self.process_creation,
                                                 values=["Custom", "Random"])
        self.process_creation_dropdown.pack(pady=10, padx=10)

        self.proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        self.proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        try:
            if self.process_creation_dropdown.get() == "Custom":
                self.controller.frames[CustomProcessCreationFrame].num_processes = int(self.num_processes_entry.get())
                self.controller.frames[CustomProcessCreationFrame].createProcessFrames()
                self.controller.showFrame(CustomProcessCreationFrame)
            else:
                self.controller.processes = initializeProcessStack(int(self.num_processes_entry.get()))
                self.controller.setupScheduler()
                self.controller.process_data = getProcessData(self.controller.processes)
                self.controller.frames[FinalFrame].displayFrame()
                self.controller.showFrame(FinalFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")


class MLFQFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Choose Pre-emption")
        label.pack(pady=10, padx=10)

        self.preemption = tk.StringVar()
        self.preemption.set("Pre-emptive")  # default value
        self.dropdown = ttk.Combobox(self, textvariable=self.preemption,
                                values=["Pre-emptive", "Non-pre-emptive"])
        self.dropdown.pack(pady=10, padx=10)

        levels_label = tk.Label(self, text="Number of levels")
        levels_label.pack(pady=10, padx=10)
                        
        self.num_levels_entry = tk.Entry(self)
        self.num_levels_entry.pack(pady=10, padx=10)

        boost_label = tk.Label(self, text="Boost time")
        boost_label.pack(pady=10, padx=10)

        self.boost_entry = tk.Entry(self)
        self.boost_entry.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        try:
            if (self.boost_entry.get()):
                boost_time = int(self.boost_entry.get())
            else:
                boost_time = 1000000
            self.controller.configurations["boost_time"] = boost_time
            self.controller.configurations["pre-emptive"] = self.dropdown.get() == "Pre-emptive"
            self.controller.frames[MLFQConfigFrame].num_levels = int(self.num_levels_entry.get())
            self.controller.frames[MLFQConfigFrame].createLevelFrames()
            self.controller.showFrame(MLFQConfigFrame)
            messagebox.showinfo("MLFQ", "If you choose FCFS, you do not need to put the quantum size")
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class LotteryFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Choose Pre-emption")
        label.pack(pady=10, padx=10)

        self.preemption = tk.StringVar()
        self.preemption.set("Pre-emptive")  # default value
        self.dropdown = ttk.Combobox(self, textvariable=self.preemption,
                                values=["Pre-emptive", "Non-pre-emptive"])
        self.dropdown.pack(pady=10, padx=10)

        quanta_label = tk.Label(self, text="Quanta size")
        quanta_label.pack(pady=10, padx=10)

        self.quantum = tk.Entry(self)
        self.quantum.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        self.controller.configurations["quantum"] = int(self.quantum.get())
        self.controller.configurations["pre-emptive"] = self.dropdown.get() == "Pre-emptive"
        self.controller.showFrame(CustomProcessConfigFrame)


class MLFQConfigFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.current_level = 0  # New attribute to track the current level
        self.currentLevelIndex = 0
        self.level_frames = []
        self.levels = []
        self.quanta = []

        # Button to show the next process
        self.next_level_button = ttk.Button(self, text="Next Process", command=self.showNextLevel)

        # Button to proceed after all processes are entered
        self.proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)

    def showNextLevel(self) -> None:
        try:
            if self.level_frames[self.currentLevelIndex][1].get() == "Round-Robin":
                self.levels.append(Queue())
                self.quanta.append(int(self.level_frames[self.currentLevelIndex][2].get()))
            else:
                self.levels.append(Queue())
                self.quanta.append(100000)
            # Hide the current process frame
            self.level_frames[self.currentLevelIndex][0].pack_forget()
            self.next_level_button.pack_forget()
            # Move to the next process
            self.currentLevelIndex = (self.currentLevelIndex + 1)

            # Show the next process frame
            self.level_frames[self.currentLevelIndex][0].pack(fill="both", expand=True, padx=10, pady=5)
            if self.currentLevelIndex == self.num_levels - 1:
                self.next_level_button.pack_forget()
                self.proceed_button.pack(pady=10)
            else:
                self.next_level_button.pack(pady=10)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

    def createLevelFrames(self) -> None:
        for level in range(self.num_levels):
            level_frame = tk.LabelFrame(self, text=f"Level {level + 1} Configuration")
            level_frame.pack(fill="both", expand=True, padx=10, pady=5)

            type_label = tk.Label(level_frame, text="Choose Type:")
            type_label.pack(side="left", padx=5)

            type_var = tk.StringVar()
            type_var.set("Round-robin")  # default value
            type_dropdown = ttk.Combobox(level_frame, textvariable=type_var,
                                         values=["Round-Robin", "FCFS"])
            type_dropdown.pack(side="left", padx=5)

            quanta_label = tk.Label(level_frame, text="Quanta size:")
            quanta_label.pack(side="left", padx=5)

            quanta_entry = tk.Entry(level_frame)
            quanta_entry.pack(side="left", padx=5)

            self.level_frames.append((level_frame, type_dropdown, quanta_entry))
            level_frame.pack_forget()  # Initially hide all frames
        # Show the first level
        self.level_frames[0][0].pack(fill="both", expand=True, padx=10, pady=5)
        self.next_level_button.pack(pady=10)

    def proceed(self) -> None:
        try:
            if self.level_frames[self.currentLevelIndex][1].get() == "Round-Robin":
                self.levels.append(Queue())
                self.quanta.append(int(self.level_frames[self.currentLevelIndex][2].get()))
            else:
                self.levels.append(Queue())
                self.quanta.append(100000)
            self.controller.configurations["quanta"] = self.quanta
            self.controller.configurations["structure"] = self.levels
            self.controller.showFrame(ProcessConfigFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")


class CustomProcessConfigFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Number of processes")
        label.pack(pady=10, padx=10)

        self.num_processes_entry = tk.Entry(self)
        self.num_processes_entry.pack(pady=10, padx=10)

        self.process_creation_label = tk.Label(self, text="Process Creation")
        self.process_creation_label.pack(pady=10, padx=10)

        self.process_creation = tk.StringVar()
        self.process_creation.set("Random")  # default value
        self.process_creation_dropdown = ttk.Combobox(self, textvariable=self.process_creation,
                                                 values=["Custom", "Random"])
        self.process_creation_dropdown.pack(pady=10, padx=10)

        self.proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        self.proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        try:
            if self.process_creation_dropdown.get() == "Custom":
                self.controller.frames[CustomProcessCreationFrameTickets].num_processes = int(self.num_processes_entry.get())
                self.controller.frames[CustomProcessCreationFrameTickets].createProcessFrames()
                self.controller.showFrame(CustomProcessCreationFrameTickets)
            else:
                self.controller.processes = initializeProcessStack(int(self.num_processes_entry.get()), max_tickets=100, depends_on_probability=0.01)
                self.controller.setupScheduler()
                self.controller.process_data = getProcessData(self.controller.processes)
                self.controller.frames[FinalFrame].displayFrame()
                self.controller.showFrame(FinalFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")


class CustomProcessCreationFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.num_processes = self.controller.frames[ProcessConfigFrame].num_processes
        self.current_process_index = 0
        self.process_frames = []
        self.next_process_button = ttk.Button(self, text="Next Process", command=self.showNextProcess)
        self.proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)

    def createProcessFrames(self) -> None:
        for process_num in range(self.num_processes):
            process_frame = tk.LabelFrame(self, text=f"Process #{process_num + 1}")
            process_frame.pack(fill="both", expand=True, padx=10, pady=5)

            arrival_label = tk.Label(process_frame, text="Arrival time:")
            arrival_label.pack(side="left", padx=5)
            arrival_entry = tk.Entry(process_frame)
            arrival_entry.pack(side="left", padx=5)

            burst_label = tk.Label(process_frame, text="Burst time:")
            burst_label.pack(side="left", padx=5)
            burst_entry = tk.Entry(process_frame)
            burst_entry.pack(side="left", padx=5)

            self.process_frames.append((process_frame, arrival_entry, burst_entry))
            process_frame.pack_forget()  # Initially hide the frame

            # Show only the first process frame initially
        self.process_frames[0][0].pack(fill="both", expand=True, padx=10, pady=5)
        if self.num_processes > 1:
            self.next_process_button.pack(pady=10)
        else:
            self.proceed_button.pack(pady=10)

    def showNextProcess(self) -> None:
        try:
            # Hide the current process frame
            self.process_frames[self.current_process_index][0].pack_forget()
            self.next_process_button.pack_forget()
            self.controller.processes.push(Process(arrival_time=int(self.process_frames[self.current_process_index][1].get()),
                                                    duration=int(self.process_frames[self.current_process_index][2].get())))
            # Move to the next process
            self.current_process_index = (self.current_process_index + 1)

            # Show the next process frame
            self.process_frames[self.current_process_index][0].pack(fill="both", expand=True, padx=10, pady=5)
            if self.current_process_index == self.num_processes - 1:
                self.next_process_button.pack_forget()
                self.proceed_button.pack(pady=10)
            else:
                self.next_process_button.pack(pady=10)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

    def proceed(self) -> None:
        try:
            self.controller.processes.push(Process(arrival_time=int(self.process_frames[self.current_process_index][1].get()),
                                                    duration=int(self.process_frames[self.current_process_index][2].get())))
            self.controller.processes.sort()
            self.controller.setupScheduler()
            self.controller.process_data = getProcessData(self.controller.processes)
            self.controller.frames[FinalFrame].displayFrame()
            self.controller.showFrame(FinalFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")
        
class CustomProcessCreationFrameTickets(tk.Frame):
    def __init__(self, parent, controller) -> None:  # Assuming defaults for demonstration
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.process_frames = []
        self.current_process_index = 0
        self.num_processes = 0
        self.next_process_button = ttk.Button(self, text="Next Process", command=self.showNextProcess)
        self.proceed_button = ttk.Button(self, text="Proceed",
                                    command=lambda: self.proceed())
        
    def createProcessFrames(self) -> None:
        for process_num in range(self.num_processes):
            process_frame = tk.LabelFrame(self, text=f"Process #{process_num + 1}")
            process_frame.pack(fill="both", expand=True, padx=10, pady=5)

            arrival_label = tk.Label(process_frame, text="Arrival time:")
            arrival_label.pack(side="left", padx=5)
            arrival_entry = tk.Entry(process_frame)
            arrival_entry.pack(side="left", padx=5)

            burst_label = tk.Label(process_frame, text="Burst time:")
            burst_label.pack(side="left", padx=5)
            burst_entry = tk.Entry(process_frame)
            burst_entry.pack(side="left", padx=5)

            tickets_label = tk.Label(process_frame, text="Number of tickets:")
            tickets_label.pack(side="left", padx=5)
            tickets_entry = tk.Entry(process_frame)
            tickets_entry.pack(side="left", padx=5)

            label = tk.Label(process_frame, text="Depends on")
            label.pack(side="left", padx=5)

            depends_on_entry = tk.Entry(process_frame)
            depends_on_entry.pack(side="left", padx=5)

            self.process_frames.append((process_frame, arrival_entry, burst_entry, tickets_entry, depends_on_entry if depends_on_entry else None))
            process_frame.pack_forget()  # Initially hide the frame

            # Show only the first process frame initially
        self.process_frames[0][0].pack(fill="both", expand=True, padx=10, pady=5)
        self.next_process_button.pack(pady=10)

    def showNextProcess(self) -> None:
        try:
            # Hide the current process frame
            self.process_frames[self.current_process_index][0].pack_forget()
            self.next_process_button.pack_forget()

            self.controller.processes.push(Process(arrival_time=int(self.process_frames[self.current_process_index][1].get()),
                                            duration=int(self.process_frames[self.current_process_index][2].get()),
                                            tickets=int(self.process_frames[self.current_process_index][3].get()),
                                            depends_on=self.controller.processes.searchForProcess(self.process_frames[self.current_process_index][4].get()) if self.process_frames[self.current_process_index][4].get() != None else None))
            # Move to the next process
            self.current_process_index = (self.current_process_index + 1)

            # Show the next process frame
            self.process_frames[self.current_process_index][0].pack(fill="both", expand=True, padx=10, pady=5)
            if self.current_process_index == self.num_processes - 1:
                self.next_process_button.pack_forget()
                self.proceed_button.pack(pady=10)
            else:
                self.next_process_button.pack(pady=10)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

    def proceed(self) -> None:
        try:
            self.controller.processes.push(Process(arrival_time=int(self.process_frames[self.current_process_index][1].get()),
                                            duration=int(self.process_frames[self.current_process_index][2].get()),
                                            tickets=int(self.process_frames[self.current_process_index][3].get()),
                                            depends_on=self.controller.processes.searchForProcess(self.process_frames[self.current_process_index][4].get()) if self.process_frames[self.current_process_index][4].get() != None else None))
            
            self.controller.processes.sort()
            self.controller.setupScheduler()
            self.controller.process_data = getProcessData(self.controller.processes)
            self.controller.frames[FinalFrame].displayFrame()
            self.controller.showFrame(FinalFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class FinalFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.counter = 0

    def step(self):
        self.counter += 1
        if self.counter == len(self.controller.past_details):
            if self.controller.step():
                saveGanttChart(self.controller.past_details[self.counter], self.ax, self.canvas)
            else:
                self.counter -= 1
                messagebox.showinfo('Simulation', 'Simulation has finished')
        else:
            saveGanttChart(self.controller.past_details[self.counter], self.ax, self.canvas)
    
    def back(self):
        if self.counter > 0:
            self.counter -= 1
            saveGanttChart(self.controller.past_details[self.counter], self.ax, self.canvas)

    def changeSchedule(self):
        if self.controller.finished:
            messagebox.showinfo('Simulation', 'Simulation has finished')
            return
        if self.controller.scheduler_name == 'MLFQ':
            for structure in self.controller.scheduler.structure:
                while(structure.peak()):
                    self.controller.queue.push(structure.pop())
        else:
            while(self.controller.scheduler.queue.peak()):
                self.controller.queue.push(self.controller.scheduler.queue.pop())
        if self.controller.scheduler_name in ['SJF', 'Round-Robin']:
            self.controller.waiting_processes = self.controller.scheduler.waiting_processes
        self.controller.prev_details = self.controller.scheduler.details
        self.controller.showFrame(REStartFrame)

    def run(self):
        while self.controller.step():
            continue
        self.counter = len(self.controller.past_details) - 1
        saveGanttChart(self.controller.past_details[self.counter], self.ax, self.canvas)

    def metrics(self):
        if not self.controller.finished:
            messagebox.showinfo('Simulation', 'Simulation has not finished')
            return
        if not self.controller.results:
            self.controller.calculateAllMetrics()
        for process in self.controller.results:
            messagebox.showinfo(process, f"Arrival time: {self.controller.results[process][0]}\nFirst turn in: {self.controller.results[process][1]}\nFinish time: {self.controller.results[process][2]}\nBurst time: {self.controller.results[process][3]}\nWaiting time: {self.controller.results[process][4]}\nResponse time: {self.controller.results[process][5]}\nTurnaround time: {self.controller.results[process][6]}")
    
    def modify(self):
        self.controller.showFrame(ModifyProcessFrame)
    
    def goBack(self):
        self.controller.showFrame(InitialFrame)

    def displayFrame(self):
        # self.controller.past_details.append(image)
        self.frame_ratio = [8, 1]
        # self.photo = ImageTk.PhotoImage(image)

        # Create Frame 1 which will have a photo (using a label as a placeholder here)
        self.frame1 = ttk.Frame(self, borderwidth=2, relief="solid")
        self.frame1.pack(side="left", fill="both", expand=True)

        # Create a label as a placeholder for the photo in Frame 1
        # self.photo_label = ttk.Label(self.frame1, image=self.photo)
        # self.photo_label.pack(fill="both", expand=True)
        # self.photo_label.image = self.photo
        self.fig, self.ax = plt.subplots(figsize=(15, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, 
                                master = self.frame1)   
        saveGanttChart(self.controller.past_details[self.counter], self.ax, self.canvas)
        self.canvas.draw() 
        self.canvas.get_tk_widget().pack() 

        # Create Frame 2 which will have some buttons
        self.frame2 = ttk.Frame(self, borderwidth=2, relief="solid")
        self.frame2.pack(side="right", fill="both", expand=False)

        # Set the width of Frame 2 to be 1/8 of Frame 1
        self.controller.update()  # Force update to calculate sizes
        self.frame1_width = self.controller.winfo_width() * self.frame_ratio[0] / sum(self.frame_ratio)
        self.frame2_width = self.controller.winfo_width() * self.frame_ratio[1] / sum(self.frame_ratio)
        self.frame1.config(width=self.frame1_width)
        self.frame2.config(width=self.frame2_width)

        # Create some buttons in Frame 2
        button1 = ttk.Button(self.frame2, text="Next", command=self.step)
        button1.pack(pady=10)

        button2 = ttk.Button(self.frame2, text="Back", command=self.back)
        button2.pack(pady=10)

        button3 = ttk.Button(self.frame2, text="Change Schedule", command=self.changeSchedule)
        button3.pack(pady=10)

        button4 = ttk.Button(self.frame2, text="Run", command=self.run)
        button4.pack(pady=10)

        button5 = ttk.Button(self.frame2, text="Modify Process", command=self.modify)
        button5.pack(pady=10)

        button6 = ttk.Button(self.frame2, text="Metrics", command=self.metrics)
        button6.pack(pady=10)

        button7 = ttk.Button(self.frame2, text="Return", command=self.goBack)
        button7.pack(pady=10)
        pass

class ModifyProcessFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        
        add_button = ttk.Button(self, text="Add",
                                    command=lambda: self.goToAddFrame(controller))
        add_button.pack(pady=10, padx=10)
        
        remove_button = ttk.Button(self, text="Remove",
                                    command=lambda: self.goToRemoveFrame(controller))
        remove_button.pack(pady=10, padx=10)

    def goToAddFrame(self, controller) -> None:
        controller.showFrame(REProcessConfigFrame)

    def goToRemoveFrame(self, controller) -> None:
        controller.frames[RemoveProcesses].start()
        controller.showFrame(RemoveProcesses)

class REStartFrame(tk.Frame):
    """Class for the StartFrame.

    This class represents a frame in the scheduler application, specifically for startframe.
    """
    def __init__(self, parent, controller) -> None:
        """Initialize the StartFrame frame.

        Sets up the UI elements and functionality specific to the startframe.
        """
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Choose the scheduling algorithm")
        label.pack(pady=10, padx=10)

        # Dropdown menu for scheduling algorithms
        self.algorithm = tk.StringVar()
        self.algorithm.set("FCFS") # default value
        dropdown = ttk.Combobox(self, textvariable=self.algorithm, 
                                values=["FCFS", "SJF", "SRTF", "Round-Robin", "MLFQ", "Lottery"])
        dropdown.pack(pady=10, padx=10)

        # Button to proceed to the corresponding frame
        proceed_button = ttk.Button(self, text="Proceed",
                                    command=lambda: self.goToFrame(controller))
        proceed_button.pack(pady=10, padx=10)

    def goToFrame(self, controller) -> None:
            selection = self.algorithm.get()
            if selection == "FCFS":
                controller.scheduler_name = "FCFS"
                controller.showFrame(FinalFrame)
                controller.reSetupScheduler()
            elif selection == "SJF":
                controller.scheduler_name = "SJF"
                controller.showFrame(FinalFrame)
                controller.reSetupScheduler()
            elif selection == "SRTF":
                controller.scheduler_name = "SRTF"
                controller.showFrame(FinalFrame)
                controller.reSetupScheduler()
            elif selection == "Round-Robin":
                controller.scheduler_name = "Round-Robin"
                controller.showFrame(RERoundRobinFrame)
            elif selection == "MLFQ":
                controller.scheduler_name = "MLFQ"
                controller.showFrame(REMLFQFrame)
                messagebox.showinfo("MLFQ", "If you do not want boosting, do not put a value in the boost time box")
            elif selection == "Lottery":
                controller.scheduler_name = "Lottery"
                controller.showFrame(RELotteryFrame)

class RERoundRobinFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        quanta_label = tk.Label(self, text="Quantum size")
        quanta_label.pack(pady=10, padx=10)

        self.quantum = tk.Entry(self)
        self.quantum.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        try:
            self.controller.configurations["quantum"] = int(self.quantum.get())
            self.controller.process_data = getProcessData(self.controller.processes)
            self.controller.showFrame(FinalFrame)
            self.controller.reSetupScheduler()
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class REMLFQFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Choose Pre-emption")
        label.pack(pady=10, padx=10)

        self.preemption = tk.StringVar()
        self.preemption.set("Pre-emptive")  # default value
        self.dropdown = ttk.Combobox(self, textvariable=self.preemption,
                                values=["Pre-emptive", "Non-pre-emptive"])
        self.dropdown.pack(pady=10, padx=10)

        levels_label = tk.Label(self, text="Number of levels")
        levels_label.pack(pady=10, padx=10)
                        
        self.num_levels_entry = tk.Entry(self)
        self.num_levels_entry.pack(pady=10, padx=10)

        boost_label = tk.Label(self, text="Boost time")
        boost_label.pack(pady=10, padx=10)

        self.boost_entry = tk.Entry(self)
        self.boost_entry.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        try:
            if (self.boost_entry.get()):
                boost_time = int(self.boost_entry.get())
            else:
                boost_time = 1000000
            self.controller.configurations["boost_time"] = boost_time
            self.controller.configurations["pre-emptive"] = self.dropdown.get() == "pre-emptive"
            self.controller.frames[REMLFQConfigFrame].num_levels = int(self.num_levels_entry.get())
            self.controller.frames[REMLFQConfigFrame].createLevelFrames()
            self.controller.showFrame(REMLFQConfigFrame)
            messagebox.showinfo("MLFQ", "If you choose FCFS, you do not need to put the quantum size")
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class RELotteryFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Choose Pre-emption")
        label.pack(pady=10, padx=10)

        self.preemption = tk.StringVar()
        self.preemption.set("Pre-emptive")  # default value
        dropdown = ttk.Combobox(self, textvariable=self.preemption,
                                values=["Pre-emptive", "Non-pre-emptive"])
        dropdown.pack(pady=10, padx=10)

        quanta_label = tk.Label(self, text="Quanta size")
        quanta_label.pack(pady=10, padx=10)

        self.quantum = tk.Entry(self)
        self.quantum.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        self.controller.showFrame(FinalFrame)
        self.controller.reSetupScheduler()


class REMLFQConfigFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.current_level = 0  # New attribute to track the current level
        self.currentLevelIndex = 0
        self.level_frames = []
        self.levels = []
        self.quanta = []

        # Button to show the next process
        self.next_level_button = ttk.Button(self, text="Next Process", command=self.showNextLevel)

        # Button to proceed after all processes are entered
        self.proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)

    def showNextLevel(self) -> None:
        try:
            if self.level_frames[self.currentLevelIndex][1].get() == "Round-Robin":
                self.levels.append(Queue())
                self.quanta.append(int(self.level_frames[self.currentLevelIndex][2].get()))
            else:
                self.levels.append(Queue())
                self.quanta.append(100000)
            # Hide the current process frame
            self.level_frames[self.currentLevelIndex][0].pack_forget()
            self.next_level_button.pack_forget()
            # Move to the next process
            self.currentLevelIndex = (self.currentLevelIndex + 1)

            # Show the next process frame
            self.level_frames[self.currentLevelIndex][0].pack(fill="both", expand=True, padx=10, pady=5)
            if self.currentLevelIndex == self.num_levels - 1:
                self.next_level_button.pack_forget()
                self.proceed_button.pack(pady=10)
            else:
                self.next_level_button.pack(pady=10)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

    def createLevelFrames(self) -> None:
        for level in range(self.num_levels):
            level_frame = tk.LabelFrame(self, text=f"Level {level + 1} Configuration")
            level_frame.pack(fill="both", expand=True, padx=10, pady=5)

            type_label = tk.Label(level_frame, text="Choose Type:")
            type_label.pack(side="left", padx=5)

            type_var = tk.StringVar()
            type_var.set("Round-robin")  # default value
            type_dropdown = ttk.Combobox(level_frame, textvariable=type_var,
                                         values=["Round-Robin", "FCFS"])
            type_dropdown.pack(side="left", padx=5)

            quanta_label = tk.Label(level_frame, text="Quanta size:")
            quanta_label.pack(side="left", padx=5)

            quanta_entry = tk.Entry(level_frame)
            quanta_entry.pack(side="left", padx=5)

            self.level_frames.append((level_frame, type_dropdown, quanta_entry))
            level_frame.pack_forget()  # Initially hide all frames
        # Show the first level
        self.level_frames[0][0].pack(fill="both", expand=True, padx=10, pady=5)
        self.next_level_button.pack(pady=10)

    def proceed(self) -> None:
        try:
            if self.level_frames[self.currentLevelIndex][1].get() == "Round-Robin":
                self.levels.append(Queue())
                self.quanta.append(int(self.level_frames[self.currentLevelIndex][2].get()))
            else:
                self.levels.append(Queue())
                self.quanta.append(100000)
            self.controller.configurations["quanta"] = self.quanta
            self.controller.configurations["structure"] = self.levels
            self.controller.showFrame(FinalFrame)
            self.controller.reSetupScheduler()
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class REProcessConfigFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.num_processes = 30

        label = tk.Label(self, text="Number of processes")
        label.pack(pady=10, padx=10)

        self.num_processes_entry = tk.Entry(self)
        self.num_processes_entry.pack(pady=10, padx=10)

        process_creation_label = tk.Label(self, text="Process Creation")
        process_creation_label.pack(pady=10, padx=10)

        self.process_creation = tk.StringVar()
        self.process_creation.set("Random")  # default value
        self.process_creation_dropdown = ttk.Combobox(self, textvariable=self.process_creation,
                                                 values=["Custom", "Random"])
        self.process_creation_dropdown.pack(pady=10, padx=10)

        self.proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        self.proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        try:
            if self.process_creation_dropdown.get() == "Custom":
                self.controller.frames[RECustomProcessCreationFrame].num_processes = int(self.num_processes_entry.get())
                self.controller.frames[RECustomProcessCreationFrame].createProcessFrames()
                self.controller.showFrame(RECustomProcessCreationFrame)
            else:
                processes = initializeProcessStack(min_arrival_time=self.controller.time_step + 1, max_arrival_time=self.controller.time_step + 30, num_processes=int(self.num_processes_entry.get()))
                for process in processes.items:
                    self.controller.scheduler.process_stack.items.append(process)
                self.controller.scheduler.process_stack.sort()
                details = getProcessData(processes)
                for data in details:
                    self.controller.process_data[data] = details[data]
                self.controller.showFrame(FinalFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")


class RECustomProcessCreationFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.num_processes = self.controller.frames[ProcessConfigFrame].num_processes
        self.current_process_index = 0
        self.process_frames = []
        self.next_process_button = ttk.Button(self, text="Next Process", command=self.showNextProcess)
        self.proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        self.processes = Stack()

    def createProcessFrames(self) -> None:
        for process_num in range(self.num_processes):
            process_frame = tk.LabelFrame(self, text=f"Process #{process_num + 1}")
            process_frame.pack(fill="both", expand=True, padx=10, pady=5)

            arrival_label = tk.Label(process_frame, text="Arrival time:")
            arrival_label.pack(side="left", padx=5)
            arrival_entry = tk.Entry(process_frame)
            arrival_entry.pack(side="left", padx=5)

            burst_label = tk.Label(process_frame, text="Burst time:")
            burst_label.pack(side="left", padx=5)
            burst_entry = tk.Entry(process_frame)
            burst_entry.pack(side="left", padx=5)

            self.process_frames.append((process_frame, arrival_entry, burst_entry))
            process_frame.pack_forget()  # Initially hide the frame

            # Show only the first process frame initially
        self.process_frames[0][0].pack(fill="both", expand=True, padx=10, pady=5)
        if self.num_processes > 1:
            self.next_process_button.pack(pady=10)
        else:
            self.proceed_button.pack(pady=10)

    def showNextProcess(self) -> None:
        try:
            arrival_time =  int(self.process_frames[self.current_process_index][1].get())
            if arrival_time < self.controller.time_step:
                messagebox.showerror("Incorrect Input", f"Arrival time should be more than or equal {self.controller.time_step}")
                return
            # Hide the current process frame
            self.process_frames[self.current_process_index][0].pack_forget()
            self.next_process_button.pack_forget()
            process = Process(arrival_time=arrival_time,
                                                    duration=int(self.process_frames[self.current_process_index][2].get()))
            self.controller.scheduler.process_stack.push(process)
            self.processes.push(process)
            # Move to the next process
            self.current_process_index = (self.current_process_index + 1)

            # Show the next process frame
            self.process_frames[self.current_process_index][0].pack(fill="both", expand=True, padx=10, pady=5)
            if self.current_process_index == self.num_processes - 1:
                self.next_process_button.pack_forget()
                self.proceed_button.pack(pady=10)
            else:
                self.next_process_button.pack(pady=10)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

    def proceed(self) -> None:
        try:
            process = Process(arrival_time=int(self.process_frames[self.current_process_index][1].get()),
                                        duration=int(self.process_frames[self.current_process_index][2].get()))
            self.controller.scheduler.process_stack.push(process)
            self.processes.push(process)
            self.controller.scheduler.process_stack.sort()
            details = getProcessData(self.processes)
            for data in details:
                self.controller.process_data[data] = details[data]
            self.controller.showFrame(FinalFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class RemoveProcesses(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.names = []

    def start(self):
        self.process_stack = self.controller.scheduler.process_stack.items
        for process in self.process_stack:
            self.names.append(process.name)
        self.selected_name = tk.StringVar()
        self.build_radio_buttons()

    def build_radio_buttons(self):
        # Clear existing radio buttons
        for widget in self.winfo_children():
            widget.destroy()

        # Create labels and radio buttons for each name
        for name in self.names:
            # Create a radio button for the name
            radio_button = ttk.Radiobutton(self, text=name, variable=self.selected_name, value=name)
            radio_button.pack(pady=10)
        
        remove_button = ttk.Button(self, text="Remove Selected Name", command=self.remove_name)
        remove_button.pack(pady=10)
        
        proceed_button = ttk.Button(self, text="Proceed", command=self.proceed)
        proceed_button.pack(pady=10)

    def remove_name(self):
        # Remove the selected name from the list and rebuild radio buttons
        try:
            self.names.remove(self.selected_name.get())
            for i in range(len(self.process_stack)):
                if self.process_stack[i].name == self.selected_name.get():
                    del self.process_stack[i]
                    break
            self.build_radio_buttons()
        except ValueError:
            messagebox.showerror("Error", "No more proceses left")
    
    def proceed(self):
        self.controller.showFrame(FinalFrame)
        self.controller.scheduler.process_stack.items = self.process_stack
        self.controller.scheduler.process_stack.sort()

class SCStartFrame(tk.Frame):
    """Class for the StartFrame.

    This class represents a frame in the scheduler application, specifically for startframe.
    """
    def __init__(self, parent, controller) -> None:
        """Initialize the StartFrame frame.

        Sets up the UI elements and functionality specific to the startframe.
        """
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Choose the scheduling algorithm")
        label.pack(pady=10, padx=10)

        # Dropdown menu for scheduling algorithms
        self.algorithm = tk.StringVar()
        self.algorithm.set("FCFS") # default value
        dropdown = ttk.Combobox(self, textvariable=self.algorithm, 
                                values=["FCFS", "SJF", "SRTF", "Round-Robin", "MLFQ"])
        dropdown.pack(pady=10, padx=10)

        # Button to proceed to the corresponding frame
        add_button = ttk.Button(self, text="Add",
                                    command=lambda: self.goToFrame(controller))
        add_button.pack(pady=10, padx=10)

        # Button to proceed to the corresponding frame
        proceed_button = ttk.Button(self, text="Proceed",
                                    command=lambda: self.proceed(controller))
        proceed_button.pack(pady=10, padx=10)

    def goToFrame(self, controller) -> None:
            selection = self.algorithm.get()
            if selection == "FCFS":
                stack = customProcessStack()
                controller.schedulers.append(FCFS(stack))
                controller.showFrame(SCStartFrame)
            elif selection == "SJF":
                stack = customProcessStack()
                controller.schedulers.append(SJF(stack))
                controller.showFrame(SCStartFrame)
            elif selection == "SRTF":
                stack = customProcessStack()
                stack.items = controller.processes.items.copy()
                controller.schedulers.append(SRTF(stack))
                controller.showFrame(SCStartFrame)
            elif selection == "Round-Robin":
                controller.showFrame(SCRoundRobinFrame)
            elif selection == "MLFQ":
                controller.showFrame(SCMLFQFrame)
                messagebox.showinfo("MLFQ", "If you do not want boosting, do not put a value in the boost time box")
    
    def proceed(self, controller):
        controller.computePerformance()
        controller.frames[SCFinalFrame].displayFrame()
        controller.showFrame(SCFinalFrame)

class SCRoundRobinFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        quanta_label = tk.Label(self, text="Quantum size")
        quanta_label.pack(pady=10, padx=10)

        self.quantum = tk.Entry(self)
        self.quantum.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        try:
            stack = customProcessStack()
            self.controller.schedulers.append(RoundRobin(stack, int(self.quantum.get())))
            self.controller.showFrame(SCStartFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class SCMLFQFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Choose Pre-emption")
        label.pack(pady=10, padx=10)

        self.preemption = tk.StringVar()
        self.preemption.set("Pre-emptive")  # default value
        self.dropdown = ttk.Combobox(self, textvariable=self.preemption,
                                values=["Pre-emptive", "Non-pre-emptive"])
        self.dropdown.pack(pady=10, padx=10)

        levels_label = tk.Label(self, text="Number of levels")
        levels_label.pack(pady=10, padx=10)
                        
        self.num_levels_entry = tk.Entry(self)
        self.num_levels_entry.pack(pady=10, padx=10)

        boost_label = tk.Label(self, text="Boost time")
        boost_label.pack(pady=10, padx=10)

        self.boost_entry = tk.Entry(self)
        self.boost_entry.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        try:
            if (self.boost_entry.get()):
                boost_time = int(self.boost_entry.get())
            else:
                boost_time = 1000000
            self.boost_time =  boost_time
            self.pre_emptive = self.dropdown.get() == "pre-emptive"
            self.controller.frames[SCMLFQConfigFrame].num_levels = int(self.num_levels_entry.get())
            self.controller.frames[SCMLFQConfigFrame].createLevelFrames()
            self.controller.showFrame(SCMLFQConfigFrame)
            messagebox.showinfo("MLFQ", "If you choose FCFS, you do not need to put the quantum size")
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class SCMLFQConfigFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.current_level = 0  # New attribute to track the current level
        self.currentLevelIndex = 0
        self.level_frames = []
        self.levels = []
        self.quanta = []

        # Button to show the next process
        self.next_level_button = ttk.Button(self, text="Next Process", command=self.showNextLevel)

        # Button to proceed after all processes are entered
        self.proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)

    def showNextLevel(self) -> None:
        try:
            if self.level_frames[self.currentLevelIndex][1].get() == "Round-Robin":
                self.levels.append(Queue())
                self.quanta.append(int(self.level_frames[self.currentLevelIndex][2].get()))
            else:
                self.levels.append(Queue())
                self.quanta.append(100000)
            # Hide the current process frame
            self.level_frames[self.currentLevelIndex][0].pack_forget()
            self.next_level_button.pack_forget()
            # Move to the next process
            self.currentLevelIndex = (self.currentLevelIndex + 1)

            # Show the next process frame
            self.level_frames[self.currentLevelIndex][0].pack(fill="both", expand=True, padx=10, pady=5)
            if self.currentLevelIndex == self.num_levels - 1:
                self.next_level_button.pack_forget()
                self.proceed_button.pack(pady=10)
            else:
                self.next_level_button.pack(pady=10)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

    def createLevelFrames(self) -> None:
        for level in range(self.num_levels):
            level_frame = tk.LabelFrame(self, text=f"Level {level + 1} Configuration")
            level_frame.pack(fill="both", expand=True, padx=10, pady=5)

            type_label = tk.Label(level_frame, text="Choose Type:")
            type_label.pack(side="left", padx=5)

            type_var = tk.StringVar()
            type_var.set("Round-robin")  # default value
            type_dropdown = ttk.Combobox(level_frame, textvariable=type_var,
                                         values=["Round-Robin", "FCFS"])
            type_dropdown.pack(side="left", padx=5)

            quanta_label = tk.Label(level_frame, text="Quanta size:")
            quanta_label.pack(side="left", padx=5)

            quanta_entry = tk.Entry(level_frame)
            quanta_entry.pack(side="left", padx=5)

            self.level_frames.append((level_frame, type_dropdown, quanta_entry))
            level_frame.pack_forget()  # Initially hide all frames
        # Show the first level
        self.level_frames[0][0].pack(fill="both", expand=True, padx=10, pady=5)
        self.next_level_button.pack(pady=10)

    def proceed(self) -> None:
        try:
            if self.level_frames[self.currentLevelIndex][1].get() == "Round-Robin":
                self.levels.append(Queue())
                self.quanta.append(int(self.level_frames[self.currentLevelIndex][2].get()))
            else:
                self.levels.append(Queue())
                self.quanta.append(100000)
            stack = customProcessStack()
            self.controller.schedulers.append(MLFQ(stack,
                                                quanta=self.quanta, structure=self.levels,
                                                pre_emptive=self.controller.frames[SCMLFQFrame].pre_emptive,
                                                boost_time=self.controller.frames[SCMLFQFrame].boost_time))
            self.controller.showFrame(SCStartFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class SCFinalFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def back(self):
        pass

    def displayFrame(self):
        # self.controller.past_details.append(image)
        self.frame_ratio = [8, 1]
        # self.photo = ImageTk.PhotoImage(image)

        # Create Frame 1 which will have a photo (using a label as a placeholder here)
        self.frame1 = ttk.Frame(self, borderwidth=2, relief="solid")
        self.frame1.pack(side="left", fill="both", expand=True)

        # Create a label as a placeholder for the photo in Frame 1
        # self.photo_label = ttk.Label(self.frame1, image=self.photo)
        # self.photo_label.pack(fill="both", expand=True)
        # self.photo_label.image = self.photo
        self.fig, self.ax = plt.subplots(figsize=(15, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, 
                                master = self.frame1)   
        savePerformancePlot(self.controller.scheduler_names, self.controller.average_waiting_times, self.controller.average_response_times, self.ax, self.canvas)
        self.canvas.draw() 
        self.canvas.get_tk_widget().pack() 

        # Create Frame 2 which will have some buttons
        self.frame2 = ttk.Frame(self, borderwidth=2, relief="solid")
        self.frame2.pack(side="right", fill="both", expand=False)

        # Set the width of Frame 2 to be 1/8 of Frame 1
        self.controller.update()  # Force update to calculate sizes
        self.frame1_width = self.controller.winfo_width() * self.frame_ratio[0] / sum(self.frame_ratio)
        self.frame2_width = self.controller.winfo_width() * self.frame_ratio[1] / sum(self.frame_ratio)
        self.frame1.config(width=self.frame1_width)
        self.frame2.config(width=self.frame2_width)

        # Create some buttons in Frame 2
        button1 = ttk.Button(self.frame2, text="Return", command=self.back)
        button1.pack(pady=10)
        pass

def customProcessStack():
    stack = Stack()
    stack.push(Process(1, 14, name='P0'))
    stack.push(Process(48, 21, name='P1'))
    stack.push(Process(18, 14, name='P2'))
    stack.push(Process(16, 17, name='P3'))
    stack.push(Process(42, 1, name='P4'))
    stack.push(Process(47, 8, name='P5'))
    stack.push(Process(11, 13, name='P6'))
    stack.push(Process(8, 6, name='P7'))
    stack.push(Process(18, 3, name='P8'))
    stack.push(Process(35, 2, name='P9'))
    stack.push(Process(29, 4, name='P10'))
    stack.push(Process(0, 15, name='P11'))
    stack.push(Process(48, 12, name='P12'))
    stack.push(Process(4, 6, name='P13'))
    stack.push(Process(26, 17, name='P14'))
    stack.push(Process(23, 21, name='P15'))
    stack.push(Process(51, 3, name='P16'))
    stack.push(Process(38, 8, name='P17'))
    stack.push(Process(0, 20, name='P18'))
    stack.push(Process(28, 8, name='P19'))
    stack.push(Process(14, 18, name='P20'))
    stack.push(Process(7, 14, name='P21'))
    stack.push(Process(31, 14, name='P22'))
    stack.push(Process(18, 21, name='P23'))
    stack.push(Process(48, 19, name='P24'))
    stack.push(Process(16, 10, name='P25'))
    stack.push(Process(30, 14, name='P26'))
    stack.push(Process(27, 21, name='P27'))
    stack.push(Process(50, 13, name='P28'))
    stack.push(Process(36, 3, name='P29'))
    stack.push(Process(10, 21, name='P30'))
    stack.push(Process(25, 13, name='P31'))
    stack.push(Process(7, 14, name='P32'))
    stack.push(Process(11, 11, name='P33'))
    stack.push(Process(9, 20, name='P34'))
    stack.push(Process(40, 8, name='P35'))
    stack.push(Process(9, 11, name='P36'))
    stack.push(Process(20, 18, name='P37'))
    stack.push(Process(8, 4, name='P38'))
    stack.push(Process(14, 2, name='P39'))
    stack.push(Process(33, 20, name='P40'))
    stack.push(Process(0, 19, name='P41'))
    stack.push(Process(30, 13, name='P42'))
    stack.push(Process(35, 19, name='P43'))
    stack.push(Process(11, 10, name='P44'))
    stack.push(Process(49, 17, name='P45'))
    stack.push(Process(0, 11, name='P46'))
    stack.push(Process(15, 17, name='P47'))
    stack.push(Process(1, 11, name='P48'))
    stack.push(Process(1, 13, name='P49'))
    stack.push(Process(30, 15, name='P50'))
    stack.push(Process(38, 12, name='P51'))
    stack.push(Process(48, 17, name='P52'))
    stack.push(Process(26, 4, name='P53'))
    stack.push(Process(33, 20, name='P54'))
    stack.push(Process(40, 2, name='P55'))
    stack.push(Process(48, 18, name='P56'))
    stack.push(Process(19, 3, name='P57'))
    stack.push(Process(38, 14, name='P58'))
    stack.push(Process(0, 15, name='P59'))
    stack.push(Process(48, 3, name='P60'))
    stack.push(Process(14, 18, name='P61'))
    stack.push(Process(15, 19, name='P62'))
    stack.push(Process(39, 8, name='P63'))
    stack.push(Process(45, 12, name='P64'))
    stack.push(Process(11, 6, name='P65'))
    stack.push(Process(34, 20, name='P66'))
    stack.push(Process(39, 2, name='P67'))
    stack.push(Process(14, 9, name='P68'))
    stack.push(Process(38, 17, name='P69'))
    stack.push(Process(44, 13, name='P70'))
    stack.push(Process(0, 10, name='P71'))
    stack.push(Process(1, 9, name='P72'))
    stack.push(Process(31, 15, name='P73'))
    stack.push(Process(37, 3, name='P74'))
    stack.push(Process(11, 4, name='P75'))
    stack.push(Process(39, 12, name='P76'))
    stack.push(Process(12, 13, name='P77'))
    stack.push(Process(13, 2, name='P78'))
    stack.push(Process(8, 7, name='P79'))
    stack.push(Process(27, 13, name='P80'))
    stack.push(Process(27, 9, name='P81'))
    stack.push(Process(21, 21, name='P82'))
    stack.push(Process(47, 18, name='P83'))
    stack.push(Process(15, 17, name='P84'))
    stack.push(Process(42, 7, name='P85'))
    stack.push(Process(17, 12, name='P86'))
    stack.push(Process(27, 3, name='P87'))
    stack.push(Process(23, 10, name='P88'))
    stack.push(Process(21, 12, name='P89'))
    stack.push(Process(3, 17, name='P90'))
    stack.push(Process(51, 6, name='P91'))
    stack.push(Process(10, 2, name='P92'))
    stack.push(Process(18, 1, name='P93'))
    stack.push(Process(48, 15, name='P94'))
    stack.push(Process(33, 7, name='P95'))
    stack.push(Process(50, 3, name='P96'))
    stack.push(Process(13, 15, name='P97'))
    stack.push(Process(32, 3, name='P98'))
    stack.push(Process(7, 1, name='P99'))
    stack.sort()
    return stack

app = SchedulerApp()
app.mainloop()
