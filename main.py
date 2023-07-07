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
        self.completed_products = collections.Counter()

        self.lock = threading.Lock()
        self.log_file = open("log.txt", "w")

        self.m = m  # Number of Part Workers
        self.n = n  # Number of Product Workers

    def log_info(self, worker_type, worker_id, action):
        self.log_file.write(f"{worker_type} {worker_id}: {action}\n")

    def part_worker(self, worker_id):
        for _ in range(5):
            load_order = self.generate_load_order()
            self.log_info("Part Worker", worker_id, f"Generating load order: {load_order}")

            while True:
                with self.lock:
                    if self.is_load_order_possible(load_order):
                        self.load_parts_to_buffer(load_order)
                        self.log_info("Part Worker", worker_id, f"Loaded parts to buffer: {load_order}")
                        break
                    else:
                        self.log_info("Part Worker", worker_id, "Waiting for buffer space")

                if random.randint(0, 1):
                    self.move_parts_back_to_buffer()

            time_taken = self.move_parts_to_cart(load_order)
            self.log_info("Part Worker", worker_id, f"Moved parts to cart: {load_order}")
            self.process_load_order(worker_id, time_taken)

    def product_worker(self, worker_id):
        for _ in range(5):
            pickup_order = self.generate_pickup_order()
            self.log_info("Product Worker", worker_id, f"Generating pickup order: {pickup_order}")

            while True:
                with self.lock:
                    if self.is_pickup_order_possible(pickup_order):
                        self.pickup_parts_from_buffer(pickup_order)
                        self.log_info("Product Worker", worker_id, f"Picked up parts from buffer: {pickup_order}")
                        break
                    else:
                        self.log_info("Product Worker", worker_id, "Waiting for required parts")

                if random.randint(0, 1):
                    self.move_parts_back_to_buffer()

            time_taken = self.move_parts_to_assembly_area(pickup_order)
            self.log_info("Product Worker", worker_id, f"Moved parts to assembly area: {pickup_order}")
            self.process_pickup_order(worker_id, time_taken)

    def generate_load_order(self):
        return [random.randint(0, 5) for _ in range(5)]

    def generate_pickup_order(self):
        a_count = random.randint(0, 3)
        b_count = random.randint(0, 3 - a_count)
        c_count = random.randint(0, 3 - a_count - b_count)
        d_count = random.randint(0, 3 - a_count - b_count - c_count)
        e_count = random.randint(0, 3 - a_count - b_count - c_count - d_count)

        return [a_count, b_count, c_count, d_count, e_count]

    def is_load_order_possible(self, load_order):
        for part_count, buffer_count in zip(load_order, self.buffer_state.queue):
            if part_count > buffer_count:
                return False
        return True

    def load_parts_to_buffer(self, load_order):
        for part_count in load_order:
            self.buffer_state.put(part_count)

    def move_parts_back_to_buffer(self):
        while not self.cart_state.empty():
            part_count = self.cart_state.get()
            self.buffer_state.put(part_count)

    def move_parts_to_cart(self, load_order):
        time_taken = sum(part_count * time for part_count, time in zip(load_order, [500, 500, 600, 600, 700]))
        for part_count in load_order:
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

    def is_pickup_order_possible(self, pickup_order):
        for part_count, buffer_count in zip(pickup_order, self.buffer_state.queue):
            if part_count > buffer_count:
                return False
        return True

    def pickup_parts_from_buffer(self, pickup_order):
        for part_count in pickup_order:
            self.buffer_state.get()

    def move_parts_to_assembly_area(self, pickup_order):
        time_taken = sum(part_count * time for part_count, time in zip(pickup_order, [200, 200, 300, 300, 400]))
        for part_count in pickup_order:
            self.cart_state.get()
        return time_taken

    def process_pickup_order(self, worker_id, time_taken):
        if time_taken > self.MaxTimeProduct:
            self.log_info("Product Worker", worker_id, "Timeout! Generating new pickup order.")
            self.move_parts_back_to_buffer()
        else:
            self.log_info("Product Worker", worker_id, "Pickup order completed.")

    def run_simulation(self):
        with ThreadPoolExecutor(max_workers=self.m + self.n) as executor:
            part_workers = [executor.submit(self.part_worker, worker_id) for worker_id in range(1, self.m + 1)]
            product_workers = [executor.submit(self.product_worker, worker_id) for worker_id in range(1, self.n + 1)]

            for worker in part_workers + product_workers:
                worker.result()

        self.log_info("Finish!", "", "")
        self.log_file.close()
        print("Finish!")

if __name__ == "__main__":
    plant_simulation = PlantSimulation(m=20, n=16)
    plant_simulation.run_simulation()
