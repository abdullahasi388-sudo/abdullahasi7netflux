# 🎬 Netflux - Netflix Clone

نسخة كاملة من Netflix مع جميع المميزات!

---

## 📁 ملفات المشروع:

### الملفات الأساسية:
- **`simple_netflux.py`** - التطبيق الرئيسي (Flask)
- **`RUN_SIMPLE.bat`** - تشغيل السيرفر المحلي
- **`data/`** - قاعدة البيانات (JSON)
- **`venv/`** - بيئة Python

### ملفات ngrok (للوصول العام):
- **`ngrok.exe`** - برنامج ngrok
- **`NGROK_SIMPLE.bat`** - تشغيل ngrok
- **`SETUP_NGROK_TOKEN.bat`** - إعداد ngrok (مرة واحدة)
- **`NGROK_INSTRUCTIONS_ARABIC.md`** - دليل ngrok بالعربي

### الوثائق:
- **`README.md`** - دليل المشروع بالإنجليزية
- **`HOW_TO_RUN_ARABIC.md`** - دليل التشغيل بالعربية
- **`ProgramlamaLabII_Proje2_FINAL.md`** - وثائق المشروع النهائية

---

## 🚀 طريقة التشغيل:

### 1️⃣ التشغيل المحلي (على جهازك فقط):
```
Double-click: RUN_SIMPLE.bat
افتح: http://localhost:5000
```

### 2️⃣ التشغيل العام (مشاركة مع العالم):
```
1. Double-click: RUN_SIMPLE.bat (اتركه شغال)
2. Double-click: NGROK_SIMPLE.bat
3. انسخ الرابط: https://xxxxx.ngrok-free.app
4. شارك الرابط مع أي شخص!
```

---

## 🔐 الحسابات:

**Admin:**
- Email: admin@netflux.com
- Password: admin123

**المستخدمين:**
- يمكن التسجيل من صفحة "Üye olun"

---

## 🎯 المميزات:

### ✅ المستخدمين:
- تسجيل الدخول
- إنشاء حساب جديد
- المفضلة
- سجل المشاهدة
- حفظ تقدم المشاهدة تلقائياً

### ✅ المحتوى:
- 20 فيلم ومسلسل (تركي + أنمي)
- مشغل فيديو HTML5
- دعم YouTube
- صور احترافية

### ✅ الإدارة (Admin):
- إضافة محتوى جديد
- تعديل المحتوى
- حذف المحتوى
- إدارة المستخدمين

### ✅ التصميم:
- تصميم احترافي مثل Netflix
- متجاوب مع جميع الأجهزة
- تأثيرات حركية
- ألوان Netflix الأصلية

---

## 📊 قاعدة البيانات:

الملفات في مجلد `data/`:
- **`users.json`** - المستخدمين
- **`content.json`** - الأفلام والمسلسلات
- **`favorites.json`** - المفضلة
- **`watch_history.json`** - سجل المشاهدة
- **`watch_progress.json`** - تقدم المشاهدة

---

## 🌐 استخدام ngrok:

### إعداد ngrok (مرة واحدة):
1. سجل حساب مجاني: https://dashboard.ngrok.com/signup
2. احصل على token: https://dashboard.ngrok.com/get-started/your-authtoken
3. Double-click: `SETUP_NGROK_TOKEN.bat`
4. الصق الـ token

### تشغيل ngrok:
1. شغّل السيرفر: `RUN_SIMPLE.bat`
2. شغّل ngrok: `NGROK_SIMPLE.bat`
3. انسخ الرابط من سطر "Forwarding"
4. شارك الرابط!

---

## 🛠️ المتطلبات:

- Python 3.x
- Flask
- ngrok (للوصول العام فقط)

---

## 📝 ملاحظات:

- السيرفر المحلي: `http://localhost:5000`
- الشبكة المحلية: `http://YOUR_IP:5000`
- ngrok (عام): `https://xxxxx.ngrok-free.app`

- ngrok المجاني:
  - الرابط يتغير كل مرة
  - جلسة واحدة في نفس الوقت
  - 40 اتصال في الدقيقة

---

## 🎓 المشروع:

هذا المشروع تم تطويره كجزء من:
- **المادة:** Programlama Lab II
- **المشروع:** Proje 2
- **الجامعة:** 2.sınıf - 2 dönem

---

## 📞 الدعم:

إذا واجهت أي مشكلة:
1. تأكد من تثبيت Python و Flask
2. تأكد من تشغيل السيرفر قبل ngrok
3. تحقق من Windows Firewall
4. راجع ملف `NGROK_INSTRUCTIONS_ARABIC.md`

---

## ✨ الخلاصة:

**للاستخدام المحلي:** `RUN_SIMPLE.bat`
**للمشاركة العامة:** `RUN_SIMPLE.bat` + `NGROK_SIMPLE.bat`

**تم بنجاح! 🎉**
