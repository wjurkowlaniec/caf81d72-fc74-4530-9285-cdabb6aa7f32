from django.http import JsonResponse
from uuid import uuid4
# Create your views here.


from django.db import models, OperationalError
from django.db import connection
from .models import DynamicTableTable

FIELD_MAPPING = {
    "text": models.CharField(max_length=20000),
    "number": models.FloatField(),
    "boolean": models.BooleanField(),
}

"""
Example mapping:
{
    "name": "text",
    "age": "number",
    "is_active": "boolean"
}

{
    "name": "text",
    "age": "number",
}

{
    "name": "number",
    "age": "number",
}

"""

def schema_diff(schema, schema2):
    """
    Returns the difference between two schema dictionaries.
    """
    added_fields = {}
    removed_fields = {}
    changed_fields = {}
    for field_name, field_type in schema.items():
        if field_name not in schema2:
            removed_fields[field_name] = field_type
        elif schema2[field_name] != field_type:
            changed_fields[field_name] = field_type
    for field_name, field_type in schema2.items():
        if field_name not in schema:
            added_fields[field_name] = field_type
    return added_fields, removed_fields, changed_fields


def get_fields_mapping(attributes: dict):
    """
    Returns a dictionary of field names and field types for the given attributes.
    """
    fields = {}
    for field_name, field_type in attributes.items():
        if field_type not in FIELD_MAPPING:
            raise Exception("Invalid field type for field: {}".format(field_name))
        fields[field_name] = FIELD_MAPPING[field_type]
    return fields

def get_single_field_mapping(name, type_text):
    if type_text not in FIELD_MAPPING:
        raise Exception("Invalid field type for field: {}".format(name))
    field = FIELD_MAPPING[type_text]
    field.name=name
    field.db_column = name
    field.concrete = True
    return field


def create_dynamic_model(table_record: DynamicTableTable):
    """
    Creates a dynamic Django model with the given name and fields.
    """
    attrs = get_fields_mapping(table_record.schema)
    attrs["__module__"] = "dynamictables.models"
    dynamic_model = type(table_record.uuid, (models.Model,), attrs)
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(dynamic_model)
            table_record.save()
        except OperationalError as exception:
            print("create_dynamic_model: OperationalError: {}".format(exception))
            raise Exception("Could not create a table")
    return dynamic_model


def alter_dynamic_model(table_record: DynamicTableTable, new_schema: dict):
    """
    Alters a dynamic Django model with the given name and fields.
    """
    # Define the fields for the model
    added_fields, removed_fields, changed_fields = schema_diff(table_record.schema, new_schema)
    original_attrs = get_fields_mapping(table_record.schema)
    original_attrs["__module__"] = "dynamictables.models"
    dynamic_model = type(table_record.uuid, (models.Model,), original_attrs)
    with connection.schema_editor() as schema_editor:
        try:
            for added_field in added_fields:
                print(f"added_field: {added_field}")
                field = get_single_field_mapping(added_field, added_fields[added_field])
                schema_editor.add_field(dynamic_model, field)
                # TODO fix FloatField not adding (no error given, doesn't add)
            for removed_field in removed_fields:
                print(f"removed_field: {removed_field}")
                field = get_single_field_mapping(removed_field, added_fields[removed_field])
                schema_editor.remove_field(dynamic_model, field)
            for changed_field in changed_fields:
                print(f"changed_field: {changed_field} NOT IMPLEMENTED")
        except Exception as exc:
            print("alter_dynamic_model: Exception: {}".format(exc))
            raise
    return dynamic_model

def create_table_view(request):
    # example payload for testing
    fields = {
        'name': 'text',
        'is_active': 'boolean'
    }
    uuid = str(uuid4())
    table = DynamicTableTable(uuid=uuid, schema = fields)
    create_dynamic_model(table)
    return JsonResponse({"uuid": uuid})



def alter_table_view(request, uuid):
    # example payload for testing
    fields = {
        'name': 'text',
        'is_active': 'boolean',
        'age': 'number',
        'piwo': "text",
    }
    table = DynamicTableTable.objects.get(uuid=uuid)
    alter_dynamic_model(table, fields)
    return JsonResponse({"uuid": uuid})

