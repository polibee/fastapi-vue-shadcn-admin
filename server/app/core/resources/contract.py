from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class FieldType(StrEnum):
    text = "text"
    email = "email"
    password = "password"
    boolean = "boolean"
    datetime = "datetime"


@dataclass(frozen=True)
class FieldDefinition:
    name: str
    type: FieldType
    label: str
    database_name: str | None = None
    required: bool = False
    nullable: bool = True
    readonly: bool = False
    searchable: bool = False
    sortable: bool = False
    filterable: bool = False


@dataclass(frozen=True)
class ResourceFeatures:
    create: bool = True
    update: bool = True
    delete: bool = True
    detail: bool = True
    search: bool = True
    filters: bool = True
    export: bool = False
    import_: bool = False


@dataclass(frozen=True)
class ActionDefinition:
    name: str
    label: str
    permission: str
    variant: str = "default"
    icon: str = "more"


@dataclass(frozen=True)
class BulkActionDefinition:
    name: str
    label: str
    permission: str
    icon: str = "more"


@dataclass(frozen=True)
class ResourceDefinition:
    name: str
    label: str
    label_plural: str
    api_base: str
    permissions: dict[str, str]
    fields: tuple[FieldDefinition, ...] = field(default_factory=tuple)
    actions: tuple[ActionDefinition, ...] = field(default_factory=tuple)
    bulk_actions: tuple[BulkActionDefinition, ...] = field(default_factory=tuple)
    features: ResourceFeatures = field(default_factory=ResourceFeatures)
    route: str | None = None


def compile_manifest(resource: ResourceDefinition) -> dict[str, Any]:
    return {
        "schemaVersion": "1.0",
        "name": resource.name,
        "label": resource.label,
        "labelPlural": resource.label_plural,
        "routes": {"list": resource.route or f"/{resource.name}"},
        "api": {"base": resource.api_base},
        "permissions": resource.permissions,
        "features": {("import" if key == "import_" else key): value for key, value in asdict(resource.features).items()},
        "query": {
            "searchFields": [field.name for field in resource.fields if field.searchable],
            "filterFields": [field.name for field in resource.fields if field.filterable],
            "sortFields": [field.name for field in resource.fields if field.sortable],
            "defaultSort": {"field": "id", "direction": "asc"},
        },
        "fields": [
            {"name": field.name, "type": field.type.value, **{key: value for key, value in asdict(field).items() if key not in {"name", "type"} and value is not None}}
            for field in resource.fields
        ],
        "table": {"columns": [field.name for field in resource.fields if field.name != "id" and not field.readonly]},
        "forms": {"create": {"fields": [field.name for field in resource.fields if not field.readonly]}, "edit": {"fields": [field.name for field in resource.fields if not field.readonly]}},
        "actions": [asdict(action) for action in resource.actions],
        "bulkActions": [asdict(action) for action in resource.bulk_actions],
        "relations": [],
    }
