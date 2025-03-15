from datetime import timedelta, timezone
from src.server.db import (
    Session,
    Account,
    Subscription,
    create_account,
    log_in_with_google,
    _generate_new_token,
    _validate_sub_info,
    _get_active_sub,
    _has_used_trial,
    _get_or_create_sub
)
from src.server.lib.models import Credentials, SubscriptionInfo, PlanDetails
from src.server.lib.constants import PREDEFINED_SUB_INFOS
from src.server.lib.utils import utcnow
from tests.utils import ctxtest, SUB_INFO

# Init
CRED = Credentials(email='testuser@gmail.com', password='testpass')

@ctxtest()
def setup_and_teardown():
    account, sub, _ = create_account(CRED, SUB_INFO)
    yield account.account_id, sub.subscription_id, Session()


def _create_random_account_without_sub(*, session) -> Account:
    account = Account(email='randomemail@gmail.com', email_verified=False)
    session.add(account)
    session.commit()
    return account


# Tests
def test_validate_sub_info_custom_plan(setup_and_teardown):
    '''Test that a custom plan validation works correctly.'''
    account_id, _, session = setup_and_teardown
    custom_plan_info = SubscriptionInfo(
        plan='custom',
        price=20.0,
        expires_at=utcnow() + timedelta(days=30),
        plan_details=PlanDetails(max_num_pediatricians=10, max_num_shifts_per_day=5)
    )

    result = _validate_sub_info(account_id, custom_plan_info, session=session)
    
    assert result['plan'] == custom_plan_info.plan
    assert result['price'] == custom_plan_info.price
    assert result['expires_at'] > utcnow()
    assert result['plan_details']['max_num_pediatricians'] == custom_plan_info.plan_details.max_num_pediatricians
    assert result['plan_details']['max_num_shifts_per_day'] == custom_plan_info.plan_details.max_num_shifts_per_day


def test_validate_sub_info_trial(setup_and_teardown):
    '''Test free trial logic where the user hasn't used a trial before.'''
    _, _, session = setup_and_teardown
    account_id = _create_random_account_without_sub(session=session).account_id

    trial_plan_info = PREDEFINED_SUB_INFOS['standard']
    result = _validate_sub_info(account_id, trial_plan_info, session=session)

    assert result['plan'] == trial_plan_info.plan
    assert result['price'] == 0.0  # First-time trial is free
    assert result['expires_at'] > utcnow()  # Should be 7-day trial


def test_get_active_sub(setup_and_teardown):
    '''Test retrieving an active subscription.'''
    account_id, _, session = setup_and_teardown

    sub_info = PREDEFINED_SUB_INFOS['premium'].model_dump()
    del sub_info['expires_at']

    sub = Subscription(
        account_id=account_id,
        expires_at=utcnow() + timedelta(days=5),
        **sub_info
    )
    session.add(sub)
    session.commit()

    active_sub = _get_active_sub(account_id, session=session)
    assert active_sub is not None
    assert active_sub.plan.value == 'basic'
    assert active_sub.expires_at.replace(tzinfo=timezone.utc) > utcnow()


def test_get_active_sub_no_active(setup_and_teardown):
    '''Test retrieving an active subscription when none exist.'''
    _, _, session = setup_and_teardown
    account_id = _create_random_account_without_sub(session=session).account_id
    active_sub = _get_active_sub(account_id, session=session)
    assert active_sub is None  # No active subscription should exist


def test_has_used_trial(setup_and_teardown):
    '''Test whether a user has used a free trial.'''
    account_id, _, session = setup_and_teardown
    free_trial = Subscription(
        account_id=account_id,
        plan='basic',
        price=0.0,  # Free trial
        expires_at=utcnow() - timedelta(days=1),  # Expired
        plan_details={}
    )
    session.add(free_trial)
    session.commit()
    assert _has_used_trial(account_id, session=session) is True


def test_has_used_trial_no_trial(setup_and_teardown):
    '''Test when a user has never used a free trial.'''
    _, _, session = setup_and_teardown
    account_id = _create_random_account_without_sub(session=session).account_id
    assert _has_used_trial(account_id, session=session) is False


def test_get_or_create_sub_new_trial(setup_and_teardown):
    '''Test creating a new subscription with a free trial when no prior trial exists.'''
    _, _, session = setup_and_teardown
    account_id = _create_random_account_without_sub(session=session).account_id
    sub = _get_or_create_sub(account_id, plan_name='basic', session=session)

    assert sub is not None
    assert sub.plan.value == 'basic'
    assert sub.price == 0.0  # Free trial


def test_get_or_create_sub_existing(setup_and_teardown):
    '''Test retrieving an existing active subscription instead of creating a new one.'''
    account_id, sub_id, session = setup_and_teardown
    sub = _get_or_create_sub(account_id, plan_name='basic', session=session)
    assert sub.subscription_id == sub_id  # Should return the same subscription
    assert sub.plan.value == SUB_INFO.plan
    assert sub.price == 0.0


def test_get_or_create_sub_upgrade(setup_and_teardown):
    '''Test upgrading a user's subscription to a different plan.'''
    account_id, _, session = setup_and_teardown
    new_sub = _get_or_create_sub(account_id, plan_name='premium', session=session)
    assert new_sub.plan.value == 'premium'
    assert new_sub.price > 0.0  # Not a free trial


def test_get_or_create_sub_oauth(setup_and_teardown):
    '''Test OAuth users cannot start a free trial on another plan after logging out'''
    _, _, session = setup_and_teardown

    account, sub, _ = log_in_with_google(
        email='oauthuser@gmail.com',
        access_token=_generate_new_token('auth')['token'],
        oauth_id='google-123456',
        plan_name='basic'
    )

    new_sub = _get_or_create_sub(account.account_id, plan_name='premium', session=session)
    assert new_sub.subscription_id == sub.subscription_id
    assert new_sub.plan.value == 'basic'
    assert new_sub.price == 0.0