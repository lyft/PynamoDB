from pynamodb.constants import (
    RETURN_VALUES_ON_CONDITION_FAILURE, ITEM, RETURN_VALUES, RESPONSES,
    TRANSACTION_CONDITION_CHECK_REQUEST_PARAMETERS, TRANSACTION_DELETE_REQUEST_PARAMETERS,
    TRANSACTION_GET_REQUEST_PARAMETERS, TRANSACTION_PUT_REQUEST_PARAMETERS, TRANSACTION_UPDATE_REQUEST_PARAMETERS
)
from pynamodb.models import _ModelFuture


class Transaction(object):

    """
    Base class for a type of transaction operation
    """

    _results = None

    def __init__(self, connection, return_consumed_capacity=None):
        self._connection = connection
        self._hashed_models = set()
        self._return_consumed_capacity = return_consumed_capacity

    def _commit(self):
        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._commit()

    def _hash_model(self, model_cls, hash_key, range_key=None):
        """
        creates a unique identifier for the model, and hashes it
        to ensure that we don't perform multiple operations on the same entry within the same transaction

        :param model_cls:
        :param hash_key:
        :param range_key:
        :return:
        """
        key = (model_cls, hash_key, range_key)
        if key in self._hashed_models:
            raise ValueError("Can't perform operation on the same entry multiple times in one transaction")
        self._hashed_models.add(key)

    @staticmethod
    def _format_request_parameters(valid_parameters, operation_kwargs):
        if RETURN_VALUES in operation_kwargs.keys():
            operation_kwargs[RETURN_VALUES_ON_CONDITION_FAILURE] = operation_kwargs.pop(RETURN_VALUES)
        return {
            key: value for key, value in operation_kwargs.items() if key in valid_parameters
        }


class TransactGet(Transaction):

    def __init__(self, *args, **kwargs):
        super(TransactGet, self).__init__(*args, **kwargs)
        self._get_items = []
        self._futures = []

    def get(self, model_cls, hash_key, range_key=None):
        """
        Adds the operation arguments for an item to list of models to get
        returns a _ModelFuture object as a placeholder

        :param model_cls:
        :param hash_key:
        :param range_key:
        :return:
        """
        self._hash_model(model_cls, hash_key, range_key)
        operation_kwargs = model_cls.get_operation_kwargs_for_get_item(hash_key, range_key=range_key)
        get_item = self._format_request_parameters(TRANSACTION_GET_REQUEST_PARAMETERS, operation_kwargs)
        model_future = _ModelFuture(model_cls)
        self._futures.append(model_future)
        self._get_items.append(get_item)
        return model_future

    def _update_futures(self):
        for model, data in zip(self._futures, self._results):
            model.update_with_raw_data(data[ITEM])

    def _commit(self):
        response = self._connection.transact_get_items(
            get_items=self._get_items,
            return_consumed_capacity=self._return_consumed_capacity
        )
        self._results = response[RESPONSES]
        self._update_futures()


class TransactWrite(Transaction):

    def __init__(self, client_request_token=None, return_item_collection_metrics=None, **kwargs):
        super(TransactWrite, self).__init__(**kwargs)
        self._client_request_token = client_request_token
        self._return_item_collection_metrics = return_item_collection_metrics
        self._condition_check_items = []
        self._delete_items = []
        self._put_items = []
        self._update_items = []

    def add_condition_check_item(self, model_cls, hash_key, range_key, operation_kwargs):
        condition_item = self._format_request_parameters(TRANSACTION_CONDITION_CHECK_REQUEST_PARAMETERS, operation_kwargs)
        self._hash_model(model_cls, hash_key, range_key)
        self._condition_check_items.append(condition_item)

    def add_delete_item(self, model, operation_kwargs):
        delete_item = self._format_request_parameters(TRANSACTION_DELETE_REQUEST_PARAMETERS, operation_kwargs)
        self._hash_model(model.__class__, model.get_hash_key(), model.get_range_key())
        self._delete_items.append(delete_item)

    def add_save_item(self, model, operation_kwargs):
        put_item = self._format_request_parameters(TRANSACTION_PUT_REQUEST_PARAMETERS, operation_kwargs)
        self._hash_model(model.__class__, model.get_hash_key(), model.get_range_key())
        self._put_items.append(put_item)

    def add_update_item(self, model, operation_kwargs):
        update_item = self._format_request_parameters(TRANSACTION_UPDATE_REQUEST_PARAMETERS, operation_kwargs)
        self._hash_model(model.__class__, model.get_hash_key(), model.get_range_key())
        self._update_items.append(update_item)

    def _commit(self):
        self._connection.transact_write_items(
            condition_check_items=self._condition_check_items,
            delete_items=self._delete_items,
            put_items=self._put_items,
            update_items=self._update_items,
            client_request_token=self._client_request_token,
            return_consumed_capacity=self._return_consumed_capacity,
            return_item_collection_metrics=self._return_item_collection_metrics,
        )
