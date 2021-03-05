import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1
threads = workers
worker_class = "eventlet"
