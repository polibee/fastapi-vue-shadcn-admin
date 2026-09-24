from .contract import ActionDefinition, BulkActionDefinition, FieldDefinition, FieldType, ResourceDefinition


USER_RESOURCE = ResourceDefinition(
    name="users",
    label="users.label",
    label_plural="users.labelPlural",
    api_base="/api/v1/users",
    route="/admin/users",
    permissions={"view": "users.view", "create": "users.create", "update": "users.update", "delete": "users.delete"},
    fields=(
        FieldDefinition("id", FieldType.text, "users.id", required=True, nullable=False, readonly=True, sortable=True),
        FieldDefinition("username", FieldType.text, "users.username", required=True, nullable=False, searchable=True, sortable=True, filterable=True),
        FieldDefinition("email", FieldType.email, "users.email", required=True, nullable=False, searchable=True, sortable=True),
        FieldDefinition("password", FieldType.password, "users.password", database_name="password_hash", required=True, nullable=False),
        FieldDefinition("is_active", FieldType.boolean, "users.status", required=True, nullable=False, readonly=True, filterable=True),
    ),
    actions=(
        ActionDefinition("edit_roles", "users.editRoles", "users.update", "ghost", "edit"),
        ActionDefinition("delete", "users.delete", "users.delete", "ghost", "delete"),
    ),
    bulk_actions=(BulkActionDefinition("delete_selected", "users.delete", "users.delete", "delete"),),
)

ROLE_RESOURCE = ResourceDefinition(
    name="roles",
    label="roles.label",
    label_plural="roles.labelPlural",
    api_base="/api/v1/roles",
    route="/admin/roles",
    permissions={"view": "roles.view", "create": "roles.create", "update": "roles.update", "delete": "roles.delete"},
    fields=(
        FieldDefinition("id", FieldType.text, "roles.id", required=True, nullable=False, readonly=True, sortable=True),
        FieldDefinition("name", FieldType.text, "roles.name", required=True, nullable=False, searchable=True, sortable=True),
        FieldDefinition("description", FieldType.text, "roles.descriptionField", searchable=True),
    ),
    actions=(
        ActionDefinition("edit_permissions", "roles.editPermissions", "roles.update", "ghost", "edit"),
        ActionDefinition("edit_scope", "roles.editScope", "roles.update", "ghost", "edit"),
        ActionDefinition("delete", "roles.delete", "roles.delete", "ghost", "delete"),
    ),
    bulk_actions=(BulkActionDefinition("delete_selected", "roles.delete", "roles.delete", "delete"),),
)

RESOURCE_DEFINITIONS = {USER_RESOURCE.name: USER_RESOURCE, ROLE_RESOURCE.name: ROLE_RESOURCE}

DEPARTMENT_RESOURCE = ResourceDefinition(
    name="departments",
    label="departments.label",
    label_plural="departments.labelPlural",
    api_base="/api/v1/departments",
    route="/admin/departments",
    permissions={"view": "departments.view", "create": "departments.create", "update": "departments.update", "delete": "departments.delete"},
    fields=(
        FieldDefinition("id", FieldType.text, "departments.id", required=True, nullable=False, readonly=True, sortable=True),
        FieldDefinition("name", FieldType.text, "departments.name", required=True, nullable=False, searchable=True, sortable=True),
        FieldDefinition("code", FieldType.text, "departments.code", required=True, nullable=False, searchable=True, sortable=True),
        FieldDefinition("description", FieldType.text, "departments.description"),
        FieldDefinition("is_active", FieldType.boolean, "departments.status", required=True, nullable=False, filterable=True),
    ),
    actions=(ActionDefinition("edit", "common.edit", "departments.update", "ghost", "edit"), ActionDefinition("delete", "common.delete", "departments.delete", "ghost", "delete")),
    bulk_actions=(BulkActionDefinition("delete_selected", "common.delete", "departments.delete", "delete"),),
)

RESOURCE_DEFINITIONS[DEPARTMENT_RESOURCE.name] = DEPARTMENT_RESOURCE
