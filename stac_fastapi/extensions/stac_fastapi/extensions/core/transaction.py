"""transaction extension."""

from typing import Callable, List, Type, Union

import attr
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response

from stac_fastapi.api.models import APIRequest
from stac_fastapi.api.routes import create_async_endpoint, create_sync_endpoint
from stac_fastapi.types import stac as stac_types
from stac_fastapi.types.config import ApiSettings
from stac_fastapi.types.core import AsyncBaseTransactionsClient, BaseTransactionsClient
from stac_fastapi.types.extension import ApiExtension


@attr.s
class TransactionExtension(ApiExtension):
    """Transaction Extension.

    The transaction extension adds several endpoints which allow the creation, deletion, and updating of items and
    collections:
        POST /collections
        PUT /collections/{collectionId}
        DELETE /collections/{collectionId}
        POST /collections/{collectionId}/items
        PUT /collections/{collectionId}/items
        DELETE /collections/{collectionId}/items

    https://github.com/radiantearth/stac-api-spec/blob/master/ogcapi-features/extensions/transaction/README.md

    Attributes:
        client: CRUD application logic
    """

    client: Union[AsyncBaseTransactionsClient, BaseTransactionsClient] = attr.ib()
    settings: ApiSettings = attr.ib()
    conformance_classes: List[str] = attr.ib(default=list())
    router: APIRouter = attr.ib(factory=APIRouter)
    response_class: Type[Response] = attr.ib(default=JSONResponse)

    def _create_endpoint(
        self,
        func: Callable,
        request_type: Union[
            Type[APIRequest],
            Type[BaseModel],
            Type[stac_types.Item],
            Type[stac_types.Collection],
        ],
    ) -> Callable:
        """Create a FastAPI endpoint."""
        if isinstance(self.client, AsyncBaseTransactionsClient):
            return create_async_endpoint(
                func, request_type, response_class=self.response_class
            )
        elif isinstance(self.client, BaseTransactionsClient):
            return create_sync_endpoint(
                func, request_type, response_class=self.response_class
            )
        raise NotImplementedError

    def register_create_item(self):
        """Register create item endpoint (POST /collections/{collection_id}/items)."""
        self.router.add_api_route(
            name="Create Item",
            path="/collections/{collection_id}/items",
            methods=["POST"],
            endpoint=self.client.create_item,
        )

    def register_update_item(self):
        """Register update item endpoint (PUT /collections/{collection_id}/items/{item_id})."""
        self.router.add_api_route(
            name="Update Item",
            path="/collections/{collection_id}/items/{item_id}",
            methods=["PUT"],
            endpoint=self.client.update_item,
        )

    def register_delete_item(self):
        """Register delete item endpoint (DELETE /collections/{collection_id}/items/{item_id})."""
        self.router.add_api_route(
            name="Delete Item",
            path="/collections/{collection_id}/items/{item_id}",
            methods=["DELETE"],
            endpoint=self.client.delete_item,
        )

    def register_create_collection(self):
        """Register create collection endpoint (POST /collections)."""
        self.router.add_api_route(
            name="Create Collection",
            path="/collections",
            methods=["POST"],
            endpoint=self.client.create_collection,
        )

    def register_update_collection(self):
        """Register update collection endpoint (PUT /collections)."""
        self.router.add_api_route(
            name="Update Collection",
            path="/collections/{collection_id}",
            methods=["PUT"],
            endpoint=self.client.update_collection,
        )

    def register_delete_collection(self):
        """Register delete collection endpoint (DELETE /collections/{collection_id})."""
        self.router.add_api_route(
            name="Delete Collection",
            path="/collections/{collection_id}",
            methods=["DELETE"],
            endpoint=self.client.delete_collection,
        )

    def register(self, app: FastAPI) -> None:
        """Register the extension with a FastAPI application.

        Args:
            app: target FastAPI application.

        Returns:
            None
        """
        self.register_create_item()
        self.register_update_item()
        self.register_delete_item()
        self.register_create_collection()
        self.register_update_collection()
        self.register_delete_collection()
        app.include_router(self.router, tags=["Transaction Extension"])
