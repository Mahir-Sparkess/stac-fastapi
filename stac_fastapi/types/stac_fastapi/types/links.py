"""link helpers."""

from typing import Dict, List, Optional
from urllib.parse import urljoin

import attr
from stac_pydantic.links import Link, Relations
from stac_pydantic.shared import MimeTypes

# These can be inferred from the item/collection so they aren't included in the database
# Instead they are dynamically generated when querying the database using the classes defined below
INFERRED_LINK_RELS = ["self", "item", "parent", "collection", "root"]


def filter_links(links: List[Dict]) -> List[Dict]:
    """Remove inferred links."""
    return [link for link in links if link["rel"] not in INFERRED_LINK_RELS]


@attr.s
class BaseLinks:
    """Create inferred links common to collections and items."""

    collection_id: Optional[str] = attr.ib()
    base_url: str = attr.ib()

    def root(self) -> Link:
        """Return the catalog root."""
        return Link(rel=Relations.root, type=MimeTypes.json, href=self.base_url)


@attr.s
class CollectionLinks(BaseLinks):
    """Create inferred links specific to collections."""

    def self(self) -> Link:
        """Create the `self` link."""
        return Link(
            rel=Relations.self,
            type=MimeTypes.json,
            href=urljoin(self.base_url, f"collections/{self.collection_id}"),
        )

    def parent(self) -> Link:
        """Create the `parent` link."""
        return Link(rel=Relations.parent, type=MimeTypes.json, href=self.base_url)

    def items(self) -> Link:
        """Create the `items` link."""
        return Link(
            rel="items",
            type=MimeTypes.geojson,
            href=urljoin(self.base_url, f"collections/{self.collection_id}/items"),
        )

    def create_links(self) -> List[Link]:
        """Return all inferred links."""
        return [self.self(), self.parent(), self.items(), self.root()]


@attr.s
class ItemLinks(BaseLinks):
    """Create inferred links specific to items."""

    item_id: str = attr.ib()

    def self(self) -> Link:
        """Create the `self` link."""
        return Link(
            rel=Relations.self,
            type=MimeTypes.geojson,
            href=urljoin(
                self.base_url, f"collections/{self.collection_id}/items/{self.item_id}"
            ),
        )

    def parent(self) -> Link:
        """Create the `parent` link."""
        return Link(
            rel=Relations.parent,
            type=MimeTypes.json,
            href=urljoin(self.base_url, f"collections/{self.collection_id}"),
        )

    def collection(self) -> Link:
        """Create the `collection` link."""
        return Link(
            rel=Relations.collection,
            type=MimeTypes.json,
            href=urljoin(self.base_url, f"collections/{self.collection_id}"),
        )

    def tiles(self) -> Link:
        """Create the `tiles` link."""
        return Link(
            rel=Relations.alternate,
            type=MimeTypes.json,
            title="tiles",
            href=urljoin(
                self.base_url,
                f"collections/{self.collection_id}/items/{self.item_id}/tiles",
            ),
        )

    def create_links(self) -> List[Link]:
        """Return all inferred links."""
        links = [
            self.self(),
            self.parent(),
            self.collection(),
            self.root(),
        ]
        # TODO: Don't always append tiles link
        # TODO: Look at using inheritence mechanism to support changes to the
        # core client and response.
        # links.append(self.tiles())
        return links
