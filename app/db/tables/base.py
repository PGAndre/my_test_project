from sqlalchemy import inspect
from sqlalchemy.orm import as_declarative
from sqlalchemy.orm.decl_api import registry


mapper_registry = registry()
metadata = mapper_registry.metadata


@as_declarative(metadata=metadata)
class Base:
    def __iter__(self):
        obj_dict = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        yield from obj_dict.items()


def get_metadata():
    """Import all project tables"""

    return mapper_registry.metadata
