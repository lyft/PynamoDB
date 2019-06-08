import os
import uuid
from datetime import datetime

import pytest

from pynamodb.connection import Connection
from pynamodb.exceptions import PutError, DoesNotExist

from pynamodb.attributes import NumberAttribute, UnicodeAttribute, UTCDateTimeAttribute, BooleanAttribute
from pynamodb.connection.transactions import TransactGet, TransactWrite

from pynamodb.models import Model

IDEMPOTENT_PARAMETER_MISMATCH = 'IdempotentParameterMismatchException'
PROVISIONED_THROUGHPUT_EXCEEDED = 'ProvisionedThroughputExceededException'
RESOURCE_NOT_FOUND = 'ResourceNotFoundException'
TRANSACTION_CANCELLED = 'TransactionCanceledException'
TRANSACTION_IN_PROGRESS = 'TransactionInProgressException'


DDB_URL = os.getenv('PYNAMODB_INTEGRATION_TEST_DDB_URL', 'http://localhost:8000')


class User(Model):
    class Meta:
        host = DDB_URL
        region = 'us-east-1'
        table_name = 'user'

    user_id = NumberAttribute(hash_key=True)


class BankStatement(Model):

    class Meta:
        host = DDB_URL
        region = 'us-east-1'
        table_name = 'statement'

    user_id = NumberAttribute(hash_key=True)
    balance = NumberAttribute(default=0)
    active = BooleanAttribute(default=True)


class LineItem(Model):

    class Meta:
        host = DDB_URL
        region = 'us-east-1'
        table_name = 'line-item'

    user_id = NumberAttribute(hash_key=True)
    created_at = UTCDateTimeAttribute(range_key=True, default=datetime.now())
    amount = NumberAttribute()
    currency = UnicodeAttribute()


class DifferentRegion(Model):

    class Meta:
        host = DDB_URL
        region = 'us-east-2'
        table_name = 'different-region'

    entry_index = NumberAttribute(hash_key=True)


TEST_MODELS = [
    BankStatement,
    DifferentRegion,
    LineItem,
    User,
]


CONNECTION = Connection(host=DDB_URL)


class TestTransactionIntegration:

    @classmethod
    def setup_class(cls):
        for m in TEST_MODELS:
            if not m.exists():
                m.create_table(
                    read_capacity_units=10,
                    write_capacity_units=10,
                    wait=True
                )

    @classmethod
    def teardown_class(cls):
        for m in TEST_MODELS:
            if m.exists():
                m.delete_table()

    @staticmethod
    def get_error_code(error):
        return error.cause.response['Error'].get('Code')

    @pytest.mark.ddblocal
    def test_transact_write__error__idempotent_parameter_mismatch(self):
        client_token = str(uuid.uuid4())

        with TransactWrite(connection=CONNECTION, client_request_token=client_token) as transaction:
            User(1).save(in_transaction=transaction)
            User(2).save(in_transaction=transaction)

        try:
            # committing the first time, then adding more info and committing again
            with TransactWrite(connection=CONNECTION, client_request_token=client_token) as transaction:
                User(3).save(in_transaction=transaction)
            assert False, 'Failed to raise error'
        except PutError as e:
            assert self.get_error_code(e) == IDEMPOTENT_PARAMETER_MISMATCH

        # ensure that the first request succeeded in creating new users
        assert User.get(1)
        assert User.get(2)

        with pytest.raises(DoesNotExist):
            # ensure it did not create the user from second request
            User.get(3)

    @pytest.mark.ddblocal
    def test_transact_write__error__different_regions(self):
        try:
            with TransactWrite(connection=CONNECTION) as transact_write:
                # creating a model in a table outside the region everyone else operates in
                DifferentRegion(entry_index=0).save(in_transaction=transact_write)
                BankStatement(1).save(in_transaction=transact_write)
                User(1).save(in_transaction=transact_write)
        except PutError as e:
            assert self.get_error_code(e) == RESOURCE_NOT_FOUND

    @pytest.mark.ddblocal
    def test_transact_write__error__transaction_cancelled(self):
        # create a users and a bank statements for them
        User(1).save()
        BankStatement(1).save()

        # attempt to do this as a transaction with the condition that they don't already exist
        try:
            with TransactWrite(connection=CONNECTION) as transaction:
                User(1).save(condition=(User.user_id.does_not_exist()), in_transaction=transaction)
                BankStatement(1).save(condition=(BankStatement.user_id.does_not_exist()), in_transaction=transaction)
            assert False, 'Failed to raise error'
        except PutError as e:
            assert self.get_error_code(e) == TRANSACTION_CANCELLED

    @pytest.mark.ddblocal
    def test_transact_get(self):
        # making sure these entries exist, and with the expected info
        User(1).save()
        BankStatement(1).save()
        User(2).save()
        BankStatement(2, balance=100).save()

        # get users and statements we just created and assign them to variables
        with TransactGet(connection=CONNECTION) as transaction:
            _user1_promise = User.get(1, in_transaction=transaction)
            _statement1_promise = BankStatement.get(1, in_transaction=transaction)
            _user2_promise = User.get(2, in_transaction=transaction)
            _statement2_promise = BankStatement.get(2, in_transaction=transaction)

        user1 = _user1_promise.resolve()
        statement1 = _statement1_promise.resolve()
        user2 = _user2_promise.resolve()
        statement2 = _statement2_promise.resolve()

        assert user1.user_id == statement1.user_id == 1
        assert statement1.balance == 0
        assert user2.user_id == statement2.user_id == 2
        assert statement2.balance == 100

    @pytest.mark.ddblocal
    def test_transact_write(self):
        # making sure these entries exist, and with the expected info
        BankStatement(1, balance=0).save()
        BankStatement(2, balance=100).save()

        # assert values are what we think they should be
        statement1 = BankStatement.get(1)
        statement2 = BankStatement.get(2)
        assert statement1.balance == 0
        assert statement2.balance == 100

        with TransactWrite(connection=CONNECTION) as transaction:
            # let the users send money to one another
            created_at = datetime.now()
            # create a credit line item to user 1's account
            LineItem(user_id=1, amount=50, currency='USD').save(
                condition=(LineItem.user_id.does_not_exist()),
                in_transaction=transaction
            )
            # create a debit to user 2's account
            LineItem(user_id=2, amount=-50, currency='USD').save(
                condition=(LineItem.user_id.does_not_exist()),
                in_transaction=transaction
            )

            # add credit to user 1's account
            statement1.balance += 50
            statement1.save(in_transaction=transaction)
            # debit from user 2's account if they have enough in the bank
            statement2.balance -= 50
            statement2.save(condition=(BankStatement.balance >= 50), in_transaction=transaction)

        assert statement1.balance == statement2.balance == 50

    @pytest.mark.ddblocal
    def test_transact_write__one_of_each(self):
        with TransactWrite(connection=CONNECTION) as transaction:
            User.condition_check(1, in_transaction=transaction, condition=(User.user_id.exists()))
            User(2).delete(in_transaction=transaction)
            LineItem(4, amount=100, currency='USD').save(condition=(LineItem.user_id.does_not_exist()))

        # confirming transaction correct and successful
        assert User.get(1)
        try:
            User.get(2)
            assert False, 'Failed to delete model'
        except DoesNotExist:
            assert True

        new_line_item = next(LineItem.query(4, scan_index_forward=False, limit=1), None)
        assert new_line_item
        assert new_line_item.amount == 100
        assert new_line_item.currency == 'USD'
