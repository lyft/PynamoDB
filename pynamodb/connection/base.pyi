from typing import Any, Dict, Iterator, MutableMapping, Optional, Sequence, Text, List

import botocore.session
from botocore.awsrequest import AWSPreparedRequest

from pynamodb.expressions.condition import Condition
from pynamodb.expressions.update import Action


BOTOCORE_EXCEPTIONS: Any
log: Any

class MetaTable:
    data: Dict
    def __init__(self, data: Dict) -> None: ...
    @property
    def range_keyname(self) -> Optional[Text]: ...
    @property
    def hash_keyname(self) -> Text: ...
    def get_index_hash_keyname(self, index_name: Text) -> Optional[Text]: ...
    def get_item_attribute_map(self, attributes, item_key: Any = ..., pythonic_key: bool = ...): ...
    def get_attribute_type(self, attribute_name, value: Optional[Any] = ...): ...
    def get_identifier_map(self, hash_key, range_key: Optional[Any] = ..., key: Any = ...): ...
    def get_exclusive_start_key_map(self, exclusive_start_key): ...

class Connection:
    host: Any
    region: Any
    session_cls: Any
    def __init__(
        self,
        region: Optional[Any] = ...,
        host: Optional[Any] = ...,
        connect_timeout_seconds: Optional[float] = ...,
        read_timeout_seconds: Optional[float] = ...,
        max_retry_attempts: Optional[int] = ...,
        base_backoff_ms: Optional[int] = ...,
        max_pool_connections: Optional[int] = ...,
        extra_headers: Optional[MutableMapping[Text, Text]] = ...,
    ) -> None: ...
    def dispatch(self, operation_name, operation_kwargs): ...
    @property
    def session(self) -> botocore.session.Session: ...
    @property
    def client(self): ...
    def get_meta_table(self, table_name: Text, refresh: bool = ...): ...
    def create_table(self, table_name: Text, attribute_definitions: Optional[Any] = ..., key_schema: Optional[Any] = ..., read_capacity_units: Optional[Any] = ..., write_capacity_units: Optional[Any] = ..., global_secondary_indexes: Optional[Any] = ..., local_secondary_indexes: Optional[Any] = ..., stream_specification: Optional[Any] = ...): ...
    def delete_table(self, table_name: Text): ...
    def update_table(self, table_name: Text, read_capacity_units: Optional[Any] = ..., write_capacity_units: Optional[Any] = ..., global_secondary_index_updates: Optional[Any] = ...): ...
    def list_tables(self, exclusive_start_table_name: Optional[Any] = ..., limit: Optional[Any] = ...): ...
    def describe_table(self, table_name: Text): ...
    def get_item_attribute_map(self, table_name: Text, attributes, item_key: Any = ..., pythonic_key: bool = ...): ...
    def parse_attribute(self, attribute, return_type: bool = ...): ...
    def get_attribute_type(self, table_name: Text, attribute_name, value: Optional[Any] = ...): ...
    def get_identifier_map(self, table_name: Text, hash_key, range_key: Optional[Any] = ..., key: Any = ...): ...
    def get_consumed_capacity_map(self, return_consumed_capacity): ...
    def get_return_values_map(self, return_values): ...
    def get_item_collection_map(self, return_item_collection_metrics): ...
    def get_exclusive_start_key_map(self, table_name: Text, exclusive_start_key): ...

    def get_operation_kwargs_for_condition_check(
        self,
        table_name: Text,
        condition: Optional[Condition],
        hash_key: Any,
        range_key: Optional[Any] = ...,
        return_values: Optional[Any] = ...
    ) -> Dict: ...
    def get_operation_kwargs_for_delete_item(
        self,
        table_name: Text,
        hash_key,
        range_key: Optional[Any] = ...,
        condition: Optional[Condition] = ...,
        return_values: Optional[Any] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...
    ) -> Dict: ...
    def get_operation_kwargs_for_get_item(
        self,
        table_name: Text,
        hash_key,
        range_key: Optional[Any] = ...,
        consistent_read: bool = ...,
        attributes_to_get: Optional[Any] = ...
    ) -> Dict: ...
    def get_operation_kwargs_for_put_item(
        self,
        table_name: Text,
        hash_key,
        range_key: Optional[Any] = ...,
        attributes: Optional[Any] = ...,
        condition: Optional[Condition] = ...,
        return_values: Optional[Any] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...
    ) -> Dict: ...
    def get_operation_kwargs_for_update_item(
        self,
        table_name: Text,
        hash_key,
        range_key: Optional[Any] = ...,
        actions: Optional[Sequence[Action]] = ...,
        condition: Optional[Condition] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...,
        return_values: Optional[Any] = ...
    ) -> Dict: ...

    def delete_item(
        self,
        table_name: Text,
        hash_key,
        range_key: Optional[Any] = ...,
        condition: Optional[Condition] = ...,
        return_values: Optional[Any] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...
    ) -> Dict: ...

    def update_item(
        self,
        table_name: Text,
        hash_key,
        range_key: Optional[Any] = ...,
        actions: Optional[Sequence[Action]] = ...,
        condition: Optional[Condition] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...,
        return_values: Optional[Any] = ...
    ) -> Dict: ...

    def put_item(
        self,
        table_name: Text,
        hash_key,
        range_key: Optional[Any] = ...,
        attributes: Optional[Any] = ...,
        condition: Optional[Condition] = ...,
        return_values: Optional[Any] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...
    ) -> Dict: ...

    def transact_write_items(
        self,
        condition_check_items: List[Dict],
        delete_items: List[Dict],
        put_items: List[Dict],
        update_items: List[Dict],
        client_request_token: Optional[Text] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...
    ) -> Dict: ...
    def transact_get_items(
        self,
        get_items: List[Dict],
        return_consumed_capacity: Optional[Any] = ...
    ) -> Dict: ...

    def batch_write_item(self, table_name: Text, put_items: Optional[Any] = ..., delete_items: Optional[Any] = ..., return_consumed_capacity: Optional[Any] = ..., return_item_collection_metrics: Optional[Any] = ...): ...
    def batch_get_item(self, table_name: Text, keys, consistent_read: Optional[Any] = ..., return_consumed_capacity: Optional[Any] = ..., attributes_to_get: Optional[Any] = ...): ...
    def get_item(self, table_name: Text, hash_key, range_key: Optional[Any] = ..., consistent_read: bool = ..., attributes_to_get: Optional[Any] = ...): ...

    def scan(
        self,
        table_name: Text = ...,
        attributes_to_get: Optional[Any] = ...,
        limit: Optional[Any] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        exclusive_start_key: Optional[Any] = ...,
        segment: Optional[str] = ...,
        total_segments: Optional[int] = ...,
    ) -> Dict: ...

    def query(
        self,
        table_name: Text,
        hash_key,
        range_key_condition: Optional[Condition] = ...,
        attributes_to_get: Optional[Any] = ...,
        consistent_read: bool = ...,
        exclusive_start_key: Optional[Any] = ...,
        index_name: Optional[Any] = ...,
        limit: Optional[Any] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        scan_index_forward: Optional[Any] = ...,
        select: Optional[Any] = ...
    ): ...

    def _create_prepared_request(self, params: Dict, operation_model: Optional[Any] = ...) -> AWSPreparedRequest: ...
