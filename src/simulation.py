import heapq
import numpy as np


class ReparationCompanySimulation:
    """
    Simulates a reparation company with:

    - 1 specialist in clasification
    - 3 specialists in general reparations
    - 4 expert specialists
    - 2 shipping port
    """

    def __init__(
        self,
        arrival_rate,
        classification_function,
        general_reparation_function,
        expert_reparation_function,
        shipping_function,
        simulation_time=1000,
    ):

        # |------------|
        # | Parameters |
        # |------------|

        self.arrival_rate = arrival_rate  # lambda parameter for Poisson
        self.classification_function = (
            classification_function  # function to generate classification service time
        )
        self.general_reparation_function = general_reparation_function  # function to generate general reparation service time
        self.expert_reparation_function = expert_reparation_function  # function to generate expert reparation service time
        self.shipping_function = (
            shipping_function  # function to generate shipping service time
        )
        self.simulation_time = simulation_time

        self.rng = np.random.default_rng()

        # |------------------|
        # | Simulation state |
        # |------------------|

        self.time = 0
        self.n_appliances = 0  # counter to give ids to appliences
        self.events_queue = (
            []
        )  # heap queue containing tuples (t, event) or (t, event, index)
        self.events = {
            "arrival": self.new_arrival,
            "end_classification": self.classification_ended,
            "end_general_reparation": self.general_reparation_ended,
            "end_expert_reparation": self.expert_reparation_ended,
            "end_shipping": self.shipping_ended,
        }

        self.q_classification = []  # Queue for classification
        self.q_general_reparation = [[], [], []]  # Queue for general reparation
        self.q_expert_reparation = [[], [], [], []]  # Queue for expert reparation
        self.q_shipping = [[], []]  # Queue for shipping

        # stores the id of the appliences using the respective servers; if none then -1
        self.classification_status = -1
        self.general_reparation_status = [-1, -1, -1]
        self.expert_reparation_status = [-1, -1, -1, -1]
        self.shipping_status = [-1, -1]

        # |---------------------|
        # | Statistics tracking |
        # |---------------------|

        self.arrivals = {}  # arrivals[i] = time of arrival of applience i
        self.classificated_at = (
            {}
        )  # classificated_at[i][j] = time of arrival of appliance i to classification the j-th time
        self.waiting_general_reparation = (
            {}
        )  # waiting_general_reparation[i][j] = time of begin waiting for general reparation of appliance i for the j-th time
        self.begin_general_reparation = (
            {}
        )  # begin_general_reparation[i][j] = tuple(time,server) of begin of general reparation of appliance i for the j-th time
        self.waiting_expert_reparation = (
            {}
        )  # waiting_expert_reparation[i] = time of begin waiting for expert reparation of appliance i
        self.begin_expert_reparation = (
            {}
        )  # begin_expert_reparation[i] = tuple(time,server) of begin of expert reparation of appliance i
        self.waiting_shipping = (
            {}
        )  # waiting_shipping[i] = time of begin waiting for shipping of appliance i
        self.begin_shipping = (
            {}
        )  # begin_shipping[i] = tuple(time,server) of arrive to shipping server of appliance i
        self.departure = {}  # departure[i] = time of departure of applience i

        # |--------|
        # | Events |
        # |--------|

    def new_arrival(self):  # event
        appliance_id = self.n_appliances
        self.n_appliances += 1
        self.arrivals[appliance_id] = self.time

        # case 1: Classification Specialist is idle
        if self.classification_status < 0:
            # Process the applience inmediately
            self.process_classification(appliance_id)

        # case 2: Classification Specialist is busy
        else:
            # Add the appliance to classification queue
            self.q_classification.append(appliance_id)

    def process_classification(self, appliance_id):
        self.classification_status = appliance_id
        self.classificated_at = self.time
        duration = self.classification_function()
        maint_time_end = self.time + duration
        heapq.heappush(self.events_queue, (maint_time_end, "end_classification"))

    def next_arrival(self):
        if self.time >= self.simulation_time:
            return
        time_arrival = self.rng.exponential(1 / self.arrival_rate)
        next_time_arrival = self.time + time_arrival
        if next_time_arrival < self.simulation_time:
            heapq.heappush(self.events_queue, (next_time_arrival, "arrival"))

    def classification_ended(self):  # event
        assert self.classification_status >= 0
        appliance_id = self.classification_status
        next_stage = self.send_2_next_stage()

        if next_stage == 0:
            self.waiting_shipping[appliance_id] = self.time
        elif next_stage == 1:
            # An applience can pass for this stage more than one
            if appliance_id in self.waiting_general_reparation:
                self.waiting_general_reparation[appliance_id].append(self.time)
            else:
                self.waiting_general_reparation[appliance_id] = [self.time]
        else:
            self.waiting_expert_reparation[appliance_id] = self.time

        # Process next applience in classification queue
        if self.q_classification:
            next_applience_id = self.q_classification.pop()
            self.process_classification(next_applience_id)
        else:
            self.classification_status = -1

        # Send to next stage
        if next_stage == 0:
            if self.q_shipping:
                self.q_shipping.append(appliance_id)
            else:
                if not (-1 in self.shipping_status):
                    self.q_shipping.append(appliance_id)
                else:
                    index = 0 if self.shipping_status[0] == -1 else 1
                    self.process_shipping(index, appliance_id)
        elif next_stage == 1:
            if self.q_general_reparation:
                self.q_general_reparation.append(appliance_id)
            else:
                if not (-1 in self.general_reparation_status):
                    self.q_general_reparation.append(appliance_id)
                else:
                    index = self.general_reparation_status.index(-1)
                    self.process_general_reparation(index, appliance_id)
        else:
            if self.q_expert_reparation:
                self.q_expert_reparation.append(appliance_id)
            else:
                if not (-1 in self.expert_reparation_status):
                    self.q_expert_reparation.append(appliance_id)
                else:
                    index = self.expert_reparation_status.index(-1)
                    self.process_expert_reparation(index, appliance_id)

    def send_2_next_stage(self):
        # Generate a random number between 0 and 1
        rand = self.rng.random()

        # It must decide next stage with:

        # 17% go to shipping
        if rand < 0.17:
            return 0
        # 47,31% go to general reparations
        elif rand < 0.17 + 0.4731:
            return 1
        # 35,69% go to expert reparations
        else:
            return 2

    def process_shipping(self, index, applience_id):
        pass

    def process_general_reparation(self, index, applience_id):
        pass

    def process_expert_reparation(self, index, applience_id):
        pass

    def general_reparation_ended(self):  # event
        pass

    def expert_reparation_ended(self):  # event
        pass

    def shipping_ended(self):  # event
        pass
