import threading
import random
import queue
import collections
from concurrent.futures import ThreadPoolExecutor

class PlantSimulation:
    def __init__(self, m, n):
        self.MaxTimePart = 18000  # Maximum wait time for a part worker
        self.MaxTimeProduct = 20000  # Maximum wait time for a product worker

        self.buffer_state = queue.Queue()
        self.cart_state = queue.SimpleQueue()
        self.completed_products = collections.defaultdict(int)

        self.lock = threading.Lock()

        self.m = m  # Number of Part Workers
        self.n = n  # Number of Product Workers

    def __enter__(self):
        self.log_file = open("log.txt", "w")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.log_file.close()

    def log_info(self, worker_type, worker_id, action):
        self.log_file.write(f"{worker_type} {worker_id}: {action}\n")

    def worker(self, worker_id, worker_type):
        for _ in range(5):
            if worker_type == "Part":
                order = self.generate_load_order()
                action_template = "Generating load order: {}"
                process_order_fn = self.process_load_order
            else:
                order = self.generate_pickup_order()
                action_template = "Generating pickup order: {}"
                process_order_fn = self.process_pickup_order

            self.log_info(worker_type + " Worker", worker_id, action_template.format(order))

            while True:
                with self.lock:
                    if self.is_order_possible(order):
                        self.load_parts_to_buffer(order)
                        self.log_info(worker_type + " Worker", worker_id, f"Loaded parts to buffer: {order}")
                        break
                    else:
                        self.log_info(worker_type + " Worker", worker_id, "Waiting for required parts")

                if random.randint(0, 1):
                    self.move_parts_back_to_buffer()

            time_taken = self.move_parts(order, worker_type)
            self.log_info(worker_type + " Worker", worker_id, f"Moved parts: {order}")
            process_order_fn(worker_id, time_taken)

    def generate_load_order(self):
        return [random.randint(0, 5) for _ in range(5)]

    def generate_pickup_order(self):
        return [random.randint(0, 3) for _ in range(5)]

    def is_order_possible(self, order):
        return all(part_count <= buffer_count for part_count, buffer_count in zip(order, self.buffer_state.queue))

    def load_parts_to_buffer(self, order):
        for part_count in order:
            self.buffer_state.put(part_count)

    def move_parts_back_to_buffer(self):
        while not self.cart_state.empty():
            part_count = self.cart_state.get()
            self.buffer_state.put(part_count)

    def move_parts(self, order, worker_type):
        time_per_part = {
            "Part": [500, 500, 600, 600, 700],
            "Product": [200, 200, 300, 300, 400]
        }
        time_taken = sum(part_count * time for part_count, time in zip(order, time_per_part[worker_type]))
        for part_count in order:
            self.buffer_state.get()
            self.cart_state.put(part_count)
        return time_taken

    def process_load_order(self, worker_id, time_taken):
        if time_taken > self.MaxTimePart:
            self.log_info("Part Worker", worker_id, "Timeout! Generating new load order.")
            self.move_parts_back_to_buffer()
        else:
            with self.lock:
                self.completed_products[worker_id] += 1
                self.log_info("Part Worker", worker_id, f"Load order completed. Total completed products: {self.completed_products[worker_id]}")

    def process_pickup_order(self, worker_id, time_taken):
        if time_taken > self.MaxTimeProduct:
            self.log_info("Product Worker", worker_id, "Timeout! Generating new pickup order.")
            self.move_parts_back_to_buffer()
        else:
            self.log_info("Product Worker", worker_id, "Pickup order completed.")

    def run_simulation(self):
        with ThreadPoolExecutor(max_workers=self.m + self.n) as executor:
            workers = [executor.submit(self.worker, worker_id, "Part") for worker_id in range(1, self.m + 1)] + [executor.submit(self.worker, worker_id, "Product") for worker_id in range(1, self.n + 1)]

            for worker in workers:
                worker.result()

        self.log_info("Finish!", "", "")
        print("Finish!")

if __name__ == "__main__":
    with PlantSimulation(m=20, n=16) as plant_simulation:
        plant_simulation.run_simulation()
