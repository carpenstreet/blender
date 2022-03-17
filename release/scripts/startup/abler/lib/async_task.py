from abc import ABCMeta, abstractmethod
from queue import Queue
from threading import Thread
from typing import Optional

import bpy


class AsyncTask(metaclass=ABCMeta):
    _wait_interval = 0.1
    _queue_sentinel = None
    _timeout_sentinel = None
    __timeout: Optional[float] = None  # seconds
    __running: Optional[Thread] = None
    __queue: Optional[Queue] = None

    def __init__(self, timeout: float):
        """
        If you don't need timeout, pass 0 as timeout parameter.
        """
        self.__timeout = timeout

    @abstractmethod
    def _task(self):
        """
        This method will be called in background thread.
        Do your networking or I/O bounded jobs in here.

        NOTE: DO NOT any bpy related jobs in here!
        """
        pass

    def _on_success(self):
        """
        This method will be called in main(script) thread,
        if the task completed without any exceptions.
        Do your bpy related jobs in here.

        NOTE: DO NOT any I/O bound jobs in here!
        """
        pass

    def _on_failure(self, e: BaseException):
        """
        This method will be called in main(script) thread,
        if the task failed.
        Do your bpy related jobs in here.

        NOTE: DO NOT any I/O bound jobs in here!
        """
        pass

    def _on_cleanup(self):
        """
        This method will be called in main(script) thread unconditionally.
        It behaves like `finally` statement.
        Do your bpy related jobs in here.

        NOTE: DO NOT any I/O bound jobs in here!
        """
        pass

    def start(self):
        """
        Starts this task. Must be called only once.

        Must be called in main(script) thread.
        """
        if self.__running is not None:
            raise AsyncTaskDoubleExecutionError("Already started")
        if self.__timeout is None:
            raise Exception("Timeout must be set")
        self.__queue = Queue(1)
        self.__running = Thread(target=self.__runner, daemon=True)
        self.__running.start()

        # NOTE: bpy.app.timers.is_registered misbehaves when an object's method is given,
        # (always return False) so ordinary functions are used here
        def queue_sentinel():
            if self.__queue.empty():
                return self._wait_interval
            if bpy.app.timers.is_registered(self._timeout_sentinel):
                bpy.app.timers.unregister(self._timeout_sentinel)
            popped = self.__queue.get_nowait()
            try:
                if isinstance(popped, BaseException):
                    self._on_failure(popped)
                else:
                    self._on_success()
            finally:
                self._on_cleanup()

        def timeout_sentinel():
            self.cancel()
            self._on_failure(AsyncTaskTimeoutError())

        self._queue_sentinel = queue_sentinel
        self._timeout_sentinel = timeout_sentinel

        bpy.app.timers.register(queue_sentinel)
        if self.__timeout > 0:
            bpy.app.timers.register(timeout_sentinel, first_interval=self.__timeout)

    def cancel(self):
        """
        Cancel the reserved execution of callbacks. Can be called multiple times safely.

        Limitation: DOES NOT cancel the task running in another thread.
        """
        if bpy.app.timers.is_registered(self._queue_sentinel):
            bpy.app.timers.unregister(self._queue_sentinel)

    def __runner(self):
        try:
            self._task()
        except BaseException as e:
            self.__queue.put_nowait(e)
        else:
            self.__queue.put_nowait(True)


class ExampleTask(AsyncTask):
    # `_task` should pass their results to `_on_XXX` callbacks
    # using object attributes like this.
    display_time = None

    def _task(self):
        import requests

        self.display_time = requests.get(
            "http://worldtimeapi.org/api/timezone/Asia/Seoul"
        ).json()["datetime"]

        # if any exception is raised, _on_failure will be called with the exception.
        # raise Exception("Surprise!")

        # if not, _on_success will be called.

    def _on_success(self):
        bpy.ops.acon3d.alert(
            "INVOKE_DEFAULT",
            title="Current Time",
            message_1=self.display_time,
        )

    def _on_failure(self, e: BaseException):
        bpy.ops.acon3d.alert(
            "INVOKE_DEFAULT",
            title="Failed!",
            message_1=str(e),
        )

    def _on_cleanup(self):
        # If you need "finally", this method is for you.
        pass


def _run_example_task():
    task = ExampleTask(timeout=10)
    # `start` must be called
    task.start()


class AsyncTaskDoubleExecutionError(Exception):
    """Raised when AsyncTask started twice"""

    pass


class AsyncTaskTimeoutError(Exception):
    """Raised when the timeout passed after task started"""

    pass
