from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from freezegun import freeze_time
import pytest
from src.server.lib.models import Credentials
from src.server.lib.utils import utcnow
from src.server.lib.constants import PREDEFINED_SUB_INFOS
from src.server.db import (
    create_account,
    check_sub_expired,
    create_checkout_session,
    create_sub,
    cancel_sub,
    get_invoice,
    change_sub,
    _get_active_sub,
    _validate_sub_info,
    _check_schedule_requests,
    _increment_schedule_requests,
    _check_account_limits
)
from tests.utils import ctxtest

# Init
class FakeStripeCheckoutSession:
    def __init__(self):
        self.id = 'cs_test_123'
        self.url = 'https://checkout.stripe.com/pay/cs_test_123'
        self.mode = 'subscription'
        self.customer = 'cus_test_abc'
        self.subscription = 'sub_test_abc'


class FakeStripeSubscription:
    def __init__(self, status='active', unit_amount=4900, lookup_key='standard', period_end=None):
        self.items = {
            'data': [{'price': {'unit_amount': unit_amount, 'lookup_key': lookup_key}}]
        }
        self.current_period_end = int(
            (period_end or datetime(2025, 12, 1, tzinfo=timezone.utc)).timestamp()
        )
        self.status = status
    
    def __getitem__(self, key):
        return getattr(self, key)


@ctxtest()
def setup_and_teardown():
    account = create_account(Credentials(email='user@test.com', password='00123400'))[0]
    yield account.account_id


# Tests
@patch('src.server.db.stripe.checkout.Session.create')
def test_create_checkout_session(mock_stripe_create, setup_and_teardown):
    account_id = setup_and_teardown
    mock_stripe_create.return_value = MagicMock(url='https://checkout.stripe.com/pay/cs_test_123')
    url = create_checkout_session(account_id, plan_name='standard')
    assert url.startswith('https://checkout.stripe.com')
    mock_stripe_create.assert_called_once()


@patch('src.server.db.stripe.Subscription.retrieve')
@patch('src.server.db.stripe.checkout.Session.retrieve')
def test_create_subsets_expired_false(mock_session_retrieve, mock_subscription_retrieve, setup_and_teardown):
    account_id = setup_and_teardown

    mock_session_retrieve.return_value = FakeStripeCheckoutSession()
    mock_subscription_retrieve.return_value = FakeStripeSubscription()

    # Before creating sub, user has no expired subs
    assert check_sub_expired(account_id) is False

    account, sub = create_sub(account_id, stripe_session_id='cs_test_123')

    assert sub.plan.value == 'standard'
    assert sub.price == 0.0
    assert (sub.expires_at - sub.created_at).days == 7
    assert account.stripe_customer_id == 'cus_test_abc'

    # After creating sub, still not expired
    assert check_sub_expired(account_id) is False


@patch('src.server.db.stripe.Subscription.retrieve')
@patch('src.server.db.stripe.checkout.Session.retrieve')
def test_check_sub_expired_true_after_time_passed(mock_session_retrieve, mock_subscription_retrieve, setup_and_teardown):
    account_id = setup_and_teardown
    mock_session_retrieve.return_value = FakeStripeCheckoutSession()
    mock_subscription_retrieve.return_value = FakeStripeSubscription('canceled')

    _, sub = create_sub(account_id, stripe_session_id='cs_test_123')

    # Travel 8 days ahead (past expiration)
    with freeze_time(sub.expires_at + timedelta(days=1)):
        assert check_sub_expired(account_id) is True


