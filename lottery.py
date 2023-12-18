# lottery scheduling method implementation using python
import random
import time
from process_with_tickets import Process_t


class lottery_scheduling:
    # max tickets doesn't matter here. it will be calculated from the generated processes
    def __init__(self, num_processes: int, max_tickets: int, chance_of_dependence: float, max_tickets_per_process: int, max_time: int):
        self.num_processes = num_processes
        self.max_tickets = max_tickets
        self.chance_of_dependence = chance_of_dependence
        self.max_tickets_per_process = max_tickets_per_process
        self.max_time = max_time
        self.processes = []


    def initialize_processes(self):
        new_max_tickets = 0
        for i in range(self.num_processes):
            tickets = random.randint(1, self.max_tickets_per_process)
            new_max_tickets += tickets
            self.processes.append(Process_t(arrival_time=random.randint(0,self.max_time-1), duration=random.randint(1,7), probability_io=0.1 if random.random()<0.15 else 0, depends_on = -1 if i == 0 or random.random()>self.chance_of_dependence else random.randint(0, i-1), ticket_count=tickets))
        self.max_tickets = new_max_tickets
        self.processes.sort(key=lambda p: p.arrival_time)



if __name__ == '__main__':
    scheduler = lottery_scheduling(num_processes=20, max_tickets=200, chance_of_dependence=0.2, max_tickets_per_process=50, max_time=100)

    scheduler.initialize_processes()
    print(f'Process\tArrival Time\tDuration\tDepends On?\tprob_io\ttickets')
    for i in scheduler.processes:

        print(f'{i.pid}\t\t{i.arrival_time}\t\t\t\t{i.duration}\t\t\t{(i.depends_on if(i.depends_on) > -1 else "no")}\t\t\t{i.probability_io}\t\t{i.ticket_count}')
    print('ticket count =', scheduler.max_tickets)

    process_list_arrival_time  = [i.arrival_time for i in scheduler.processes]
    print('arrival times:', process_list_arrival_time)
    process_list = [i for i in scheduler.processes]
    j = 0
    current_max_tickets = 1
    sc_time = ''
    sc_winning_ticket = ''
    sc_result = ''
    # arrived_processes = []
    print('time\tticket\trunning')
    for i in range(scheduler.max_time):
        scheduler_winning_ticket = 1 if current_max_tickets == 1  else random.randint(1, current_max_tickets)
        sc_time = f'{i}\t\t'
        sc_winning_ticket = f'{scheduler_winning_ticket}\t\t'
        # sc_result += f'{process_list[j].name}\t'
        while (i == process_list_arrival_time[j]):
            current_max_tickets += process_list[j].ticket_count
            j += 1
        
        compounded_ticket_count = 0
        for k in range(j):
                compounded_ticket_count += process_list[k].ticket_count
                if scheduler_winning_ticket <= compounded_ticket_count:
                    sc_result = f'{process_list[k].name}'
                    # process_list[k].state = Process_t.ProcessState.RUNNING
                    process_list[k].duration -= 1
                    if process_list[k].duration == 0:
                        j -= 1
                        current_max_tickets -= process_list[k].ticket_count
                        process_list.pop(k)
                        process_list_arrival_time.pop(k)
                    break


        # print(f'time:\t\t{sc_time}\nticket:\t\t{sc_winning_ticket}\nrunning:\t{sc_result}', end='\r')
        # print(f'\rtime:\t\t{sc_time}\n', end='\r')
        # print(f'\rticket:\t\t{sc_winning_ticket}\n', end='\r')
        # print(f'\rrunning:\t{sc_result}\n', end='\r')
        print(f'{sc_time}{sc_winning_ticket}{sc_result}')
        time.sleep(0.5)
