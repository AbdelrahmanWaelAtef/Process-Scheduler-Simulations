import random


class RoundRobin:
    def __init__(self, num_processes, quantum):
        self.processes = [i + 1 for i in range(num_processes)]
        self.burst_time = [random.randint(1, 10) for _ in range(num_processes)]
        self.quantum = quantum
        self.n = len(self.processes)
        self.rem_bt = [0] * self.n
        self.wt = [0] * self.n
        self.tat = [0] * self.n

    def schedule(self):
        for i in range(self.n):
            self.rem_bt[i] = self.burst_time[i]
        t = 0
        while True:
            done = True
            for i in range(self.n):
                if self.rem_bt[i] > 0:
                    done = False
                    if self.rem_bt[i] > self.quantum:
                        t += self.quantum
                        self.rem_bt[i] -= self.quantum
                    else:
                        t = t + self.rem_bt[i]
                        self.wt[i] = t - self.burst_time[i]
                        self.rem_bt[i] = 0
            if done:
                break

    def print_times(self):
        total_wt = 0
        total_tat = 0
        for i in range(self.n):
            total_wt = total_wt + self.wt[i]
            total_tat = total_tat + self.tat[i]
            print(" " + str(i + 1) + "\t\t" + str(self.burst_time[i]) + "\t " + str(self.wt[i]) + "\t\t " + str(
                self.tat[i]))
        print("\nAverage waiting time = %.5f " % (total_wt / self.n))
        print("Average turn around time = %.5f " % (total_tat / self.n))


num_processes = 3
quantum = 2
rr = RoundRobin(num_processes, quantum)
rr.schedule()
rr.print_times()
