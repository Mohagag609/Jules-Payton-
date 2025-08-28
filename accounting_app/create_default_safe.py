def create_default_safe():
    # Check if any safe exists
    if not Safe.objects.exists():
        # Create a default safe
        safe = Safe.objects.create(
            code='SAFE001',
            name='الخزنة الرئيسية',
            balance=0
        )
        print(f"تم إنشاء الخزنة الافتراضية: {safe.name}")
    else:
        print("توجد خزائن بالفعل في النظام")

if __name__ == '__main__':
    import django
    import os
    import sys
    
    sys.path.insert(0, '/workspace/accounting_app')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    from accounting.models import Safe
    create_default_safe()