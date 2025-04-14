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

    def average_time_in_node_classification(self):
        total_waiting = 0
        total_occurrences = 0

        waiting_classification = self.statistics.get("waiting_classification", {})
        # For exit times, merge waiting times from all next-node queues.
        for appliance_id, entry_times in waiting_classification.items():
            exit_times = []
            # waiting_general_reparation might be a list for multiple occurrences
            if appliance_id in self.statistics.get("waiting_general_reparation", {}):
                val = self.statistics["waiting_general_reparation"][appliance_id]
                if isinstance(val, list):
                    exit_times.extend(val)
                else:
                    exit_times.append(val)
            # waiting_expert_reparation is stored as a scalar or list
            if appliance_id in self.statistics.get("waiting_expert_reparation", {}):
                val = self.statistics["waiting_expert_reparation"][appliance_id]
                if isinstance(val, list):
                    exit_times.extend(val)
                else:
                    exit_times.append(val)
            # waiting_shipping is stored as a scalar or list
            if appliance_id in self.statistics.get("waiting_shipping", {}):
                val = self.statistics["waiting_shipping"][appliance_id]
                if isinstance(val, list):
                    exit_times.extend(val)
                else:
                    exit_times.append(val)

            # Sort entry and exit times to pair them in order.
            entry_times_sorted = sorted(entry_times)
            exit_times_sorted = sorted(exit_times)

            # Pair occurrences in order (only as many pairs as the shortest list).
            for entry, exit in zip(entry_times_sorted, exit_times_sorted):
                if exit > entry:
                    total_waiting += exit - entry
                    total_occurrences += 1

        return total_waiting / total_occurrences if total_occurrences > 0 else 0

    def average_wait_time_in_general_reparation(self):
        total_wait = 0
        total_occurrences = 0
        waiting_general = self.statistics.get("waiting_general_reparation", {})
        begin_general = self.statistics.get("begin_general_reparation", {})
        for appliance_id, entry_times in waiting_general.items():
            # Ensure entry_times is a list (for appliances with multiple entries)
            if not isinstance(entry_times, list):
                entry_times = [entry_times]
            # Use the general reparation start time as exit time if available.
            if appliance_id in begin_general:
                begin_time = begin_general[appliance_id][0]
                for entry in entry_times:
                    if begin_time > entry:
                        total_wait += begin_time - entry
                        total_occurrences += 1
        return total_wait / total_occurrences if total_occurrences > 0 else 0
