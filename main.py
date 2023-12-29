import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from queue_ import Queue
from priority_queue import PriorityQueue
from utils import *
from mlfq import MLFQ
from sjf import SJF
from fcfs import FCFS

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

        # Initialize a dictionary to hold the frames
        self.frames = {}

        self.scheduler_name = ""
        self.configurations = dict()
        self.processes = Stack()

        self.processes_IO = None

        # Iterate over the frame classes and add them to the container
        for F in (StartFrame, RoundRobinFrame, ProcessConfigFrame,
                  MLFQFrame, MLFQConfigFrame, LotteryFrame,
                  CustomProcessConfigFrame, CustomProcessCreationFrame,
                  CustomProcessCreationFrameTickets, FinalFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Display the initial frame
        self.showFrame(StartFrame)

    def showFrame(self, cont) -> None:
        """Show a specified frame in the application.

        Args:
            cont (class): The class of the frame to be displayed.
        """
        # Raise the selected frame to the top
        frame = self.frames[cont]
        frame.tkraise()

        # Special handling for EncodeDecodeSelection frame
        if cont == CustomProcessConfigFrame or cont == ProcessConfigFrame:
            self.geometry("400x230")  # Set a custom size that fits the contents of this frame
        elif cont == LotteryFrame or cont == RoundRobinFrame:
            self.geometry("400x250")
        elif cont == MLFQFrame:
            self.geometry("400x320")
        elif cont == MLFQConfigFrame:
            self.geometry("800x200")
        elif cont == CustomProcessCreationFrame and self.processes_IO == "Pattern":
            self.geometry("1000x200")
        elif cont == CustomProcessCreationFrame:
            self.geometry("700x200")
        elif cont == CustomProcessCreationFrameTickets:
            self.geometry("820x200")
        elif cont == FinalFrame:
            self.geometry(f"400x50")
        else:
            self.geometry("400x150") # Resize window to fit the frame

    def runSchedule(self):
        if self.scheduler_name == "MLFQ":
            self.scheduler = MLFQ(process_stack=self.processes,
                                    boost_time=self.configurations["boost_time"],
                                    pre_emptive=self.configurations["pre-emptive"],
                                    quanta=self.configurations["quanta"],
                                    structure=self.configurations["structure"])
            self.process_data = getProcessData(self.processes)
            self.details = self.scheduler.run()
            self.results = calculateMetrics(self.details["state"], self.process_data)
 
        if self.scheduler_name == "SJF":
                    self.scheduler = SJF(process_stack=self.processes)
                    self.process_data = getProcessData(self.processes)
                    self.details = self.scheduler.run()
                    self.results = calculateMetrics(self.details["state"], self.process_data)
        if self.scheduler_name == "FCFS":
                    self.scheduler = FCFS(process_stack=self.processes)
                    self.process_data = getProcessData(self.processes)
                    self.details = self.scheduler.run()
                    self.results = calculateMetrics(self.details["state"], self.process_data)           

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
        label = tk.Label(self, text="Choose Pre-emption")
        label.pack(pady=10, padx=10)

        self.preemption = tk.StringVar()
        self.preemption.set("Pre-emptive")  # default value
        dropdown = ttk.Combobox(self, textvariable=self.preemption,
                                values=["Pre-emptive", "Non-pre-emptive"])
        dropdown.pack(pady=10, padx=10)

        quanta_label = tk.Label(self, text="Quanta size")
        quanta_label.pack(pady=10, padx=10)

        self.quanta_size = tk.Entry(self)
        self.quanta_size.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
        self.controller.showFrame(ProcessConfigFrame)


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
                self.controller.runSchedule()
                self.controller.frames[FinalFrame].displayDetails()
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
            self.controller.configurations["pre-emptive"] = self.dropdown.get() == "pre-emptive"
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
        dropdown = ttk.Combobox(self, textvariable=self.preemption,
                                values=["Pre-emptive", "Non-pre-emptive"])
        dropdown.pack(pady=10, padx=10)

        quanta_label = tk.Label(self, text="Quanta size")
        quanta_label.pack(pady=10, padx=10)

        self.quanta_size = tk.Entry(self)
        self.quanta_size.pack(pady=10, padx=10)

        proceed_button = ttk.Button(self, text="Proceed",
                                    command=self.proceed)
        proceed_button.pack(pady=10, padx=10)

    def proceed(self) -> None:
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
                self.controller.frames[CustomProcessCreationFrame].num_processes = int(self.num_processes_entry.get())
                self.controller.frames[CustomProcessCreationFrame].createProcessFrames()
                self.controller.showFrame(CustomProcessCreationFrame)
            else:
                self.controller.processes = initializeProcessStack(int(self.num_processes_entry.get()), max_tickets=100, depends_on_probability=0.01)
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
        self.io_type = self.controller.processes_IO
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
        self.next_process_button.pack(pady=10)

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
            self.controller.runSchedule()
            self.controller.frames[FinalFrame].displayDetails()
            self.controller.showFrame(FinalFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")
        
class CustomProcessCreationFrameTickets(tk.Frame):
    def __init__(self, parent, controller) -> None:  # Assuming defaults for demonstration
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.process_frames = []
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

            label = tk.Label(self, text="Depends on")
            label.pack(pady=10, padx=10)

            depends_on_entry = tk.Entry(process_frame)
            depends_on_entry.pack(side="left", padx=5)

            self.process_frames.append((process_frame, arrival_entry, burst_entry, tickets_entry, depends_on_entry))
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
                                            tickets=int(self.process_frames[self.current_process_index][3].get())),
                                            depends_on=self.controller.processes.searchForProcess(self.process_frames[self.current_process_index][4].get()))

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
                                            tickets=int(self.process_frames[self.current_process_index][3].get())),
                                            depends_on=self.controller.processes.searchForProcess(self.process_frames[self.current_process_index][4].get()))
            self.controller.processes.sort()
            self.controller.runSchedule()
            self.controller.frames[FinalFrame].displayDetails()
            self.controller.showFrame(FinalFrame)
        except:
            messagebox.showerror("Incorrect Input", "Please enter valid inputs")

class FinalFrame(tk.Frame):
    def __init__(self, parent, controller) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def displayGanttChart(self) -> None:
        plotGanttChart(self.controller.details)

    def displayDetails(self) -> None:
        for process in self.controller.results:
            messagebox.showinfo(process, f"Arrival time: {self.controller.results[process][0]}\nFirst turn in: {self.controller.results[process][1]}\nFinish time: {self.controller.results[process][2]}\nBurst time: {self.controller.results[process][3]}\nWaiting time: {self.controller.results[process][4]}\nResponse time: {self.controller.results[process][5]}\nTurnaround time: {self.controller.results[process][6]}")
        gantt_chart_button = ttk.Button(self, text="Display Gantt Chart",
                                        command=self.displayGanttChart)
        gantt_chart_button.pack(pady=10)


app = SchedulerApp()
app.mainloop()
