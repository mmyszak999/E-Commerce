import pytest
from sqlalchemy.orm import Session

from src.apps.orders.schemas import CartItemOutputSchema, CartOutputSchema
from src.apps.payments.services import (
    get_all_payments,
    get_all_user_payments,
    get_single_payment
)
from src.apps.payments.schemas import PaymentOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import (
    ActiveCartException,
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
)
from src.core.factories import CartInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_orders.conftest import db_cart_items, db_carts
from tests.test_products.conftest import db_products
from tests.test_users.conftest import db_user
from tests.test_payments.conftest import db_payments, payment_intent, stripe_session


def test_raise_exception_when_getting_nonexistent_payment(
    sync_session: Session,
    db_payments: PagedResponseSchema[PaymentOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_payment(sync_session, generate_uuid())

def test_if_correct_schema_is_returnen_when_staff_retrieve_single_payment(
    sync_session: Session,
    db_payments: PagedResponseSchema[PaymentOutputSchema]
):
    payment = get_single_payment(sync_session, db_payments.results[0].id, as_staff=True)
    assert type(payment) == PaymentOutputSchema


def test_if_multiple_payments_are_returned(
    sync_session: Session,
    db_payments: PagedResponseSchema[PaymentOutputSchema]
):
    payments = get_all_payments(sync_session, PageParams())
    assert payments.total == db_payments.total
    
    
def test_if_returned_payments_belong_to_the_same_user(
    sync_session: Session, db_user: UserOutputSchema,
    db_payments: PagedResponseSchema[PaymentOutputSchema]
):
    get_all_user_payments(sync_session, db_user.id, PageParams())
    payments = get_all_user_payments(sync_session, db_user.id, PageParams())

    assert [user_id for user_id in {payment.user.id for payment in payments.results}][
        0
    ] == db_user.id

    