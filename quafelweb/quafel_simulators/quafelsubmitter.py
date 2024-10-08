"""
Here is the submission class that is used to submit a simulation request to the hardware.
"""
from collections.abc import Callable
from enum import Enum
from threading import Lock, Thread

from quafel_simulators.base.simulation_request import QuafelSimulationRequest
from quafel_simulators.output import QuafelOutputHardware
from quafel_simulators.util.connection import SubmitConnection, OutputConnection
from simulation_controller.util.simulation_request import SimulationRequest


class QuafelSubmissionState(Enum):
    """
    State of the request submitted
    """

    READY = 0  # Ready to return the output
    RUNNING = 1  # Running at the moment
    ERROR = -1  # Error occurred


class QuafelSubmitter:
    """
    The submitter class to submit a simulation request
    This class is a singleton
    """

    __quafel_submitter_instance = None
    __initialized = False
    __lock = Lock()

    def __new__(cls, *args, **kwargs):
        """
        Return the singleton instance
        """
        if cls.__quafel_submitter_instance is None:
            with cls.__lock:
                if cls.__quafel_submitter_instance is None:
                    cls.__quafel_submitter_instance = super(QuafelSubmitter, cls).__new__(cls)
        return cls.__quafel_submitter_instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        
        # The output hardware
        # Change this to a custom object of quafel_output_hardware to disable the configuration file
        self.quafel_output_hardware: QuafelOutputHardware = QuafelOutputHardware()

        self._requests: dict[str, QuafelSubmissionState] = (
            {}
        )  # dict of requests and their states (id: state)
        self._requests_lock = Lock()  # Lock for the requests

    def _add_request(self, simulation_request: QuafelSimulationRequest):
        """
        Add a request to the list
        """
        with self._requests_lock:
            self._requests[simulation_request.get_id()] = QuafelSubmissionState.RUNNING

    def _has_request(self, simulation_request: QuafelSimulationRequest) -> bool:
        """
        Check if the request is in the list
        """
        with self._requests_lock:
            return simulation_request.get_id() in self._requests

    def _set_state(
        self, simulation_request: QuafelSimulationRequest, state: QuafelSubmissionState
    ):
        """
        Set the state of the request
        """
        with self._requests_lock:
            self._requests[simulation_request.get_id()] = state

    def _remove_request(self, simulation_request: QuafelSimulationRequest):
        """
        Remove a request from the list
        """
        with self._requests_lock:
            del self._requests[simulation_request.get_id()]

    def _submit(self, simulation_request: QuafelSimulationRequest, handle: Callable[[QuafelSimulationRequest], None] = None):
        """
        Submit a simulation request
        """

        hardware_connection = SubmitConnection(
            simulation_request, self.quafel_output_hardware
        )
        self._add_request(simulation_request)

        print("Connect to hardware", simulation_request.get_hardware().get_id())
        if not hardware_connection.connect():
            self._set_state(simulation_request, QuafelSubmissionState.ERROR)
            return

        print("Initiating request", simulation_request.get_id())
        if not hardware_connection.initiate():
            self._set_state(simulation_request, QuafelSubmissionState.ERROR)
            return

        print("Submitting request", simulation_request.get_id())
        if not hardware_connection.submit():
            self._set_state(simulation_request, QuafelSubmissionState.ERROR)
            return

        print("Disconnecting from hardware", simulation_request.get_hardware().get_id())
        if not hardware_connection.disconnect():
            self._set_state(simulation_request, QuafelSubmissionState.ERROR)
            return

        print("Simulation done and ready to be pulled", simulation_request.get_id())
        self._set_state(simulation_request, QuafelSubmissionState.READY)
        
        if handle is not None:
            handle(simulation_request)

    def submit(self, simulation_request: QuafelSimulationRequest, handle: Callable[[SimulationRequest], None] = None) -> bool:
        """
        Submit a simulation request
        :param simulation_request: The simulation request to submit
        :param handle: The function to call when the request is ready to return the output (gets the id of the request)
        """

        if not self.quafel_output_hardware.update():
            # The output hardware is not configured
            raise RuntimeError("The output hardware is not configured")

        if self._has_request(simulation_request):
            # The request is already submitted
            # If the request is running, wait for it to finish
            # If the request failed and should be submitted again, get the output first to delete the request
            return False

        # Create thread to submit the request
        # The thread will call _submit
        thread: Thread = Thread(target=self._submit, args=[simulation_request, handle])
        thread.start()

        return True

    def get_state(
        self, simulation_request: QuafelSimulationRequest
    ) -> QuafelSubmissionState | None:
        """
        Get the state of the request
        :return: The state of the request or None if the request does not exist
        """
        with self._requests_lock:
            return self._requests.get(simulation_request.get_id(), None)

    def get_output(self, simulation_request) -> str | None:
        """
        Return the content of the csv file generated by the last pipeline combine.
        The request must be ready to return the output.
        The output is deleted after returned by this function.
        Returns None if the request is not ready to return the output or not existent. (the request is not deleted)
        """
        if not self._has_request(simulation_request):
            return None

        if self.get_state(simulation_request) == QuafelSubmissionState.RUNNING:
            return None

        if self.quafel_output_hardware is None:
            return None

        if not self.quafel_output_hardware.update():
            raise RuntimeError("The output hardware is not configured")

        output_connection = OutputConnection(
            self.quafel_output_hardware, simulation_request.get_id()
        )
        output = output_connection.get_output()

        self._remove_request(simulation_request)
        return output
