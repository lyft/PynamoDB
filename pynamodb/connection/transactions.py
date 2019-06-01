from pynamodb.exceptions import GetError, DoesNotExist

from pynamodb.connection.base import Connection
from pynamodb.constants import (
    TABLE_NAME, PROJECTION_EXPRESSION, UPDATE, GET, PUT, DELETE, TRANSACT_ITEMS, CLIENT_REQUEST_TOKEN, CONDITION_CHECK,
    CONDITION_EXPRESSION, EXPRESSION_ATTRIBUTE_NAMES, EXPRESSION_ATTRIBUTE_VALUES, UPDATE_EXPRESSION,
    RETURN_VALUES_ON_CONDITION_FAILURE, ITEM, KEY, RETURN_VALUES, RESPONSES
)

PUT = PUT.lower().capitalize()
DELETE = DELETE.lower().capitalize()

# each transaction can only support 10 actions at a time
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html#limits-dynamodb-transactions
TRANSACT_ITEM_LIMIT = 10

CONDITION_CHECK_REQUEST_PARAMETERS = {
    CONDITION_EXPRESSION,
    EXPRESSION_ATTRIBUTE_NAMES,
    EXPRESSION_ATTRIBUTE_VALUES,
    KEY,
    RETURN_VALUES_ON_CONDITION_FAILURE,
    TABLE_NAME,
}

DELETE_REQUEST_PARAMETERS = {
    CONDITION_EXPRESSION,
    EXPRESSION_ATTRIBUTE_NAMES,
    EXPRESSION_ATTRIBUTE_VALUES,
    KEY,
    RETURN_VALUES_ON_CONDITION_FAILURE,
    TABLE_NAME,
}

GET_REQUEST_PARAMETERS = {
    KEY,
    TABLE_NAME,
    EXPRESSION_ATTRIBUTE_NAMES,
    EXPRESSION_ATTRIBUTE_VALUES,
    PROJECTION_EXPRESSION,
}

PUT_REQUEST_PARAMETERS = {
    CONDITION_EXPRESSION,
    EXPRESSION_ATTRIBUTE_NAMES,
    EXPRESSION_ATTRIBUTE_VALUES,
    ITEM,
    RETURN_VALUES_ON_CONDITION_FAILURE,
    TABLE_NAME,
}

UPDATE_REQUEST_PARAMETERS = {
    CONDITION_EXPRESSION,
    EXPRESSION_ATTRIBUTE_NAMES,
    EXPRESSION_ATTRIBUTE_VALUES,
    KEY,
    RETURN_VALUES_ON_CONDITION_FAILURE,
    TABLE_NAME,
    UPDATE_EXPRESSION,
}


class Transaction(object):

    _connection = None
    _hashed_models = None
    _item_limit = TRANSACT_ITEM_LIMIT
    _operation_kwargs = None
    _proxy_models = None
    _results = None

    def __init__(self, return_consumed_capacity=None, override_connection=False, **connection_kwargs):
        self._hashed_models = set()
        self._proxy_models = []
        self._operation_kwargs = {
            TRANSACT_ITEMS: [],
        }
        self._connection = _get_connection(override_connection=override_connection, **connection_kwargs)
        if return_consumed_capacity is not None:
            self._operation_kwargs.update(self._connection.get_consumed_capacity_map(return_consumed_capacity))

    def __len__(self):
        return len(self.transact_items)

    @staticmethod
    def _get_key(model_cls, hash_key, range_key=None):
        return "{0}({1},{2})".format(model_cls.__name__, hash_key, range_key)

    @property
    def transact_items(self):
        return self._operation_kwargs[TRANSACT_ITEMS]

    @staticmethod
    def format_item(method, valid_parameters, operation_kwargs):
        if RETURN_VALUES in operation_kwargs.keys():
            operation_kwargs[RETURN_VALUES_ON_CONDITION_FAILURE] = operation_kwargs.pop(RETURN_VALUES)
        request_params = {
            key: value for key, value in operation_kwargs.items() if key in valid_parameters
        }
        return {method: request_params}

    def add_item(self, item):
        if len(self) >= self._item_limit:
            raise ValueError("Transaction can't support more than {0} items".format(self._item_limit))
        self.transact_items.append(item)


class TransactGet(Transaction):

    def add_get_item(self, model_cls, hash_key, range_key, operation_kwargs):
        get_item = self.format_item(GET, GET_REQUEST_PARAMETERS, operation_kwargs)
        self.add_item(get_item)
        return self._add_item_class(model_cls, hash_key, range_key)

    def _add_item_class(self, model_cls, hash_key, range_key=None):
        key = self._get_key(model_cls, hash_key, range_key)
        if key in self._hashed_models:
            raise ValueError("Can't perform operation on the same entry multiple times in one transaction")
        proxy_kwargs = {'hash_key': hash_key}
        if range_key is not None:
            proxy_kwargs['range_key'] = range_key
        proxy_model = model_cls(**proxy_kwargs)
        self._hashed_models.add(key)
        self._proxy_models.append(proxy_model)
        return proxy_model

    def get_results_in_order(self):
        if self._results is None:
            raise GetError('Attempting to access item before committing the transaction')
        return self._proxy_models

    def _update_proxy_models(self):
        for model, data in zip(self._proxy_models, self._results):
            model.update_item_with_raw_data(data[ITEM])

    def commit(self):
        self._results = self._connection.transact_get_items(self._operation_kwargs)[RESPONSES]
        self._update_proxy_models()


class TransactWrite(Transaction):

    @staticmethod
    def _validate_client_request_token(token):
        if not isinstance(token, str):
            raise ValueError('Client request token must be a string')
        if len(token) > 36:
            raise ValueError('Client request token max length is 36 characters')

    def __init__(self, client_request_token=None, return_item_collection_metrics=None, **kwargs):
        super(TransactWrite, self).__init__(**kwargs)
        if client_request_token is not None:
            self._validate_client_request_token(client_request_token)
            self._operation_kwargs[CLIENT_REQUEST_TOKEN] = client_request_token
        if return_item_collection_metrics is not None:
            self._operation_kwargs.update(self._connection.get_item_collection_map(return_item_collection_metrics))

    def add_condition_check_item(self, operation_kwargs):
        condition_item = self.format_item(CONDITION_CHECK, CONDITION_CHECK_REQUEST_PARAMETERS, operation_kwargs)
        self.add_item(condition_item)

    def add_delete_item(self, operation_kwargs):
        delete_item = self.format_item(DELETE, DELETE_REQUEST_PARAMETERS, operation_kwargs)
        self.add_item(delete_item)

    def add_save_item(self, operation_kwargs):
        put_item = self.format_item(PUT, PUT_REQUEST_PARAMETERS, operation_kwargs)
        self.add_item(put_item)

    def add_update_item(self, operation_kwargs):
        update_item = self.format_item(UPDATE, UPDATE_REQUEST_PARAMETERS, operation_kwargs)
        self.add_item(update_item)

    def _update_proxy_models(self):
        for model in self._proxy_models:
            model.refresh()

    def commit(self):
        self._connection.transact_write_items(self._operation_kwargs)
        self._update_proxy_models()


_CONNECTION = None


def _get_connection(override_connection=False, **kwargs):
    global _CONNECTION
    if override_connection or _CONNECTION is None:
        _CONNECTION = Connection(**kwargs)
    return _CONNECTION