@patch('src.server.db.functions.stripe.Invoice.list')
@patch('src.server.db.functions._get_active_sub')
@patch('src.server.db.functions._check_account')
def test_get_invoice_success(mock_check_account, mock_get_active_sub, mock_invoice_list):
    # Mock account with stripe customer ID
    mock_check_account.return_value = MagicMock(stripe_customer_id='cus_test_123')
    mock_get_active_sub.return_value = MagicMock(stripe_subscription_id='sub_test_123')

    fake_invoice = MagicMock(
        id='in_test_123',
        amount_due=4900,
        amount_paid=4900,
        currency='usd',
        status='paid',
        invoice_pdf='https://stripe.com/invoice.pdf',
        hosted_invoice_url='https://stripe.com/invoice',
        created=int(datetime(2025, 3, 24, 12, 0, tzinfo=timezone.utc).timestamp()),
        due_date=int(datetime(2025, 3, 31, 12, 0, tzinfo=timezone.utc).timestamp()),
        description='March invoice',
        subscription='sub_test_123',
    )
    mock_invoice_list.return_value = MagicMock(data=[fake_invoice])

    invoice = get_invoice(1)
    assert invoice['invoice_id'] == 'in_test_123'
    assert invoice['amount_due'] == 49.0
    assert invoice['status'] == 'paid'
    assert invoice['currency'] == 'USD'
    assert invoice['subscription_id'] == 'sub_test_123'


@patch('src.server.db.functions.stripe.Subscription.delete')
@patch('src.server.db.functions.stripe.Customer.delete')
@patch('src.server.db.functions._get_active_sub')
@patch('src.server.db.functions._check_account')
def test_cancel_sub_success(mock_check_account, mock_get_active_sub, mock_customer_delete, mock_sub_delete):
    account = MagicMock(stripe_customer_id='cus_test_abc')
    subscription = MagicMock(stripe_subscription_id='sub_test_abc')
    mock_check_account.return_value = account
    mock_get_active_sub.return_value = subscription

    cancel_sub(1)

    mock_sub_delete.assert_called_once_with('sub_test_abc', prorate=True)
    mock_customer_delete.assert_called_once_with('cus_test_abc')
    assert account.stripe_customer_id is None
    assert subscription.canceled_at is not None


@patch('src.server.db.functions.stripe.Subscription.retrieve')
@patch('src.server.db.functions.stripe.Invoice.pay')
@patch('src.server.db.functions.stripe.Invoice.finalize_invoice')
@patch('src.server.db.functions.stripe.Invoice.create')
@patch('src.server.db.functions.stripe.Subscription.modify')
@patch('src.server.db.functions._get_active_sub')
@patch('src.server.db.functions._check_account')
def test_change_sub_success(mock_check_account, mock_get_active_sub, mock_modify, mock_create_invoice, mock_finalize, mock_pay, mock_retrieve):
    account = MagicMock(stripe_customer_id='cus_abc')
    subscription = MagicMock(
        stripe_subscription_id='sub_abc',
        plan='basic',
        price=49.0,
        canceled_at=None
    )
    mock_check_account.return_value = account
    mock_get_active_sub.return_value = subscription
    mock_retrieve.return_value = {
        'items': {'data': [{'id': 'item_123'}]},
        'current_period_end': int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())
    }
    mock_create_invoice.return_value = MagicMock(id='inv_123')

    sub = change_sub(1, new_plan='standard')
    assert sub.plan == 'standard'
    assert sub.price == PREDEFINED_SUB_INFOS['standard'].price
    assert sub.plan_details == PREDEFINED_SUB_INFOS['standard'].plan_details.model_dump()


@patch('src.server.db.utils.stripe.Subscription.retrieve')
def test_get_active_sub_with_expired_but_active_in_stripe(mock_stripe_retrieve):
    session = MagicMock()
    subscription = MagicMock()
    subscription.account_id = 1
    subscription.expires_at = utcnow() - timedelta(days=1)  # expired locally
    subscription.canceled_at = None
    subscription.stripe_subscription_id = 'sub_mock_123'

    # Properly chain .first()
    session.query.return_value.filter.return_value.order_by.return_value.first.return_value = subscription

    # Stripe says it's still active and extended
    new_expiry = utcnow() + timedelta(days=30)

    class FakeStripeSub:
        status = 'active'
        current_period_end = int(new_expiry.timestamp())

    mock_stripe_retrieve.return_value = FakeStripeSub()

    result = _get_active_sub(1, session=session)
    assert result is subscription
    assert subscription.expires_at.replace(microsecond=0) == new_expiry.replace(microsecond=0)
    session.commit.assert_called_once()


