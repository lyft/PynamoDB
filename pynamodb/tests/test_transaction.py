import pytest
import six

from pynamodb.connection import Connection
from pynamodb.connection.transactions import Transaction, TransactGet, TransactWrite
from pynamodb.exceptions import GetError

if six.PY3:
    from unittest.mock import MagicMock
else:
    from mock import MagicMock


class TestTransaction:

    def test_initialize(self, mocker):
        mock_connection = mocker.MagicMock(spec=Connection)
        mock_connection.get_consumed_capacity_map.return_value = {
            'ReturnConsumedCapacity': 'TOTAL'
        }
        t = Transaction(connection=mock_connection)
        assert t._operation_kwargs == {'TransactItems': []}

        t = Transaction(connection=mock_connection, return_consumed_capacity='TOTAL')
        assert t._operation_kwargs == {'ReturnConsumedCapacity': 'TOTAL', 'TransactItems': []}

    def test_commit__not_implemented(self, mocker):
        t = Transaction(connection=mocker.MagicMock())
        with pytest.raises(NotImplementedError):
            t._commit()

    def test_format_item(self, mocker):
        transaction = Transaction(connection=mocker.MagicMock())
        method = 'Foo'
        valid_parameters = ['a', 'c', 'e', 'ReturnValuesOnConditionCheckFailure']
        operation_kwargs = {'ReturnValues': 'ALL_OLD'}

        item = transaction.format_item(method, valid_parameters, operation_kwargs)
        assert item == {'Foo': {'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'}}

        item = transaction.format_item(method, valid_parameters, {'a': 1, 'b': 2, 'c': 3})
        assert item == {'Foo': {'a': 1, 'c': 3}}

    def test_hash_model__duplicate(self, mocker):
        mock_model = mocker.MagicMock()
        mock_model.__class__.__name__ = 'Mock'
        t = Transaction(connection=mocker.MagicMock())
        t._hash_model(mock_model, 1, 2)
        with pytest.raises(ValueError):
            t._hash_model(mock_model, 1, 2)


class TestTransactGet:

    def setup(self):
        self.mock_model_cls = MagicMock(__name__='MockModel')

    def test_get_results_in_order__get_error(self, mocker):
        t = TransactGet(connection=mocker.MagicMock())
        with pytest.raises(GetError):
            t.get_results_in_order()

        t._results = []
        assert t.get_results_in_order() == []

    def test_commit(self, mocker):
        mock_connection = mocker.MagicMock(spec=Connection)
        mock_connection.transact_get_items.return_value = {
            'Responses': [{'Item': {}}]
        }

        with TransactGet(connection=mock_connection) as t:
            t.add_get_item(self.mock_model_cls, 1, 2, {})

        mock_connection.transact_get_items.assert_called_once_with({'TransactItems': [{'Get': {}}]})


class TestTransactWrite:

    def test_initialize(self, mocker):
        mock_connection = mocker.MagicMock(spec=Connection)
        mock_connection.get_item_collection_map.return_value = {
            'ReturnItemCollectionMetrics': 'NONE'
        }
        t = TransactWrite(
            connection=mock_connection,
            client_request_token='foo',
            return_item_collection_metrics='NONE'
        )
        assert t._operation_kwargs == {
            'ClientRequestToken': 'foo',
            'ReturnItemCollectionMetrics': 'NONE',
            'TransactItems': [],
        }

    def test_validate_client_request_token(self, mocker):
        t = TransactWrite(connection=mocker.MagicMock())
        with pytest.raises(ValueError):
            t._validate_client_request_token(123)

        with pytest.raises(ValueError):
            too_long = 'i' * 40
            assert len(too_long) == 40
            t._validate_client_request_token(too_long)

    def test_update_proxy_models(self, mocker):
        t = TransactWrite(connection=mocker.MagicMock())
        mock_model = mocker.MagicMock()
        t._proxy_models = [mock_model for _ in range(5)]
        t._update_proxy_models()
        assert mock_model.refresh.call_count == 5

    def test_commit(self, mocker):
        mock_connection = mocker.MagicMock(spec=Connection)
        with TransactWrite(connection=mock_connection) as t:
            t.add_condition_check_item(mocker.MagicMock(), 1, 2, {})
            t.add_delete_item(mocker.MagicMock(), {})
            t.add_save_item(mocker.MagicMock(), {})
            t.add_update_item(mocker.MagicMock(), {})

        mock_connection.transact_write_items.assert_called_once_with({
            'TransactItems': [{'ConditionCheck': {}}, {'Delete': {}}, {'Put': {}}, {'Update': {}}]
        })
