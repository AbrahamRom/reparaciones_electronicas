class Statistics:
    """
    Class to calculate the statistics of the simulation.
    """

    def __init__(self, statistics):
        self.statistics = statistics

    def _simulation_duration(self):
        arrivals = self.statistics["arrivals"]
        departures = self.statistics["departure"]
        return max(departures.values()) - min(arrivals.values())

    def _arrival_rate(self):
        arrivals = self.statistics["arrivals"]
        T = self._simulation_duration()
        return len(arrivals) / T if T > 0 else 0

    def average_time_in_system(self):
        total_time = 0
        departures = self.statistics["departure"]
        arrivals = self.statistics["arrivals"]
        for a in departures:
            total_time += departures[a] - arrivals[a]
        return total_time / len(departures) if departures else 0

    def average_time_in_classification(self):
        total_time = 0
        classificated_at = self.statistics["classificated_at"]
        arrivals = self.statistics["arrivals"]
        for a in classificated_at:
            total_time += classificated_at[a] - arrivals[a]
        return total_time / len(classificated_at) if classificated_at else 0

    def average_time_in_general_reparation(self):
        total_time = 0
        begin_general = self.statistics["begin_general_reparation"]
        arrivals = self.statistics["arrivals"]
        for a in begin_general:
            total_time += begin_general[a][0] - arrivals[a]
        return total_time / len(begin_general) if begin_general else 0

    def average_time_in_expert_reparation(self):
        total_time = 0
        begin_expert = self.statistics["begin_expert_reparation"]
        arrivals = self.statistics["arrivals"]
        for a in begin_expert:
            total_time += begin_expert[a][0] - arrivals[a]
        return total_time / len(begin_expert) if begin_expert else 0

    def average_time_in_shipping(self):
        total_time = 0
        begin_shipping = self.statistics["begin_shipping"]
        arrivals = self.statistics["arrivals"]
        for a in begin_shipping:
            total_time += begin_shipping[a][0] - arrivals[a]
        return total_time / len(begin_shipping) if begin_shipping else 0

    # Using Little's Law: L = λ * W, where W is the average time in the node.
    def average_appliances_in_classification(self):
        arrival_rate = self._arrival_rate()
        return arrival_rate * self.average_time_in_classification()

    def average_appliances_in_general_reparation(self):
        arrival_rate = self._arrival_rate()
        return arrival_rate * self.average_time_in_general_reparation()

    def average_appliances_in_expert_reparation(self):
        arrival_rate = self._arrival_rate()
        return arrival_rate * self.average_time_in_expert_reparation()

    def average_appliances_in_shipping(self):
        arrival_rate = self._arrival_rate()
        return arrival_rate * self.average_time_in_shipping()

    # Tiempo medio en la empresa desde que se clasifica hasta que se empaqueta.
    # Se calcula usando la diferencia entre el tiempo de salida (departure) y el momento en que termina la clasificación.
    def average_time_in_company(self):
        total_time = 0
        departures = self.statistics["departure"]
        classificated_at = self.statistics["classificated_at"]
        count = 0
        for a in departures:
            if a in classificated_at:
                total_time += departures[a] - classificated_at[a]
                count += 1
        return total_time / count if count > 0 else 0
