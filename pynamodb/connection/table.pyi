from typing import Any, Dict, Iterator, MutableMapping, Optional, Sequence, Text

from pynamodb.expressions.condition import Condition


class TableConnection:
    table_name: Any
    connection: Any
    def __init__(
        self,
        table_name,
        region: Optional[Any] = ...,
        host: Optional[Any] = ...,
        connect_timeout_seconds: Optional[float] = ...,
        read_timeout_seconds: Optional[float] = ...,
        max_retry_attempts: Optional[int] = ...,
        base_backoff_ms: Optional[int] = ...,
        max_pool_connections: Optional[int] = ...,
        extra_headers: Optional[MutableMapping[Text, Text]] = ...,
        aws_access_key_id: Optional[str] = ...,
        aws_secret_access_key: Optional[str] = ...,
    ) -> None: ...

    def get_operation_kwargs_for_delete_item(self, *args, **kwargs) -> Dict: ...
    def delete_item(
        self,
        hash_key,
        range_key: Optional[Any] = ...,
        condition: Optional[Condition] = ...,
        expected: Optional[Any] = ...,
        conditional_operator: Optional[Any] = ...,
        return_values: Optional[Any] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...
    ) -> Dict: ...

    def get_operation_kwargs_for_update_item(self, *args, **kwargs) -> Dict: ...
    def update_item(
        self,
        hash_key,
        range_key: Optional[Any] = ...,
        attribute_updates: Optional[Any] = ...,
        condition: Optional[Condition] = ...,
        expected: Optional[Any] = ...,
        conditional_operator: Optional[Any] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...,
        return_values: Optional[Any] = ...
    ) -> Dict: ...

    def get_operation_kwargs_for_condition_check(
            self,
            table_name: Text,
            condition: Optional[Condition],
            hash_key: Any,
            range_key: Optional[Any] = ...,
            return_values: Optional[Any] = ...
    ) -> Dict: ...

    def get_operation_kwargs_for_put_item(self, *args, **kwargs) -> Dict: ...
    def put_item(
        self,
        hash_key,
        range_key: Optional[Any] = ...,
        attributes: Optional[Any] = ...,
        condition: Optional[Condition] = ...,
        expected: Optional[Any] = ...,
        conditional_operator: Optional[Any] = ...,
        return_values: Optional[Any] = ...,
        return_consumed_capacity: Optional[Any] = ...,
        return_item_collection_metrics: Optional[Any] = ...
    ) -> Dict: ...

    def batch_write_item(self, put_items: Optional[Any] = ..., delete_items: Optional[Any] = ..., return_consumed_capacity: Optional[Any] = ..., return_item_collection_metrics: Optional[Any] = ...): ...
    def batch_get_item(self, keys, consistent_read: Optional[Any] = ..., return_consumed_capacity: Optional[Any] = ..., attributes_to_get: Optional[Any] = ...): ...
    def get_item(self, hash_key, range_key: Optional[Any] = ..., consistent_read: bool = ..., attributes_to_get: Optional[Any] = ...): ...

    def rate_limited_scan(
        self,
        filter_condition: Optional[Condition] = ...,
        attributes_to_get: Optional[Sequence[str]] = ...,
        page_size: Optional[int] = ...,
        limit: Optional[int] = ...,
        conditional_operator: Optional[Text] = ...,
        scan_filter: Optional[Dict] = ...,
        exclusive_start_key: Optional[Any] = ...,
        segment: Optional[int] = ...,
        total_segments: Optional[int] = ...,
        timeout_seconds: Optional[float] = ...,
        read_capacity_to_consume_per_second: int = ...,
        allow_rate_limited_scan_without_consumed_capacity: Optional[bool] = ...,
        max_sleep_between_retry: float = ...,
        max_consecutive_exceptions: int = ...,
        consistent_read: Optional[bool] = ...,
        index_name: Optional[str] = ...
    ) -> Iterator[Dict]: ...

    def scan(self, attributes_to_get: Optional[Any] = ..., limit: Optional[Any] = ..., conditional_operator: Optional[Any] = ..., scan_filter: Optional[Any] = ..., return_consumed_capacity: Optional[Any] = ..., segment: Optional[Any] = ..., total_segments: Optional[Any] = ..., exclusive_start_key: Optional[Any] = ...): ...
    def query(self, hash_key, attributes_to_get: Optional[Any] = ..., consistent_read: bool = ..., exclusive_start_key: Optional[Any] = ..., index_name: Optional[Any] = ..., key_conditions: Optional[Any] = ..., query_filters: Optional[Any] = ..., limit: Optional[Any] = ..., return_consumed_capacity: Optional[Any] = ..., scan_index_forward: Optional[Any] = ..., conditional_operator: Optional[Any] = ..., select: Optional[Any] = ...): ...
    def describe_table(self): ...
    def delete_table(self): ...
    def update_table(self, read_capacity_units: Optional[Any] = ..., write_capacity_units: Optional[Any] = ..., global_secondary_index_updates: Optional[Any] = ...): ...
    def create_table(self, attribute_definitions: Optional[Any] = ..., key_schema: Optional[Any] = ..., read_capacity_units: Optional[Any] = ..., write_capacity_units: Optional[Any] = ..., global_secondary_indexes: Optional[Any] = ..., local_secondary_indexes: Optional[Any] = ..., stream_specification: Optional[Any] = ...): ...

