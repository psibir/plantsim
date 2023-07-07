import unittest
from queue import Queue
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from ../main import PlantSimulation

class PlantSimulationTests(unittest.TestCase):
    def test_buffer_state_initialization(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            self.assertIsInstance(simulation.buffer_state, Queue)
            self.assertEqual(simulation.buffer_state.qsize(), 0)

    def test_cart_state_initialization(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            self.assertIsInstance(simulation.cart_state, Queue)
            self.assertEqual(simulation.cart_state.qsize(), 0)

    def test_completed_products_initialization(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            self.assertIsInstance(simulation.completed_products, defaultdict)
            self.assertEqual(len(simulation.completed_products), 0)

    def test_generate_load_order(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            order = simulation.generate_load_order()
            self.assertIsInstance(order, list)
            self.assertEqual(len(order), 5)

    def test_generate_pickup_order(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            order = simulation.generate_pickup_order()
            self.assertIsInstance(order, list)
            self.assertEqual(len(order), 5)

    def test_is_order_possible(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            simulation.buffer_state.put(3)
            simulation.buffer_state.put(2)
            simulation.buffer_state.put(4)
            order1 = [1, 2, 3]
            order2 = [3, 2, 1]
            order3 = [1, 2, 5]
            self.assertTrue(simulation.is_order_possible(order1))
            self.assertFalse(simulation.is_order_possible(order2))
            self.assertFalse(simulation.is_order_possible(order3))

    def test_load_parts_to_buffer(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            simulation.load_parts_to_buffer([1, 2, 3])
            self.assertEqual(simulation.buffer_state.qsize(), 3)

    def test_move_parts_back_to_buffer(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            simulation.cart_state.put(2)
            simulation.cart_state.put(3)
            simulation.move_parts_back_to_buffer()
            self.assertEqual(simulation.buffer_state.qsize(), 2)
            self.assertEqual(simulation.cart_state.qsize(), 0)

    def test_move_parts(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            time_per_part = [500, 500, 600, 600, 700]
            time_taken = simulation.move_parts([1, 2, 3, 4, 5], "Part")
            expected_time = sum(part_count * time for part_count, time in zip([1, 2, 3, 4, 5], time_per_part))
            self.assertEqual(time_taken, expected_time)
            self.assertEqual(simulation.buffer_state.qsize(), 0)
            self.assertEqual(simulation.cart_state.qsize(), 5)

    def test_process_load_order(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            worker_id = 1
            time_taken = simulation.MaxTimePart - 1
            simulation.process_load_order(worker_id, time_taken)
            self.assertEqual(simulation.completed_products[worker_id], 1)

    def test_process_pickup_order(self):
        with self.create_plant_simulation(m=5, n=3) as simulation:
            worker_id = 1
            time_taken = simulation.MaxTimeProduct - 1
            simulation.process_pickup_order(worker_id, time_taken)
            self.assertEqual(simulation.completed_products[worker_id], 1)

    @contextmanager
    def create_plant_simulation(self, m, n):
        with PlantSimulation(m, n) as simulation:
            yield simulation

if __name__ == "__main__":
    unittest.main()
