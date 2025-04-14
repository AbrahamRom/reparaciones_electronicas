from simulation import ReparationCompanySimulation as Simulation

from sim_stats import Statistics

import numpy as np


def run_simulation():
    """
    Run the simulation.
    """

    # Set function distributions for times on simulation

    def classification_function():
        return np.random.exponential(6)

    def general_reparation_function():
        return np.random.exponential(35)

    def expert_reparation_function():
        return np.random.exponential(65)

    def shipping_function():
        return np.random.exponential(12.5)

    # Set the simulation parameters
    arrival_rate = 9 / 60  # 9 appliances per hour
    simulation_time = 500  # time in minutes

    # Create the simulation
    simulation = Simulation(
        arrival_rate,
        classification_function,
        general_reparation_function,
        expert_reparation_function,
        shipping_function,
        simulation_time,
    )

    # Run the simulation
    simulation.run()

    # Get the statistics
    statistics = simulation.get_statistics()

    # Create the Statistics object

    stats = Statistics(statistics)

    stats.plot_timeline()

    # Calculate the statistics


# if __name__ == "__main__":
run_simulation()
