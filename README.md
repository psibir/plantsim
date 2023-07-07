# Plant Simulation

The Plant Simulation program simulates a plant environment with part workers and product workers. It models the movement of parts from buffers to carts and from carts to the assembly area, tracking the completion of load and pickup orders.

## Features
- Simulates a plant environment with part workers and product workers.
- Generates random load orders and pickup orders.
- Handles waiting for buffer space and required parts.
- Tracks the completion of load orders and pickup orders.
- Detects timeouts and generates new orders if necessary.
- Uses multithreading with a thread pool to simulate concurrent worker operations.

## Installation
1. Clone the repository or download the source code.
2. Make sure you have Python 3 installed on your system.
3. Install the required dependencies by running the following command:
   ```
   pip install concurrent.futures
   ```
4. Run the simulation by executing the `main.py` file.

## Usage
1. Create an instance of the `PlantSimulation` class, specifying the number of part workers (`m`) and product workers (`n`).
2. Run the simulation by calling the `run_simulation()` method on the `PlantSimulation` instance.
3. The simulation will log the actions of the workers to a file named `log.txt`.
4. Once the simulation is complete, the log file will be closed and the program will print "Finish!".

## Configuration
You can modify the following parameters in the `PlantSimulation` class to customize the simulation:

- `MaxTimePart`: Maximum wait time for a part worker.
- `MaxTimeProduct`: Maximum wait time for a product worker.
- `m`: Number of part workers.
- `n`: Number of product workers.

## License
This code is released under the MIT License. See [LICENSE](LICENSE) for more information.

## Acknowledgments
The Plant Simulation program was developed as a sample project to demonstrate multithreading and simulation concepts.

*Disclaimer: This simulation is a simplified representation and may not reflect real-world scenarios accurately.*
