from decimal import Decimal
from datetime import date
from django.db import transaction

from accounting.models import Installment, ReceiptVoucher, Safe

def pay_installment(
    installment: Installment,
    amount: Decimal,
    safe: Safe,
    payment_date: date,
    description: str = None
) -> ReceiptVoucher:
    """
    Handles the logic of paying an installment.
    - Creates a ReceiptVoucher.
    - Updates the installment's paid_amount.
    - Updates the installment's status.
    This all happens within a transaction.
    """

    with transaction.atomic():
        # 1. Create the receipt voucher
        if description is None:
            description = f"سداد القسط رقم {installment.seq_no} للعقد {installment.contract.code}"

        receipt = ReceiptVoucher.objects.create(
            date=payment_date,
            amount=amount,
            safe=safe,
            description=description,
            customer=installment.contract.customer,
            contract=installment.contract,
            installment=installment
        )

        # 2. Update the installment's paid amount
        installment.paid_amount += amount

        # 3. Update the installment's status and save
        installment.update_status() # This method also saves the installment

    return receipt
