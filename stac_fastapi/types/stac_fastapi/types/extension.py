"""base api extension."""
import abc
from typing import List, Optional

import attr
from fastapi import FastAPI
from pydantic import BaseModel


@attr.s
class ApiExtension(abc.ABC):
    """Abstract base class for defining API extensions."""

    conformance_classes: List[str] = attr.ib()
    GET = None
    POST = None

    def get_request_model(self, verb: Optional[str] = "GET") -> Optional[BaseModel]:
        """Return the request model for the extension.method.

        The model can differ based on HTTP verb
        """
        return getattr(self, verb)

    @abc.abstractmethod
    def register(self, app: FastAPI) -> None:
        """Register the extension with a FastAPI application.

        Args:
            app: target FastAPI application.

        Returns:
            None
        """
        pass
