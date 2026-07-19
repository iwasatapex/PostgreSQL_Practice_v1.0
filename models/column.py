from dataclasses import dataclass


@dataclass
class Column:
    """
    Represents a database column.
    """

    name: str
    data_type: str
    nullable: bool

    default: str | None = None

    primary_key: bool = False

    foreign_key: bool = False

    unique: bool = False
