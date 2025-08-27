from decimal import Decimal, ROUND_DOWN
from dateutil.relativedelta import relativedelta
from django.db import transaction

from accounting.models import Contract, Installment

def generate_installments_for_contract(contract: Contract):
    """
    توليد جدول الأقساط الكامل لعقد معين.
    يتم تنفيذ هذه العملية داخل transaction لضمان السلامة.
    تقوم بحذف أي أقساط قديمة أولاً ثم إنشاء الجدول الجديد.
    """

    # المبلغ المتبقي بعد الدفعة المقدمة
    total_amount_to_schedule = contract.remaining_amount
    installments_count = contract.installments_count

    if installments_count <= 0:
        return # لا تقم بأي شيء إذا لم يكن هناك أقساط

    # حساب قيمة القسط الأساسية وتقريبها لأقرب قرشين
    base_installment_amount = (total_amount_to_schedule / Decimal(installments_count)).quantize(
        Decimal('0.01'), rounding=ROUND_DOWN
    )

    # حساب الفرق الناتج عن التقريب
    total_base_amount = base_installment_amount * installments_count
    remainder = total_amount_to_schedule - total_base_amount

    installments_to_create = []
    current_due_date = contract.start_date

    # تحديد فترة الزيادة بناءً على نوع الجدولة
    if contract.schedule_type == Contract.ScheduleType.MONTHLY:
        delta = relativedelta(months=1)
    elif contract.schedule_type == Contract.ScheduleType.QUARTERLY:
        delta = relativedelta(months=3)
    elif contract.schedule_type == Contract.ScheduleType.YEARLY:
        delta = relativedelta(years=1)
    else:
        # Should not happen with current model choices
        raise ValueError(f"نوع جدولة غير معروف: {contract.schedule_type}")

    for i in range(1, installments_count + 1):
        amount = base_installment_amount
        # إضافة الفرق المتبقي إلى القسط الأخير لضمان تطابق المجموع
        if i == installments_count:
            amount += remainder

        installments_to_create.append(
            Installment(
                contract=contract,
                seq_no=i,
                due_date=current_due_date,
                amount=amount,
                status=Installment.InstallmentStatus.PENDING,
            )
        )

        # حساب تاريخ الاستحقاق التالي
        current_due_date += delta

    # استخدام transaction لضمان أن العملية تتم بالكامل أو لا تتم على الإطلاق
    with transaction.atomic():
        # حذف الأقساط القديمة إذا كانت موجودة
        contract.installments.all().delete()
        # إنشاء الأقساط الجديدة دفعة واحدة
        Installment.objects.bulk_create(installments_to_create)
