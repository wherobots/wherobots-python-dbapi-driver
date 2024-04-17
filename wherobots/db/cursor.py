import queue
from typing import Any, Optional

from .errors import ProgrammingError, DatabaseError


class Cursor:

    def __init__(self, exec_fn, cancel_fn):
        self.__exec_fn = exec_fn
        self.__cancel_fn = cancel_fn

        self.__queue: queue.Queue = queue.Queue()
        self.__results: Optional[list[Any]] = None
        self.__current_execution_id: Optional[str] = None
        self.__current_row: int = 0

        # Description and row count are set by the last executed operation.
        # Their default values are defined by PEP-0249.
        self.__description: Optional[str] = None
        self.__rowcount: int = -1

        # Array-size is also defined by PEP-0249 and is expected to be read/writable.
        self.arraysize: int = 1

    @property
    def description(self) -> Optional[str]:
        return self.__description

    @property
    def rowcount(self) -> int:
        return self.__rowcount

    def __on_execution_result(self, result) -> None:
        self.__queue.put(result)

    def __get_results(self) -> Optional[list[Any]]:
        if not self.__current_execution_id:
            raise ProgrammingError("No query has been executed yet")
        if self.__results is not None:
            return self.__results

        result = self.__queue.get()
        if isinstance(result, DatabaseError):
            raise result
        self.__rowcount = len(result)
        self.__results = result
        return self.__results

    def execute(self, operation: str, parameters: dict[str, Any] = None):
        if self.__current_execution_id:
            self.__cancel_fn(self.__current_execution_id)

        self.__results = None
        self.__current_row = 0
        self.__rowcount = -1

        sql = operation.format(**(parameters or {}))
        self.__current_execution_id = self.__exec_fn(sql, self.__on_execution_result)

    def executemany(self, operation: str, seq_of_parameters: list[dict[str, Any]]):
        raise NotImplementedError

    def fetchone(self):
        results = self.__get_results()[self.__current_row :]
        if not results:
            return None
        self.__current_row += 1
        return results[0]

    def fetchmany(self, size: int = None):
        size = size or self.arraysize
        results = self.__get_results()[self.__current_row : self.__current_row + size]
        self.__current_row += size
        return results

    def fetchall(self):
        return self.__get_results()[self.__current_row :]

    def close(self):
        """Close the cursor."""
        pass

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
