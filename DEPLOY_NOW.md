# Deploy NOW — 3-step instructions

git repo is initialized and committed locally. ทำ 3 ขั้นตอนนี้ตามลำดับ:

## ขั้น 1: สร้าง GitHub repo (browser, ~1 นาที)

1. ไปที่ **https://github.com/new**
2. กรอก:
   - **Repository name**: `compxm-2026-andrews`
   - **Description**: `Comp-XM 2026 Capsim Simulator — Andrews edition`
   - **Public** หรือ **Private** ก็ได้ (Streamlit Cloud ฟรี 1 private app)
   - **อย่ากดเลือก** "Add README", "Add .gitignore", "Choose license" (เพราะเรามีแล้ว)
3. กด **Create repository**

## ขั้น 2: Push code ขึ้น GitHub (PowerShell, ~30 วินาที)

เปิด PowerShell ที่ folder นี้แล้วรัน (เปลี่ยน `YOUR_USERNAME` เป็น GitHub username ของคุณ):

```powershell
cd "F:\Claude CODE\CAPSIM"
git remote add origin https://github.com/YOUR_USERNAME/compxm-2026-andrews.git
git push -u origin main
```

ถ้าถาม credentials:
- Username: GitHub username
- Password: ใช้ **Personal Access Token** (ไม่ใช่ password) — สร้างที่ https://github.com/settings/tokens เลือก scope `repo`

## ขั้น 3: Deploy บน Streamlit Cloud (browser, ~3 นาที)

1. ไปที่ **https://share.streamlit.io**
2. กด **Sign in with GitHub**
3. กด **New app** (มุมขวาบน)
4. กรอก:
   - **Repository**: `YOUR_USERNAME/compxm-2026-andrews`
   - **Branch**: `main`
   - **Main file path**: `sim/app.py`
   - **App URL** (subdomain): `compxm-andrews` (จะได้ `https://compxm-andrews.streamlit.app`)
5. (Optional) **Advanced settings** to Python version: 3.11
6. กด **Deploy!**

รอ ~3 นาที. Streamlit จะ:
- Clone repo
- pip install -r requirements.txt
- Run streamlit run sim/app.py

เสร็จแล้วได้ URL ใช้ได้ทุก device ทุกที่ — ไม่ต้องลงอะไรเลย

---

## เมื่อ update code (รอบหน้า)

```powershell
cd "F:\Claude CODE\CAPSIM"
git add sim/
git commit -m "Fix bug X"
git push
```

Streamlit Cloud จะ auto-redeploy ภายใน 1 นาที

---

## ถ้าเจอปัญหา

| ปัญหา | วิธีแก้ |
|---|---|
| Push fails "remote rejected" | Repo มีไฟล์อยู่แล้ว — ลบ repo สร้างใหม่ หรือ `git push -f origin main` |
| Streamlit Cloud build fails | เช็ค logs ที่ dashboard. ปกติเป็น dependency issue — update `requirements.txt` |
| App load error "no module sim" | Main file path ผิด — ต้องเป็น `sim/app.py` (มี `sim/` prefix) |
| เปิด app ครั้งแรกช้ามาก | Free tier sleeps after 12hr inactive. รอ ~30 วิ. ตื่นแล้วเร็วปกติ |

---

## URL หลัง deploy

จะได้ URL แบบนี้: **https://compxm-andrews.streamlit.app**

แชร์ URL ได้เลย — เพื่อนเปิดบน:
- ✅ มือถือ (iPhone/Android)
- ✅ iPad / tablet
- ✅ คอมเพื่อน (Windows/Mac/Linux)
- ✅ Chromebook
- ❌ ไม่ต้องลงอะไรเลย
