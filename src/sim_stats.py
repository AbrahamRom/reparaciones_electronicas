from scipy import stats
import matplotlib.pyplot as plt


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

    # ------------------------------------------------------------------------------

    def plot_timeline(self):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 8))

        # Get statistics dictionaries
        arrivals = self.statistics.get("arrivals", {})
        departures = self.statistics.get("departure", {})
        classificated_at = self.statistics.get("classificated_at", {})
        begin_general = self.statistics.get("begin_general_reparation", {})
        begin_expert = self.statistics.get("begin_expert_reparation", {})
        begin_shipping = self.statistics.get("begin_shipping", {})

        # Set closing_time (if available in statistics, else use max departure)
        closing_time = self.statistics.get(
            "closing_time", max(departures.values()) if departures else 0
        )

        # Iterate over each appliance in order (assuming keys are numeric IDs)
        appliance_ids = sorted(arrivals.keys())
        for appliance_id in appliance_ids:
            a_time = arrivals[appliance_id]

            # Extract classification time (take first occurrence if list)
            c_time = classificated_at.get(appliance_id)
            if isinstance(c_time, list):
                c_time = c_time[0] if c_time else None

            # Determine repair start: extract the time value from the tuple (time, server)
            repair_time = None
            if appliance_id in begin_general:
                val = begin_general[appliance_id]
                if isinstance(val, list):
                    repair_time = val[0][0] if len(val) > 0 and val[0] else None
                else:
                    repair_time = val[0] if val else None
                repair_label = "General Reparation Start"
            elif appliance_id in begin_expert:
                val = begin_expert[appliance_id]
                if isinstance(val, list):
                    repair_time = val[0][0] if len(val) > 0 and val[0] else None
                else:
                    repair_time = val[0] if val else None
                repair_label = "Expert Reparation Start"
            else:
                repair_label = "Repair Start"

            # Ensure shipping time is a scalar (extract time from tuple)
            s_val = begin_shipping.get(appliance_id)
            if isinstance(s_val, list):
                s_time = s_val[0][0] if len(s_val) > 0 and s_val[0] else None
            elif s_val is not None:
                s_time = s_val[0]
            else:
                s_time = None

            d_time = departures.get(appliance_id)

            # Plot arrival to classification if classification time exists
            if c_time is not None:
                plt.plot(
                    [a_time, c_time],
                    [appliance_id, appliance_id],
                    "b-",
                    alpha=0.5,
                    label=(
                        "Arrival to Classification"
                        if appliance_id == appliance_ids[0]
                        else ""
                    ),
                )
                plt.plot(
                    a_time,
                    appliance_id,
                    "bo",
                    label=("Arrival" if appliance_id == appliance_ids[0] else ""),
                )
                plt.plot(
                    c_time,
                    appliance_id,
                    "g>",
                    label=(
                        "Classification" if appliance_id == appliance_ids[0] else ""
                    ),
                )

            # Plot classification to repair start if repair_time exists
            if (c_time is not None) and (repair_time is not None):
                plt.plot(
                    [c_time, repair_time],
                    [appliance_id, appliance_id],
                    "g-",
                    linewidth=2,
                    label=(repair_label if appliance_id == appliance_ids[0] else ""),
                )
                plt.plot(
                    repair_time,
                    appliance_id,
                    "gv",
                    label=(repair_label if appliance_id == appliance_ids[0] else ""),
                )

            # Plot repair to shipping start if both exist
            if (repair_time is not None) and (s_time is not None):
                plt.plot(
                    [repair_time, s_time],
                    [appliance_id, appliance_id],
                    "m-",
                    alpha=0.5,
                    label=(
                        "Repair to Shipping" if appliance_id == appliance_ids[0] else ""
                    ),
                )
                plt.plot(
                    s_time,
                    appliance_id,
                    "mo",
                    label=(
                        "Shipping Start" if appliance_id == appliance_ids[0] else ""
                    ),
                )

            # Plot shipping to departure if both exist
            if (s_time is not None) and (d_time is not None):
                plt.plot(
                    [s_time, d_time],
                    [appliance_id, appliance_id],
                    "r-",
                    linewidth=2,
                    label=(
                        "Shipping to Departure"
                        if appliance_id == appliance_ids[0]
                        else ""
                    ),
                )
                plt.plot(
                    d_time,
                    appliance_id,
                    "ro",
                    label=("Departure" if appliance_id == appliance_ids[0] else ""),
                )

        # Add vertical line for closing time
        plt.axvline(x=closing_time, color="k", linestyle="--", label="Closing Time")

        # Formatting
        plt.title("Appliance Processing Timeline")
        plt.xlabel("Time")
        plt.ylabel("Appliance ID")
        plt.xlim(-5, max(departures.values()) + 5)
        plt.ylim(-5, max(appliance_ids) + 5)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


# -----------------------------------------------------------------------------


def best_stats(self):
    time_by_applience = []
    for appliance_id in self.statistics["arrivals"]:
        time_by_applience.append(
            self.statistics["departure"][appliance_id]
            - self.statistics["arrivals"][appliance_id]
        )

    classification_times = []
    for appliance_id in self.statistics["classificated_at"]:
        classification_times.append(
            self.statistics["classificated_at"][appliance_id]
            - self.statistics["arrivals"][appliance_id]
        )

    general_reparation_times = []
    for appliance_id in self.statistics["begin_general_reparation"]:
        general_reparation_times.append(
            self.statistics["begin_general_reparation"][appliance_id][0]
            - self.statistics["waiting_general_reparations"][appliance_id]
        )

    expert_reparation_times = []
    for appliance_id in self.statistics["begin_expert_reparation"]:
        expert_reparation_times.append(
            self.statistics["begin_expert_reparation"][appliance_id][0]
            - self.statistics["waiting_expert_reparations"][appliance_id]
        )

    shipping_times = []
    for appliance_id in self.statistics["begin_shipping"]:
        shipping_times.append(
            self.statistics["begin_shipping"][appliance_id][0]
            - self.statistics["waiting_shippings"][appliance_id]
        )

    return {
        "time_by_applience": time_by_applience,
        "classification_times": classification_times,
        "general_reparation_times": general_reparation_times,
        "expert_reparation_times": expert_reparation_times,
        "shipping_times": shipping_times,
    }
