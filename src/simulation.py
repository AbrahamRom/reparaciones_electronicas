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

    def new_arrival(self):  # event
        appliance_id = self.n_appliances
        self.n_appliances += 1
        self.arrivals[appliance_id] = self.time

        # case 1: Classification Specialist is idle
        if self.classification_status < 0:
            # Process the applience inmediately
            self.process_classification()

        # case 2: Classification Specialist is busy
        else:
            # Add the appliance to classification queue
            pass

    def process_classification(self, appliance_id):
        self.classification_status = appliance_id
        self.classificated_at = self.time
        duration = self.classification_function()
        maint_time_end = self.time + duration
        heapq.heappush(self.events_queue, (maint_time_end, "end_classification"))

    def classification_ended(self):  # event
        assert self.classification_status >= 0
        appliance_id = self.classification_status
