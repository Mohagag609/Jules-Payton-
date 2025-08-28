# دليل حل مشكلة التنسيقات

## المشكلة
كانت التنسيقات لا تعمل بشكل صحيح في التطبيق بسبب عدم بناء ملف CSS من Tailwind بشكل صحيح.

## الحل

### 1. إنشاء ملف المصدر لـ Tailwind CSS
تم إنشاء الملف `/accounting_app/static/src/tailwind.css` بالمحتوى التالي:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 2. تحديث ملف package.json
تم تحديث الملف لإضافة سكريبتات لبناء CSS:
```json
{
  "scripts": {
    "build-css": "tailwindcss -i ./accounting_app/static/src/tailwind.css -o ./accounting_app/static/css/tailwind.css --minify",
    "watch-css": "tailwindcss -i ./accounting_app/static/src/tailwind.css -o ./accounting_app/static/css/tailwind.css --watch"
  }
}
```

### 3. تثبيت التبعيات وبناء CSS
```bash
npm install
npm run build-css
```

### 4. التحقق من التنسيقات
يمكنك زيارة `/test-styles/` لرؤية صفحة اختبار التنسيقات.

## الأوامر المفيدة

### لبناء CSS مرة واحدة:
```bash
npm run build-css
```

### لمراقبة التغييرات وإعادة البناء تلقائياً:
```bash
npm run watch-css
```

### لتشغيل الخادم (بعد تثبيت متطلبات Python):
```bash
cd accounting_app
python3 manage.py runserver
```

## ملاحظات مهمة
- تأكد من تشغيل `npm run build-css` بعد أي تعديل على القوالب أو إضافة فئات Tailwind جديدة
- في بيئة الإنتاج، يجب بناء CSS كجزء من عملية النشر
- الملف `/accounting_app/static/css/tailwind.css` هو الملف المترجم ويجب عدم تعديله يدوياً