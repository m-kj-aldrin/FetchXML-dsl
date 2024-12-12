from __future__ import annotations
from typing import List, overload, TypeVar
from xml.dom.minidom import Attr, parseString

Self = TypeVar("Self", bound="Entity")


class Attribute:
    def __init__(self, name: str):
        self.name = name

    @property
    def xml(self) -> str:
        return f'<attribute name="{self.name}"/>'


class Order:
    def __init__(self, name: str, descending: bool = False):
        self.name = name
        self.descending = descending

    @property
    def xml(self) -> str:
        return f'<order attribute="{self.name}" descending="{str(self.descending).lower()}"/>'


class LinkEntity:
    def __init__(self, name: str):
        self.name = name
        self.attributes: List[Attribute] = []
        self.orders: List[Order] = []

    @property
    def xml(self) -> str:
        parts = []
        parts.extend(attr.xml for attr in self.attributes)
        parts.extend(order.xml for order in self.orders)
        return f'<link-entity name="{self.name}">{" ".join(parts)}</link-entity>'

    @overload
    def __add__(self, other: Attribute) -> LinkEntity: ...
    @overload
    def __add__(self, other: Order) -> LinkEntity: ...

    def __add__(self, other: Attribute | Order) -> LinkEntity:
        if isinstance(other, Attribute):
            self.attributes.append(other)
            return self
        elif isinstance(other, Order):
            self.orders.append(other)
            return self
        raise TypeError(f"Cannot add LinkEntity with {type(other)}")


class Entity:
    def __init__(self, name: str):
        self.name = name
        self.attributes: List[Attribute] = []
        self.link_entities: List[LinkEntity] = []
        self.orders: List[Order] = []

    @overload
    def __add__(self: Self, other: Attribute) -> Self: ...
    @overload
    def __add__(self: Self, other: Order) -> Self: ...
    @overload
    def __add__(self, other: LinkEntity) -> LinkEntity: ...

    def __add__(self: Self, other: Attribute | Order | LinkEntity) -> Self | LinkEntity:
        if isinstance(other, Attribute):
            self.attributes.append(other)
            # Return self, which is Self (an Entity)
            return self
        elif isinstance(other, Order):
            self.orders.append(other)
            # Return self, which is Self (an Entity)
            return self
        elif isinstance(other, LinkEntity):
            self.link_entities.append(other)
            # Return the LinkEntity
            return other
        raise TypeError(f"Cannot add Entity with {type(other)}")

    @property
    def xml(self) -> str:
        parts = []
        parts.extend(attr.xml for attr in self.attributes)
        parts.extend(order.xml for order in self.orders)
        parts.extend(link.xml for link in self.link_entities)
        return f"<entity>{' '.join(parts)}</entity>"

    def pretty(self) -> str:
        """Returns a pretty-printed version of the XML"""
        dom = parseString(self.xml)
        pretty_xml = dom.toprettyxml(indent="  ")
        lines = pretty_xml.split("\n")[1:]  # Skip XML declaration
        lines = [line for line in lines if line.strip()]
        return "\n".join(lines)


entity = (
    Entity("incidents")
    + Attribute("createdon")
    + Attribute("incidentid")
    + Order("createdon", False)
)

link_entity = (
    entity + LinkEntity("contact") + Attribute("fullname") + Order("fullname", False)
)


print(entity.pretty())
