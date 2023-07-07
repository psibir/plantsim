import threading
import random

# Constants
MaxTimePart = 18000  # Maximum wait time for a part worker
MaxTimeProduct = 20000  # Maximum wait time for a product worker

# Shared resources
buffer_lock = threading.Lock()
buffer_state = [5, 5, 4, 3, 3]
cart_state = [0, 0, 0, 0, 0]
completed_products = [0] * 16  # Number of completed products for each product worker

# Log file
log_file = open("log.txt", "w")

def log_info(worker_type, worker_id, action):
    log_file.write(f"{worker_type} {worker_id}: {action}\n")

def part_worker(worker_id):
    global buffer_state, cart_state

    for _ in range(5):
        load_order = generate_load_order()
        log_info("Part Worker", worker_id, f"Generating load order: {load_order}")

        while True:
            with buffer_lock:
                if is_load_order_possible(load_order):
                    load_parts_to_buffer(load_order)
                    log_info("Part Worker", worker_id, f"Loaded parts to buffer: {load_order}")
                    break
                else:
                    log_info("Part Worker", worker_id, "Waiting for buffer space")

            if random.randint(0, 1):
                move_parts_back_to_buffer()

        time_taken = move_parts_to_cart(load_order)
        log_info("Part Worker", worker_id, f"Moved parts to cart: {load_order}")
        process_load_order(worker_id, time_taken)

def product_worker(worker_id):
    global buffer_state, cart_state, completed_products

    for _ in range(5):
        pickup_order = generate_pickup_order()
        log_info("Product Worker", worker_id, f"Generating pickup order: {pickup_order}")

        while True:
            with buffer_lock:
                if is_pickup_order_possible(pickup_order):
                    pickup_parts_from_buffer(pickup_order)
                    log_info("Product Worker", worker_id, f"Picked up parts from buffer: {pickup_order}")
                    break
                else:
                    log_info("Product Worker", worker_id, "Waiting for required parts")

            if random.randint(0, 1):
                move_parts_back_to_buffer()

        time_taken = move_parts_to_assembly_area(pickup_order)
        log_info("Product Worker", worker_id, f"Moved parts to assembly area: {pickup_order}")
        process_pickup_order(worker_id, time_taken)

def generate_load_order():
    return [random.randint(0, 5) for _ in range(5)]

def generate_pickup_order():
    a_count = random.randint(0, 3)
    b_count = random.randint(0, 3 - a_count)
    c_count = random.randint(0, 3 - a_count - b_count)
    d_count = random.randint(0, 3 - a_count - b_count - c_count)
    e_count = random.randint(0, 3 - a_count - b_count - c_count - d_count)

    return [a_count, b_count, c_count, d_count, e_count]

def is_load_order_possible(load_order):
    global buffer_state

    for part_count, buffer_count in zip(load_order, buffer_state):
        if part_count > buffer_count:
            return False

    return True

def load_parts_to_buffer(load_order):
    global buffer_state

    buffer_state = [buffer_count - part_count for buffer_count, part_count in zip(buffer_state, load_order)]

def move_parts_back_to_buffer():
    global cart_state, buffer_state

    cart_state = [cart_count + part_count for cart_count, part_count in zip(cart_state, buffer_state)]
    buffer_state = [0] * 5

def move_parts_to_cart(load_order):
    global buffer_state, cart_state

    time_taken = sum(part_count * time for part_count, time in zip(load_order, [500, 500, 600, 600, 700]))
    buffer_state = [buffer_count - part_count for buffer_count, part_count in zip(buffer_state, load_order)]
    cart_state = [cart_count + part_count for cart_count, part_count in zip(cart_state, load_order)]

    return time_taken

def process_load_order(worker_id, time_taken):
    global completed_products

    if time_taken > MaxTimePart:
        log_info("Part Worker", worker_id, "Timeout! Generating new load order.")
        move_parts_back_to_buffer()
    else:
        completed_products[worker_id - 1] += 1
        log_info("Part Worker", worker_id, f"Load order completed. Total completed products: {completed_products[worker_id - 1]}")

def is_pickup_order_possible(pickup_order):
    global buffer_state

    for part_count, buffer_count in zip(pickup_order, buffer_state):
        if part_count > buffer_count:
            return False

    return True

def pickup_parts_from_buffer(pickup_order):
    global buffer_state

    buffer_state = [buffer_count - part_count for buffer_count, part_count in zip(buffer_state, pickup_order)]

def move_parts_to_assembly_area(pickup_order):
    global cart_state

    time_taken = sum(part_count * time for part_count, time in zip(pickup_order, [200, 200, 300, 300, 400]))
    cart_state = [cart_count - part_count for cart_count, part_count in zip(cart_state, pickup_order)]

    return time_taken

def process_pickup_order(worker_id, time_taken):
    if time_taken > MaxTimeProduct:
        log_info("Product Worker", worker_id, "Timeout! Generating new pickup order.")
        move_parts_back_to_buffer()
    else:
        log_info("Product Worker", worker_id, "Pickup order completed.")

if __name__ == "__main__":
    m = 20  # Number of Part Workers
    n = 16  # Number of Product Workers

    part_workers = []
    product_workers = []

    for i in range(m):
        part_workers.append(threading.Thread(target=part_worker, args=(i + 1,)))

    for i in range(n):
        product_workers.append(threading.Thread(target=product_worker, args=(i + 1,)))

    for worker in part_workers:
        worker.start()

    for worker in product_workers:
        worker.start()

    for worker in part_workers:
        worker.join()

    for worker in product_workers:
        worker.join()

    log_file.write("Finish!\n")
    log_file.close()
    print("Finish!")
  
