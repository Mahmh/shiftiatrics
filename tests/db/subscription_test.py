from datetime import timedelta
from unittest.mock import MagicMock, patch
from freezegun import freeze_time
from src.server.lib.models import Credentials
from src.server.lib.utils import utcnow
from src.server.db import create_account, check_sub_expired, create_sub, _get_active_sub
from tests.utils import ctxtest, FakeStripeCheckoutSession, FakeStripeSubscription

# Init
@ctxtest()
def setup_and_teardown():
    account = create_account(Credentials(email='user@test.com', password='00123400'))[0]
    yield account.account_id


# Tests
@patch('src.server.db.stripe.Subscription.retrieve')
@patch('src.server.db.stripe.checkout.Session.retrieve')
def test_create_sub_expired_false(mock_session_retrieve, mock_subscription_retrieve, setup_and_teardown):
    account_id = setup_and_teardown
    mock_session_retrieve.return_value = FakeStripeCheckoutSession()
    mock_subscription_retrieve.return_value = FakeStripeSubscription(period_end=utcnow() + timedelta(days=7))

    # Before creating sub, user has no expired subs
    assert check_sub_expired(account_id) is False

    account, sub = create_sub(
        account_id,
        plan='starter',
        expires_at=utcnow() + timedelta(days=7),
        stripe_subscription_id='subid',
        stripe_customer_id='cus_test_abc'
    )

    assert sub.plan.value == 'starter'
    assert (sub.expires_at - sub.created_at).days + 1 == 7
    assert account.stripe_customer_id == 'cus_test_abc'

    # After creating sub, still not expired
    assert check_sub_expired(account_id) is False


@patch('src.server.db.stripe.Subscription.retrieve')
@patch('src.server.db.stripe.checkout.Session.retrieve')
def test_check_sub_expired_true_after_time_passed(mock_session_retrieve, mock_subscription_retrieve, setup_and_teardown):
    account_id = setup_and_teardown
    mock_session_retrieve.return_value = FakeStripeCheckoutSession()
    mock_subscription_retrieve.return_value = FakeStripeSubscription(status='canceled')

    _, sub = create_sub(
        account_id,
        plan='growth',
        expires_at=utcnow() + timedelta(days=7),
        stripe_subscription_id='subid',
        stripe_customer_id='cus_test_abc'
    )

    # Travel 8 days ahead (past expiration)
    with freeze_time(sub.expires_at + timedelta(days=1)):
        assert check_sub_expired(account_id) is True


@patch('src.server.db.utils.stripe.Subscription.retrieve')
def test_get_active_sub_with_expired_but_active_in_stripe(mock_stripe_retrieve):
    session = MagicMock()
    sub = MagicMock()
    sub.account_id = 1
    sub.expires_at = utcnow() - timedelta(days=1)  # expired locally
    sub.stripe_subscription_id = 'sub_mock_123'

    # Properly chain .first()
    session.query.return_value.filter.return_value.order_by.return_value.first.return_value = sub

    # Stripe says it's still active and extended
    new_expiry = utcnow() + timedelta(days=30)

    class FakeStripeSub:
        status = 'active'
        current_period_end = int(new_expiry.timestamp())

    mock_stripe_retrieve.return_value = FakeStripeSub()

    result = _get_active_sub(1, session=session)
    assert result is sub
    assert sub.expires_at.replace(microsecond=0) == new_expiry.replace(microsecond=0)
    session.commit.assert_called_once()


@patch('src.server.db.stripe.Subscription.retrieve')
def test_get_active_sub_fully_expired(mock_stripe_retrieve):
    session = MagicMock()
    sub = MagicMock()
    sub.account_id = 1
    sub.expires_at = utcnow() - timedelta(days=2)
    sub.stripe_subscription_id = 'sub_expired'
    session.query().filter().order_by().first.return_value = sub

    # Stripe says sub is canceled
    mock_stripe_retrieve.return_value = MagicMock(
        status='canceled',
        current_period_end=int((utcnow() - timedelta(days=1)).timestamp())
    )

    result = _get_active_sub(1, session=session)
    assert result is None
    session.commit.assert_not_called()


@patch('src.server.db.utils.stripe.Subscription.retrieve')
def test_get_active_sub_up_to_date(mock_stripe_retrieve):
    session = MagicMock()
    sub = MagicMock()
    sub.account_id = 1
    sub.expires_at = utcnow() + timedelta(days=5)
    session.query().filter().order_by().first.return_value = sub

    result = _get_active_sub(1, session=session)
    assert result is sub
    mock_stripe_retrieve.assert_not_called()