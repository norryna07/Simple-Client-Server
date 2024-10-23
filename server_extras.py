import queue
import threading

# Used ChatGPT for a overview about how to create a ThreadPool and about the python class syntax

# A Thread class where we will handle the request
class Worker(threading.Thread):
    """
    A class that create a thread that take tasks from a queue and execute them.
    """
    def __init__(self, task_queue):
        """Initialize the task_queue, set the daemon on true and set the running varible on true.

        Args:
            task_queue (queue): A queue of task from where the worker can select.
        """
        super().__init__()
        self.task_queue = task_queue # the task queue used to store the tasks
        self.daemon = True # make the program to run when the main program is up
        self.running = True # running variable

    def run(self):
        """
        Task the first task from the queue and executes it.
        After finishing the task mark it as done.
        """
        while self.running:
            try:
                task, args = self.task_queue.get_nowait() # get the first task from the queue
                try:
                    task(*args) # execute the task
                finally:
                    self.task_queue.task_done() # mask the task as done
            except queue.Empty:
                pass
    
    def stop(self):
        """
        Mark the running varible as False to stop the run loop.
        """
        self.running = False


class ThreadPool:
    """
    A class that creates a pool of threads to can handle multiple task in the same time.
    """
    def __init__(self, workers_number):
        """
        Initialize the queue. Create and start the threads.

        Args:
            workers_number (int): The number of threads to create. The number must to be positive and be smaller than 64
            (the maximum number of threads that can be created)
        """
        self.task_queue = queue.Queue()
        if workers_number > 64: workers_number = 64 # do not make more then 64 threads
        if workers_number < 0: workers_number = 16 # if the numbers is negative we will create a default number of threads (16)
        self.workers = [Worker(self.task_queue) for _ in range(workers_number)]

        for worker in self.workers:
            worker.start() # start all the thread from the pool
    
    def submit(self, task, *args):
        """Add a task to the task queue.

        Args:
            task (function): The task that need to be done.
            *args: The arguments od the function
        """
        self.task_queue.put((task, args))

    def shutdown(self):
        """
        Stop all the threads and wait all the task to be finished.
        """
        # close all created threads
        for worker in self.workers:
            worker.stop()

        # wait for all task to finish        
        self.task_queue.join()


