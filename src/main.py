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
    simulation_time = 100  # time in minutes

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

    print("Simulation Statistics:")
    # print(f"Total arrivals: {statistics['arrivals']} \n")
    print(f"Total waiting_classification: {statistics['waiting_classification']} \n")
    print(f"Total classificated_at: {statistics['classificated_at']} \n")
    print(
        f"Total waiting_general_reparation: {statistics['waiting_general_reparation']} \n"
    )
    print(
        f"Total waiting_expert_reparation: {statistics['waiting_expert_reparation']} \n"
    )
    print(f"Total waiting_shipping: {statistics['waiting_shipping']} \n")

    print(f"Total departures: {statistics['departure']} \n")
    # print(f"Total appliances in classification: {statistics['classification']}")
    # print(f"Total appliances in general reparation: {statistics['general_reparation']}")
    # print(f"Total appliances in expert reparation: {statistics['expert_reparation']}")
    # print(f"Total appliances in shipping: {statistics['shipping']}")
    # print(f"Total appliances in system: {statistics['in_system']}")

    # Create the Statistics object

    # stats = Statistics(statistics)

    # Calculate the statistics


# if __name__ == "__main__":
run_simulation()
