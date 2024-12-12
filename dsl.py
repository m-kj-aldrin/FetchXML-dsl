from __future__ import annotations
from typing import List, overload, TypeVar, Union
from xml.dom.minidom import parseString

EntityOrLinkEntity = Union["Entity", "LinkEntity"]

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


class Condition:
    def __init__(self, attribute: str, operator: str, value: str):
        self.attribute = attribute
        self.operator = operator
        self.value = value

    @property
    def xml(self) -> str:
        return f'<condition attribute="{self.attribute}" operator="{self.operator}" value="{self.value}"/>'


class Filter:
    def __init__(self, filter_type: str):
        self.filter_type = filter_type
        self.conditions: List[Condition] = []

    def __add__(self, other: Condition) -> Filter:
        if not isinstance(other, Condition):
            raise TypeError(f"Cannot add {type(other)} to Filter")
        self.conditions.append(other)
        return self

    @property
    def xml(self) -> str:
        conditions_xml = " ".join(cond.xml for cond in self.conditions)
        return f'<filter type="{self.filter_type}">{conditions_xml}</filter>'


class LinkEntity:
    def __init__(self, name: str):
        self.name = name
        self.attributes: List[Attribute] = []
        self.orders: List[Order] = []
        self.filters: List[Filter] = []
        self.link_entities: List[LinkEntity] = []

    @overload
    def __add__(self, other: Attribute) -> LinkEntity: ...
    @overload
    def __add__(self, other: Order) -> LinkEntity: ...
    @overload
    def __add__(self, other: Filter) -> LinkEntity: ...
    @overload
    def __add__(self, other: LinkEntity) -> LinkEntity: ...
    def __add__(self, other: Attribute | Order | Filter | LinkEntity) -> LinkEntity:
        if isinstance(other, Attribute):
            self.attributes.append(other)
        elif isinstance(other, Order):
            self.orders.append(other)
        elif isinstance(other, Filter):
            self.filters.append(other)
        elif isinstance(other, LinkEntity):
            self.link_entities.append(other)
        else:
            raise TypeError(f"Cannot add {type(other)} to LinkEntity")
        return self

    @property
    def xml(self) -> str:
        parts = []
        parts.extend(attr.xml for attr in self.attributes)
        parts.extend(order.xml for order in self.orders)
        parts.extend(filt.xml for filt in self.filters)
        parts.extend(link.xml for link in self.link_entities)
        return f'<link-entity name="{self.name}">{" ".join(parts)}</link-entity>'


class Entity:
    def __init__(self, name: str):
        self.name = name
        self.attributes: List[Attribute] = []
        self.orders: List[Order] = []
        self.filters: List[Filter] = []
        self.link_entities: List[LinkEntity] = []

    @overload
    def __add__(self: Self, other: Attribute) -> Self: ...
    @overload
    def __add__(self: Self, other: Order) -> Self: ...
    @overload
    def __add__(self: Self, other: Filter) -> Self: ...
    @overload
    def __add__(self: Self, other: LinkEntity) -> Self: ...
    def __add__(self: Self, other: Attribute | Order | Filter | LinkEntity) -> Self:
        if isinstance(other, Attribute):
            self.attributes.append(other)
        elif isinstance(other, Order):
            self.orders.append(other)
        elif isinstance(other, Filter):
            self.filters.append(other)
        elif isinstance(other, LinkEntity):
            self.link_entities.append(other)
        else:
            raise TypeError(f"Cannot add {type(other)} to Entity")
        return self

    @property
    def xml(self) -> str:
        parts = []
        parts.extend(attr.xml for attr in self.attributes)
        parts.extend(order.xml for order in self.orders)
        parts.extend(filt.xml for filt in self.filters)
        parts.extend(link.xml for link in self.link_entities)
        return f"<entity>{' '.join(parts)}</entity>"

    def pretty(self) -> str:
        """Returns a pretty-printed version of the XML"""
        dom = parseString(self.xml)
        pretty_xml = dom.toprettyxml(indent="  ")
        lines = pretty_xml.split("\n")[1:]  # Skip XML declaration
        lines = [line for line in lines if line.strip()]
        return "\n".join(lines)


# Example usage
entity = (
    Entity("incidents")
    + Attribute("createdon")
    + Attribute("incidentid")
    + Order("createdon", False)
    + (Filter("and") + Condition("createdon", "gt", "2024-10-01"))
    + (
        LinkEntity("contact")
        + Attribute("fullname")
        + Order("fullname", False)
        + (LinkEntity("incident") + Attribute("ticketnumber"))
    )
)

print(entity.pretty())
