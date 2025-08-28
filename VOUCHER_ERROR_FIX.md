# حل مشكلة Server Error 500 في السندات

## المشكلة
عند إضافة سند صرف أو قبض، يظهر خطأ Server Error 500 ويجب عمل refresh لرؤية السند المضاف.

## الأسباب المحتملة والحلول

### 1. معالجة الأخطاء المحسنة
تم تحديث views لإضافة معالجة أفضل للأخطاء:
```python
try:
    payment = form.save()
    # ... success response
except Exception as e:
    logger.error(f'Error creating payment voucher: {str(e)}', exc_info=True)
    messages.error(request, f'حدث خطأ: {str(e)}')
    return render(request, 'accounting/vouchers/_payment_form_container.html', 
                  {'form': form}, status=400)
```

### 2. التحقق من صحة البيانات
- إضافة معالجة للنماذج غير الصالحة
- إرجاع النموذج مع الأخطاء في حالة الفشل

### 3. التأكد من وجود البيانات المطلوبة
- **الخزنة (Safe)**: مطلوبة لكل سند
- تم إنشاء سكريبت للتحقق من وجود خزنة افتراضية

### 4. تحسين تجربة المستخدم
- إضافة رسائل خطأ واضحة
- عرض الأخطاء في النموذج نفسه
- استخدام status codes مناسبة (400 للأخطاء)

## خطوات التشخيص

### 1. تفعيل سجلات الأخطاء
```python
import logging
logger = logging.getLogger('accounting')
```

### 2. التحقق من البيانات المطلوبة
```bash
cd /workspace/accounting_app
python3 manage.py shell
>>> from accounting.models import Safe
>>> Safe.objects.count()  # يجب أن يكون > 0
```

### 3. فحص سجلات الخادم
عند حدوث الخطأ، افحص:
- Console output في المتصفح (F12)
- سجلات Django في Terminal
- رسائل الخطأ المفصلة

## التحسينات المطبقة

### 1. في Forms
```python
# إضافة labels واضحة للحقول الفارغة
self.fields['safe'].empty_label = "اختر الخزنة"
self.fields['supplier'].empty_label = "اختر المورد (اختياري)"
```

### 2. في JavaScript
```javascript
// معالجة أخطاء HTMX
document.body.addEventListener('htmx:responseError', function(evt) {
    showErrorMessage('حدث خطأ في العملية. يرجى المحاولة مرة أخرى.');
});
```

### 3. في Templates
- إضافة عرض للأخطاء في النموذج
- تحسين رسائل الخطأ

## الحل النهائي

إذا استمرت المشكلة:

1. **تأكد من وجود خزنة واحدة على الأقل**:
   ```bash
   python3 manage.py shell
   >>> from accounting.models import Safe
   >>> Safe.objects.create(code='MAIN', name='الخزنة الرئيسية', balance=0)
   ```

2. **تحقق من الحقول المطلوبة في النموذج**
3. **افحص سجلات الأخطاء للحصول على تفاصيل أكثر**

## ملاحظات
- الآن عند حدوث خطأ، ستظهر رسالة واضحة بدلاً من Server Error 500
- النموذج سيعرض الأخطاء مباشرة دون الحاجة لـ refresh
- السندات الناجحة ستضاف مباشرة للجدول مع رسالة نجاح