@patch('src.server.db.stripe.Subscription.retrieve')
def test_get_active_sub_fully_expired(mock_stripe_retrieve):
    session = MagicMock()
    subscription = MagicMock()
    subscription.account_id = 1
    subscription.expires_at = utcnow() - timedelta(days=2)
    subscription.canceled_at = None
    subscription.stripe_subscription_id = 'sub_expired'
    session.query().filter().order_by().first.return_value = subscription

    # Stripe says sub is canceled
    mock_stripe_retrieve.return_value = MagicMock(
        status='canceled',
        current_period_end=int((utcnow() - timedelta(days=1)).timestamp())
    )

    result = _get_active_sub(1, session=session)
    assert result is None
    session.commit.assert_not_called()


@patch('src.server.db.functions.stripe.Subscription.retrieve')
def test_get_active_sub_up_to_date(mock_stripe_retrieve):
    session = MagicMock()
    subscription = MagicMock()
    subscription.account_id = 1
    subscription.expires_at = utcnow() + timedelta(days=5)
    subscription.canceled_at = None
    session.query().filter().order_by().first.return_value = subscription

    result = _get_active_sub(1, session=session)
    assert result is subscription
    mock_stripe_retrieve.assert_not_called()


def test_validate_sub_info_premium_trial():
    # Setup mock session and account
    session = MagicMock()
    account = MagicMock()
    account.has_used_trial = False
    session.query().filter_by().first.return_value = None  # No existing stripe_session_id
    session.query().filter().exists().where().scalar.return_value = False  # No custom plan exists
    session.query.return_value.scalar.return_value = False
    session.query.return_value.filter_by.return_value.first.return_value = None

    session.query.return_value.filter.return_value.exists.return_value = False

    with patch('src.server.db.utils._check_account', return_value=account):
        stripe_session_id = 'cs_test_123'
        stripe_subscription_id = 'sub_test_456'

        result = _validate_sub_info(
            1,
            sub_info=PREDEFINED_SUB_INFOS['premium'],
            stripe_session_id=stripe_session_id,
            stripe_subscription_id=stripe_subscription_id,
            session=session
        )

    assert result['price'] == 0.0
    assert result['plan'] == 'premium'
    assert result['account_id'] == 1
    assert result['stripe_session_id'] == stripe_session_id
    assert result['stripe_subscription_id'] == stripe_subscription_id
    assert result['expires_at'] <= utcnow() + timedelta(days=7)
    assert isinstance(result['expires_at'], datetime)
    assert result['plan_details']['max_num_pediatricians'] == 999
    assert result['plan_details']['max_num_shifts_per_day'] == 999
    assert result['plan_details']['max_num_schedule_requests'] == 999
    assert account.has_used_trial is True


def test_validate_sub_info_used_trial():
    # Setup mock session and account
    session = MagicMock()
    account = MagicMock()
    account.has_used_trial = True
    session.query().filter_by().first.return_value = None  # No existing stripe_session_id

    with patch('src.server.db.utils._check_account', return_value=account):
        stripe_session_id = 'cs_test_999'
        stripe_subscription_id = 'sub_test_999'

        result = _validate_sub_info(
            1,
            sub_info=PREDEFINED_SUB_INFOS['standard'],
            stripe_session_id=stripe_session_id,
            stripe_subscription_id=stripe_subscription_id,
            session=session
        )

    assert result['price'] == PREDEFINED_SUB_INFOS['standard'].price
    assert result['plan'] == 'standard'
    assert result['account_id'] == 1
    assert result['stripe_session_id'] == stripe_session_id
    assert result['stripe_subscription_id'] == stripe_subscription_id
    assert isinstance(result['expires_at'], datetime)
    assert result['expires_at'] <= utcnow() + timedelta(days=30)
    assert result['plan_details'] == PREDEFINED_SUB_INFOS['standard'].plan_details.model_dump()
    assert account.has_used_trial is True


def test_check_account_limits_within_limits():
    # Mock subscription with limits
    session = MagicMock()
    subscription = MagicMock()
    subscription.plan_details = {'max_num_pediatricians': 5, 'max_num_shifts_per_day': 3}

    with patch('src.server.db.utils._get_active_sub', return_value=subscription), \
         patch('src.server.db.utils._check_schedule_requests') as mock_check_sched:
        session.query.return_value.filter.return_value.count.side_effect = [3, 2]  # employees, shifts

        # Should NOT raise an exception
        _check_account_limits(1, session=session)

        mock_check_sched.assert_called_once_with(1, session=session)


def test_check_account_limits_exceeds_employees():
    session = MagicMock()
    subscription = MagicMock()
    subscription.plan_details = {'max_num_pediatricians': 5, 'max_num_shifts_per_day': 3}

    with patch('src.server.db.utils._get_active_sub', return_value=subscription), \
         patch('src.server.db.utils._check_schedule_requests'):

        session.query.return_value.filter.return_value.count.side_effect = [6, 2]  # Exceeds pediatricians

        with pytest.raises(ValueError, match='maximum number of pediatricians'):
            _check_account_limits(1, session=session)


def test_check_account_limits_exceeds_shifts():
    session = MagicMock()
    subscription = MagicMock()
    subscription.plan_details = {'max_num_pediatricians': 5, 'max_num_shifts_per_day': 3}

    with patch('src.server.db.utils._get_active_sub', return_value=subscription), \
         patch('src.server.db.utils._check_schedule_requests'):

        session.query.return_value.filter.return_value.count.side_effect = [3, 5]  # Exceeds shifts

        with pytest.raises(ValueError, match='maximum number of shift types'):
            _check_account_limits(1, session=session)


def test_check_schedule_requests_with_active_sub_allows_request():
    # Create a fake subscription with high request limit
    session = MagicMock()
    sub = MagicMock()
    sub.plan_details = {'max_num_schedule_requests': 10}

    # Patch _get_active_sub to return the subscription
    with patch('src.server.db.utils._get_active_sub', return_value=sub):
        schedule_requests = MagicMock()
        schedule_requests.month = utcnow().month
        schedule_requests.num_requests = 5
        session.get.return_value = schedule_requests

        _check_schedule_requests(1, session=session)

        # Should not raise
        session.commit.assert_not_called()  # No need to update month


def test_check_schedule_requests_with_active_sub_reaches_limit():
    session = MagicMock()
    sub = MagicMock()
    sub.plan_details = {'max_num_schedule_requests': 5}

    with patch('src.server.db.utils._get_active_sub', return_value=sub):
        schedule_requests = MagicMock()
        schedule_requests.month = utcnow().month
        schedule_requests.num_requests = 5
        session.get.return_value = schedule_requests

        with pytest.raises(ValueError, match="Max number of schedule requests"):
            _check_schedule_requests(1, session=session)


def test_schedule_request_increment_until_limit():
    session = MagicMock()
    sub = MagicMock()
    sub.plan_details = {'max_num_schedule_requests': 3}

    # Patch _get_active_sub to return the subscription
    with patch('src.server.db.utils._get_active_sub', return_value=sub):
        # Setup schedule_requests and assign to session.get
        schedule_requests = MagicMock()
        schedule_requests.month = utcnow().month
        schedule_requests.num_requests = 0
        session.get.return_value = schedule_requests

        # Increment until just below the limit
        for _ in range(3):
            _check_schedule_requests(1, session=session)  # Should not raise
            _increment_schedule_requests(1, session=session)

        # Now it should raise
        with pytest.raises(ValueError, match="Max number of schedule requests"):
            _check_schedule_requests(1, session=session)

        assert schedule_requests.num_requests == 3
        assert session.commit.call_count == 3  # once per increment