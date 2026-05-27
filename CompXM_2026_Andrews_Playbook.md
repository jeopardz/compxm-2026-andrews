# Comp-XM 2026 — คู่มือละเอียด (Andrews)

> คู่มือที่อธิบายทุกตัวแปรว่าคืออะไร คำนวณยังไง ใช้ตัวเลขจริงจากสนามสอบของคุณ
>
> สำหรับ: **Andrews Corporation** สอบ **30 พฤษภาคม 2026** | 3 attempts
>
> ที่มาข้อมูล: Industry Conditions Report 2026 + Inquirer R0 (Dec 31 2025) + Examination Guide + Guide2Exam

---

## สารบัญ

- **Part 0**: ก่อนเข้าห้องสอบ
- **Part 1**: คะแนนประเมิน — เข้าใจให้ลึก
  - 1.1 โครงสร้าง 1,000 คะแนน
  - 1.2 Board Queries 500 คะแนน
  - 1.3 Balanced Scorecard 500 คะแนน
  - 1.4 Target ที่ Andrews ต้องไปถึง
  - **1.5 📊 Detailed Scoring Reference** — ตารางครบทุก metric
  - **1.6 Recap Scorecard** (จบเกม R4)
  - **1.7 Decision → Metric Mapping**
  - **1.8 Top Priority Actions**
- **Part 2**: Round 1 — ทุกตัวแปรอธิบายละเอียด
- **Part 3**: Round 2-4 — Routine ทุกรอบ (+ TQM Conservative ใหม่)
- **Part 4**: Board Queries — เตรียมตัว
- **Part 5**: Cheatsheet สรุปด่วน (+ HR+TQM Schedule)

---

## Part 0: ก่อนเข้าห้องสอบ

### Schedule วันสอบ (อย่าให้เพี้ยน)

```
08:45        เข้าห้องสอบ
09:00-09:20  อ่านเอกสาร (Industry Conditions + Inquirer R0)
09:20-10:50  R1 Decision + Board Query #1  (1.5 ชม.)
10:50-12:20  R2 Decision + Board Query #2  (1.5 ชม.)
12:20-13:00  พักกลางวัน (40 นาทีเป๊ะ — fixed)
13:00-14:00  R3 Decision + Board Query #3  (1 ชม.)
14:00-15:00  R4 Decision + Board Query #4  (1 ชม.)
15:00-16:00  Board Query #5 (สุดท้าย)      (1 ชม.)
```

### Mindset

**คุณนำอยู่แล้ว** (Stock #1, ROE #1, Market Share 30.6%) — สอบนี้เป็นเรื่อง **"ปกป้องตำแหน่ง"** ไม่ใช่ "ตามให้ทัน"

เปรียบเหมือน **แข่งฟุตบอลที่นำ 3-0 หลังครึ่งแรก** — ครึ่งหลังเล่นเกมรัดกุม ค่อยๆ คุมจังหวะ ไม่ต้องผลีผลามทำ goal เพิ่ม

### เครื่องมือเตรียมก่อนเข้าห้อง

1. **Excel pre-built** กับ formulas (ลิสต์ใน Part 5)
2. **กระดาษ A4** เขียนข้อมูล Andrews + competitor (จากตาราง Part 1 ในไฟล์นี้)
3. **เครื่องคิดเลข** — สำคัญสำหรับ Board Query
4. **ปริ้น Part 5 (Cheatsheet)** ไว้ดูใต้โต๊ะ — drift rates / ideal spots / target

### กฎที่ห้ามลืม

- ❌ **กดต่อรอบแล้วย้อนไม่ได้** — เช็คทุกอย่างก่อนกด
- ❌ ต้องตอบ Board Query อย่างน้อย 1 ข้อก่อน Advance
- ❌ อย่ามองเพื่อน — คนละสนาม คนละคำถาม
- ✅ **มี 3 attempts** — ครั้งแรกใช้แผนนี้ defensive, ครั้ง 2-3 อาจ tweak ถ้าทันเวลา

---

## Part 1: คะแนนประเมิน

### 1.1 โครงสร้าง 1,000 คะแนน — เปรียบเปรย

คะแนนเหมือนข้อสอบที่มี **2 ส่วน**:
- **ส่วนที่ 1: ทำโปรเจ็กต์** (Balanced Scorecard 500) = **ผลการบริหารบริษัท 4 ปี**
- **ส่วนที่ 2: สอบปรนัย** (Board Queries 500) = **5 ชุดคำถาม + final**

**ผ่าน = ~662 คะแนน** (50th percentile จากปี 2025)
**Top เก่ง = 900+** (ทำได้)

---

### 1.2 Board Queries 500 คะแนน — เข้าใจให้ลึก

#### โครงสร้าง

- **5 ชุด** = ชุดละ ~100 คะแนน
- **ออกหลังจบแต่ละรอบ** + ชุดที่ 5 (final) หลังจบ R4
- แต่ละชุดมี **5-8 ข้อ** (multiple choice, true/false, essay บางข้อ)
- **เวลาทำ ~3 นาที/ข้อ** (มีรวมใน 1.5 ชม. ของแต่ละรอบ)

#### หัวข้อยอดฮิตที่ออก (เปรียบเปรย)

เหมือนข้อสอบ MBA แบบย่อ — ถามว่า "คุณ analyze บริษัทเป็นไหม"

| หัวข้อ | ตัวอย่างคำถาม | สูตร |
|---|---|---|
| **Strategic Analysis** | "Andrews อยู่ในกลยุทธ์ไหน?" | (ดู product portfolio + price) |
| **Finance** | "ROS ของ Andrews?" | Net Income ÷ Sales |
| **Marketing** | "Forecast Nano รอบหน้า?" | units × (1 + 0.14) |
| **Accounting** | "Asset Turnover ของ Digby?" | Sales ÷ Total Assets |
| **Operations** | "Plant Util Attic?" | Production ÷ 1st Shift Cap × 100% |
| **TQM** | "Material reduction ของ X?" | (เห็นจาก HR/TQM page) |
| **HR** | "Productivity Index?" | (เห็นจาก HR page) |
| **Situation Analysis** | "ใครจะ stockout รอบหน้า?" | (วิเคราะห์ Inquirer) |

#### เทคนิคทำคะแนน Board Queries สูง

**ก่อนเปิด Query** ทำ 3 อย่างนี้:
1. ดาวน์โหลด Inquirer
2. เปิด Excel ที่ pre-built (Part 5)
3. ใส่ตัวเลขจาก Inquirer ลง Excel

**ระหว่างทำ**:
- **ห้ามเดา** — ทุกข้อคำนวณได้
- ถ้าไม่แน่ใจ → ข้ามไปทำข้ออื่นก่อน
- ตอบครบทุกข้อ (ตอบผิดไม่หักคะแนน)

---

### 1.3 Balanced Scorecard 500 คะแนน — แยกตาม 4 ด้าน

> เปรียบเปรย: เหมือนการบริหารร้านอาหารต้องดู **เงิน + งานหลังบ้าน + ลูกค้า + พนักงาน** = 4 ด้านครบ

#### 🟢 Financial (~125 pts) — ด้านการเงิน

**1. Stock Price** ⭐ สำคัญสุด

**คืออะไร**: ราคาหุ้นปลายปี — สะท้อนว่าตลาดมองบริษัทดีแค่ไหน

**ทำสูงยังไง**:
- EPS (กำไรต่อหุ้น) สูง → ทำ profit สูง
- หุ้นน้อย (ผ่าน buyback) → EPS สูงขึ้น
- Dividend สม่ำเสมอ
- Leverage ปานกลาง (1.8-2.8)
- ห้าม Emergency Loan

**Andrews ตอนนี้**: $95.38 (นำ) → **Target R4: $140+**

**2. Profit (Net Income)**

**คืออะไร**: กำไรสุทธิหลังหักทุกอย่าง

**ทำสูงยังไง**:
- Revenue สูง (ขายดี + ราคาดี)
- COGS ต่ำ (TQM ลด material/labor)
- SG&A ต่ำ (TQM ลด admin)
- Interest ต่ำ (debt น้อย)

**Andrews ตอนนี้**: $20.1M (นำ) → **Target R4: $32M+**

**3. Leverage (Total Assets ÷ Equity)**

**คืออะไร**: อัตราการใช้หนี้ — ยิ่งสูงยิ่งกู้เยอะ

**Sweet spot**: **1.8-2.8** (Andrews ตอนนี้น่าจะ ~1.5-2.0)
- ต่ำกว่า 1.8 = ใช้ debt น้อยไป (asset turnover ต่ำ)
- สูงกว่า 2.8 = หนี้เยอะไป (risky)

**4. EPS (Earnings Per Share)**

**คืออะไร**: กำไรต่อหุ้น = Net Income ÷ shares outstanding

**Andrews ตอนนี้**: $9.80 → Target R4: $15+
- Buyback stock ใน R3-R4 = ดัน EPS

**5. Emergency Loan** ⚠️ ห้ามให้เกิด

**คืออะไร**: ถ้า cash Dec 31 ติดลบ → ระบบให้กู้ฉุกเฉิน
- ดอกเบี้ย = Current Debt rate + **7.5% penalty**
- กระทบ Balanced Scorecard ตรงๆ (เสีย ~100 pts)

**ป้องกัน**: Dec 31 cash ≥ $5M (target $15-30M)

---

#### 🟡 Internal Business Process (~125 pts) — ด้านงานหลังบ้าน

**1. Contribution Margin %**

**คืออะไร**: % ที่ราคาขายเหลือจากต้นทุน variable
- สูตร: **(Price − Material − Labor) ÷ Price**
- Andrews Attic ตอนนี้: ($26 − $8.13 − $7.90) ÷ $26 = **38.3%** ✅

**Target**: ทุก product ≥ 30%, average **≥ 36%**

**ทำให้สูงยังไง**:
- Raise price (ระวัง demand drop)
- Lower material (TQM CPI/GEMI)
- Lower labor (TQM QIT/CCE หรือ raise automation)

**2. Plant Utilization**

**คืออะไร**: % ของ 1st shift capacity ที่ใช้
- = Production ÷ 1st Shift Capacity × 100%
- 100% = ใช้ shift 1 เต็มพอดี
- 200% = ใช้ทั้ง shift 1+2 เต็ม (max)
- **150-200% = Capsim official บอก "ดีต่อ ROA"**

**Andrews ตอนนี้**: Attic 188%, Axe 149%, Art 141%, Ant 121%

**Target**: ทุก product **150-180%** (R1-R3), **180-200% R4**

**3. Days Working Capital**

**คืออะไร**: working capital พอใช้กี่วัน
- = (Current Assets − Current Liabilities) ÷ (Sales ÷ 365)
- **Target: 30-90 วัน**
- ต่ำกว่า 30 = cash ตึง (เสี่ยง Emergency Loan)
- เกิน 90 = cash ล้น (ไม่ productive)

**4. Stock-Out Cost**

**คืออะไร**: ค่าเสียโอกาสจากของหมด stock
- = 0 ดีที่สุด (ผลิตให้ทันที่ขายได้)
- ถ้ามี = แปลว่า forecast ต่ำเกิน

**5. Inventory Carrying Cost**

**คืออะไร**: ค่าเก็บ inventory ที่ขายไม่ออก
- = **12% ต่อปี** ของ inventory value
- Target: < $1M
- ถ้าเยอะ = ผลิตเกิน demand

---

#### 🔵 Customer (~125 pts) — ด้านลูกค้า

**1. Customer Survey Score** ⭐ สำคัญสุด

**คืออะไร**: คะแนนที่ลูกค้าให้ product (0-100)
- คำนวณจาก: Position fit + Price fit + Age fit + MTBF fit
- คูณด้วย Awareness × Accessibility
- December Score = ตัวที่ Inquirer แสดง

**Target**: ≥ 40 ใน segment ที่อยู่
- Andrews Attic Dec 2025 = 30 (Thrift) — **ต้องดันขึ้น**
- Andrews Axe = 27 (Core)
- Andrews Art = 44 (Nano) ✅
- Andrews Ant = 39 (Elite) ✅

**ทำให้สูงยังไง**:
- ตำแหน่ง (Pfmn/Size) ใกล้ Ideal Spot
- Price ใน bottom 1/3 ของ range
- MTBF ใน top 1/3 ของ range
- Age ใกล้ ideal segment
- Awareness 100% (Promo $1.4M+)
- Accessibility 100% (Sales $3.3M+/segment)

**2. Product Count**

**คืออะไร**: จำนวน product ของคุณใน segment
- Andrews มี 4 products (1 ต่อ segment) — เพียงพอ
- ไม่ต้อง launch ใหม่ใน Comp-XM (เกินแก้แล้ว — 4 รอบไม่ทัน)

**3. Awareness %**

**คืออะไร**: % ลูกค้าที่รู้จัก product
- Decay 33%/ปี ถ้าไม่ลง Promo
- $1.5M promo = +36% awareness
- $1.4M = maintain 100%

**Target**: ทุก product ≥ 100%

**4. Accessibility %**

**คืออะไร**: % ลูกค้าที่เข้าถึง product ได้สะดวก (sales channel)
- **ที่ segment level** (ไม่ใช่ product)
- ต้องมี 2+ products/segment ถึงจะ 100%
- $3.3M maintain 100%

**Andrews ตอนนี้**: 1 product/segment → **ceiling แค่ 22%** ❌ (per Section 14.3 ของ Deep Research)

**แต่!** ดูใน Inquirer ตอนนี้ Andrews Accessibility:
- Thrift 62%, Core 58%, Nano 81%, Elite 87% — สูงเพราะมี product มานานแล้ว สะสม accessibility

→ **กลยุทธ์**: รักษา sales budget $2M ขึ้นไปทุก product เพื่อ maintain

---

#### 🟣 Learning & Growth (~125 pts) — ด้านพนักงาน

**1. Employee Productivity (Productivity Index)**

**คืออะไร**: ดัชนี productivity ของพนักงาน (100% = baseline)
- ลงทุน HR (Recruit + Training) → ขึ้นได้ถึง 120-130%
- 110% = ใช้คนน้อยลง 9% (ลด labor cost)

**Andrews ตอนนี้**: 100% (baseline — ยังไม่เคยลง HR)

**Target**: ≥ 110% (R2 ขึ้นไป)

**2. Employee Turnover Rate**

**คืออะไร**: % คนงานที่ลาออก/ปี
- Baseline: ~10%
- ลง HR + Training = ลดได้ -50% → **5% ก็ทำได้**

**Andrews ตอนนี้**: 10%

**Target**: ≤ 7% (R2+)

**3. TQM Cumulative Impacts**

**คืออะไร**: ผลสะสมจาก TQM ทุกรอบ
- Material Cost reduction (max -11.8%)
- Labor Cost reduction (max -14%)
- Admin Cost reduction (max -60%)
- R&D Cycle Time reduction (max -40%)
- Demand increase (max +14.4%)

**Andrews ตอนนี้**: 0% (ยังไม่เคยลง — โอกาส!)

---

### 1.4 Target ที่ Andrews ต้องไปถึง

#### เปรียบสถานะปัจจุบัน vs target

| Metric | R0 (ตอนนี้) | **R4 Target** | ช่องว่างที่ต้องไป |
|---|---|---|---|
| Stock Price | $95.38 | **$140+** | +47% |
| Net Profit | $20.1M | **$32M+** | +59% |
| Cumulative Profit (R1-R4) | — | **$100M+** | — |
| Market Share | 30.6% | **35%+** | +4-5% |
| ROS | 12.3% | **15%+** | +3% |
| ROE | 28.3% | **30%+** | +2% |
| Contribution Margin avg | ~36% | **≥ 38%** | +2% |
| Plant Utilization avg | ~150% | **180%** | +30% |
| Productivity Index | 100% | **≥ 115%** | +15% |
| Turnover Rate | 10% | **≤ 7%** | -3% |
| Customer Survey Score (ทุก seg avg) | ~35 | **≥ 45** | +10 |
| Awareness ทุก product | varies | **100%** | — |
| Emergency Loan | $0 | **$0** | คงไว้ |
| **Total Score (BSC + BQ)** | — | **≥ 900/1000** | — |

#### กลยุทธ์ภาพรวม "Defend & Extend"

```
R1: Foundation (วาง base TQM/HR ก่อนคู่แข่ง + revise Attic ด่วน)
R2: Scale (ทบ TQM/HR + ขึ้น automation)
R3: Lock-In (extract margin + buyback stock)
R4: Harvest (max dividend + retire debt + dump price + reduce TQM)
```

---

### 1.5 📊 Detailed Scoring Reference — ค่าไหน ได้คะแนนอะไร

> ตารางสรุปทุก metric ที่ BSC จับ + threshold ที่ต้องชน + ดูได้ที่ไหน
>
> ใช้เป็น checklist ทุกรอบ — ครบไหม

#### 🟢 Financial Perspective (~125 pts)

| Metric | ดูที่ไหน | Full Credit | Partial | Zero | สูตร / หมายเหตุ |
|---|---|---|---|---|---|
| **Stock Price** | Annual Report / Page 2 Inquirer | ≥ **$80** (Comp-XM) | $40-80 scaled | < $20 | สูงสุดยิ่งดี |
| **Profit** | Income Statement | ≥ **$7M/รอบ** | $1-7M scaled | ≤ $0 | Andrews target $22-32M |
| **Leverage** (Assets/Equity) | Balance Sheet | **1.8 - 2.8** (band) | 1.5-1.8 or 2.8-3.5 | < 1.5 or > 3.5 | Sweet spot 2.0 |
| **ROS** | Income Statement | ≥ **10%** | 1-10% scaled | ≤ 0 | NI ÷ Sales |
| **Asset Turnover** | คำนวณ | ≥ **1.5** (high) | 0.5-1.5 | < 0.5 | Sales ÷ Assets |
| **ROA** | คำนวณ | ≥ **15%** | 5-15% | < 0% | NI ÷ Assets |
| **ROE** | คำนวณ | ≥ **20%** | 10-20% | < 0% | NI ÷ Equity |
| **Emergency Loan** | Income Statement | **$0** | ≤ $5M (−50pts) | > $10M (−100pts) | **ห้ามให้เกิด!** |

#### 🟡 Internal Business Process (~125 pts)

| Metric | ดูที่ไหน | Full Credit | Partial | Zero | สูตร / หมายเหตุ |
|---|---|---|---|---|---|
| **Contribution Margin %** | Income Statement / Production | **≥ 36%** portfolio avg | 30-36% | < 30% | (Price − Mat − Lab) ÷ Price |
| **Plant Utilization** | Production page | **150 - 200%** | 100-150% | < 100% or > 200% | Production ÷ 1st Cap |
| **Days Working Capital** | คำนวณ | **30 - 90 days** | 20-30 or 90-120 | < 20 or > 120 | (CA−CL) ÷ (Sales/365) |
| **Stock-Out Cost** | Inquirer | **$0** | $1-5M | > $10M | ลูกค้าเสียโอกาส |
| **Inventory Carrying Cost** | Income Statement | < **$1M** | $1-5M | > $10M | 12% × inventory |
| **SG&A / Sales Ratio** | Income Statement | **≤ 12%** | 12-18% | > 25% | Lower = better |

#### 🔵 Customer Perspective (~125 pts)

| Metric | ดูที่ไหน | Full Credit | Partial | Zero | สูตร / หมายเหตุ |
|---|---|---|---|---|---|
| **Customer Survey Score** (per segment) | Inquirer Segment Analysis | **≥ 40 ทุก segment** | 20-40 | ≤ 10 | คะแนน 0-100 |
| **Awareness %** (per product) | Inquirer | **≥ 100%** | 70-100% | < 30% | Maintain $1.4M promo |
| **Accessibility %** (per segment) | Inquirer | **≥ 80%** | 50-80% | < 30% | Andrews มี 1/seg = ceiling ~22% (ทฤษฎี) แต่สะสม |
| **Product Count** | Inquirer | 1+ ทุก segment | — | 0 | Andrews มี 4/4 ✓ |
| **Market Share** | Inquirer Market Share Report | ≥ **30%** | 20-30% | < 15% | Andrews R0 = 30.6% |

#### 🟣 Learning & Growth (~125 pts)

| Metric | ดูที่ไหน | Full Credit | Partial | Zero | สูตร / หมายเหตุ |
|---|---|---|---|---|---|
| **Employee Productivity** | HR/TQM page | **≥ 115%** | 100-115% | = 100% | จาก HR investment |
| **Employee Turnover** | HR/TQM page | **≤ 7%** | 7-10% | > 12% | จาก HR investment |
| **TQM Material Reduction** | TQM page | ≥ **−10%** | −5 to −10% | 0% | Max −11.8% |
| **TQM Labor Reduction** | TQM page | ≥ **−12%** | −5 to −12% | 0% | Max −14% |
| **TQM Admin Reduction** | TQM page | ≥ **−50%** | −20 to −50% | 0% | Max −60% |
| **TQM Demand Increase** | TQM page | ≥ **+12%** | +5 to +12% | 0% | Max +14.4% |
| **TQM R&D Cycle Reduction** | TQM page | ≥ **−30%** | −10 to −30% | 0% | Max −40% |

---

### 1.6 🎯 Recap Scorecard (จบเกม R4)

> นอกเหนือจาก 4 รอบ Annual Score มี **Recap Scorecard** ตอนจบเกม
> ใช้ **cumulative averages** ของ 4 รอบ — น้ำหนักต่างจาก Annual

| Recap Metric | Threshold | สำคัญแค่ไหน |
|---|---|---|
| **Cumulative Profit** | ≥ $80M (4 รอบ) | ⭐⭐⭐⭐⭐ น้ำหนักสูงสุด |
| **Ending Stock Price** | ≥ $120 | ⭐⭐⭐⭐⭐ น้ำหนักสูง |
| **Ending Market Cap** | ≥ $200M | ⭐⭐⭐⭐ |
| **Average ROS** | ≥ 12% | ⭐⭐⭐⭐ |
| **Average ROA** | ≥ 15% | ⭐⭐⭐⭐ |
| **Average ROE** | ≥ 25% | ⭐⭐⭐⭐ |
| **Average Asset Turnover** | ≥ 1.5 | ⭐⭐⭐ |
| **Ending Market Share** | ≥ 33% | ⭐⭐⭐ |
| **Cumulative Sales** | ≥ $700M | ⭐⭐⭐ |
| **Average Customer Survey** | ≥ 40 | ⭐⭐ |
| **Average Productivity** | ≥ 110% | ⭐⭐ |

---

### 1.7 🔗 Decision → Metric Mapping (ทำอะไร ได้คะแนนไหน)

> ตารางบอกว่า **decision ของคุณ** กระทบคะแนน metric ไหนบ้าง
> ช่วย prioritize ว่าควรลงทุนอะไรมากสุด

| Decision | กระทบ Financial | กระทบ Internal | กระทบ Customer | กระทบ L&G |
|---|:---:|:---:|:---:|:---:|
| **R&D — Position** | — | — | ✅✅✅ CSS | — |
| **R&D — MTBF** | — | — | ✅ CSS | — |
| **R&D — Revise (Age reset)** | — | — | ✅ CSS | — |
| **Marketing — Price ลด** | ✅ Profit↓ | ✅✅ CM↓ | ✅ CSS↑ | — |
| **Marketing — Promo** | — | — | ✅✅✅ Awareness | — |
| **Marketing — Sales** | — | — | ✅✅✅ Accessibility | — |
| **Production — ผลิตเพิ่ม** | — | ✅ Util, ✅ Inv | — | — |
| **Production — Buy Capacity** | ✅ Assets↑ | ✅ Util | — | — |
| **Production — Automation ↑** | — | ✅✅ Labor↓, CM↑ | — | — |
| **HR — Recruit Spend** | — | ✅ Labor↓ | — | ✅✅ Productivity, Turnover |
| **HR — Training Hours** | — | ✅ Labor↓ | — | ✅✅ Productivity |
| **TQM — CPI Systems** | — | ✅✅ Material↓, CM↑ | — | ✅✅ TQM Material |
| **TQM — QIT** | — | ✅✅ Labor↓, CM↑ | — | ✅✅ TQM Labor |
| **TQM — Vendor/JIT** | — | ✅✅ Material+Admin↓ | — | ✅✅ TQM Material+Admin |
| **TQM — Channel Support** | — | — | ✅ Demand | ✅ TQM Demand |
| **TQM — Concurrent Eng** | — | ✅ R&D faster | — | ✅ TQM R&D Cycle |
| **TQM — QFD** | — | ✅ R&D | ✅✅ Promo/Sales effective | ✅ TQM |
| **Finance — Retire Bond** | ✅✅ Leverage↓ | — | — | — |
| **Finance — Issue Stock** | ❌ EPS dilute | — | — | — |
| **Finance — Buyback Stock** | ✅✅ EPS↑, Stock↑ | — | — | — |
| **Finance — Dividend** | ✅ Stock↑ | — | — | — |
| **Finance — Current Debt** | ✅ Cash↑ | — | — | — |
| **A/R 60-90 days** | — | ✅ Days WC | ✅ CSS | — |
| **A/P 30 days** | — | ✅ Days WC | — | — |

---

### 1.8 🚀 Top Priority Actions — High-Impact Levers

ถ้าต้องเลือก 5 อันดับแรกที่ส่งผลกระแสที่สุดต่อ BSC:

| Priority | Action | Impact |
|---|---|---|
| **#1** | **ห้าม Emergency Loan** ($0 ตลอด) | −100 pts ถ้าเกิด |
| **#2** | **TQM $9M ลง R1** (6 initiatives × $1.5M) | +50-80 pts cumulative (4 quadrants) |
| **#3** | **Revise ทุก product ทุกรอบ** | +30-50 pts Customer + Internal |
| **#4** | **HR Recruit $5K + Train 80hrs** | +20-30 pts L&G + Internal |
| **#5** | **Retire 13.5S2027 R1** | +10-15 pts Financial (Leverage + Profit) |

---

## Part 2: Round 1

### 2.0 ก่อนเริ่ม R1: อ่าน Inquirer R0 (Dec 31 2025)

> เปรียบเปรย: เหมือน scout ทีมคู่แข่งก่อนแข่ง — ต้องรู้ว่าเขาเก่งอะไร แย่อะไร

#### หน้าที่ 1: Front Page
**ดูอะไร**: ตัวเลขรวมของ Andrews vs คู่แข่ง

```
Andrews:  Stock $95.38 ⭐ | Profit $20M | Cumulative $163M ⭐ | Share 30.6% ⭐
Baldwin:  $55.73 | $11M | $119M | 22.4%
Chester:  $44.50 | $7.5M | $131M | 24.7%
Digby:    $53.17 | $10M | $118M | 22.3%
```

**สรุป**: Andrews ทิ้งทุกบริษัท → **strategy ไม่เปลี่ยน, รักษา momentum**

#### หน้าที่ 2: Stocks & Bonds

**ดูอะไร**: Bond ของ Andrews + คู่แข่ง

```
Andrews bonds:
  13.5S2027 ($11.3M @ 13.5%) ← ครบ R2 อีก 1 ปี
  11.2S2032 ($8.84M @ 11.2%)
  11.9S2033 ($7.07M @ 11.9%)

Prime rate รอบหน้า: 8.0%
```

**Insight**: 13.5S2027 ดอกเบี้ยสูงมาก ($1.5M/ปี) — พิจารณา retire R1 (จ่ายค่าธรรมเนียม 1.5% = $170K แต่ save dollar)

#### หน้าที่ 3: Financial Summary

**ดูอะไร**: เปรียบ ROS, Asset Turnover, ROE ของทุกบริษัท
- Andrews นำหมด → **กลยุทธ์ของเรา work**

#### หน้าที่ 4: Production Analysis

**ดู Andrews products**:
```
Attic (Thrift): Plant Util 188% ← เกือบเต็ม 2nd shift
Axe (Core):     Plant Util 149% ← ใช้ 2nd shift บ้าง
Art (Nano):     Plant Util 141% ← ใช้บ้าง
Ant (Elite):    Plant Util 121% ← ใช้น้อย
```

**ดูคู่แข่ง**:
- ใคร revise product ในปีหน้า? (Revision Date 2026)
- ใคร automation ขึ้น?
- ใคร capacity เพิ่ม?

#### หน้าที่ 5-8: Segment Analysis × 4

**สำหรับแต่ละ segment** ดู:
1. **Statistics** — Total industry units, Next Year's Growth Rate
2. **Buying Criteria** (น้ำหนัก) — Position/Price/Age/MTBF
3. **Perceptual Map** — Andrews vs คู่แข่ง อยู่ตรงไหน
4. **Accessibility chart** — ของเราเทียบคู่แข่ง
5. **Market Share Actual vs Potential** — ของเราขายได้น้อยกว่าที่ควรไหม?
6. **Top Products** — รายละเอียดทุก product ใน segment

#### หน้าที่ 11: HR/TQM Report

**ดูอะไร**:
```
ทุกบริษัท Recruit Spend: $0 | Training: 0 hrs | TQM: $0
```

**Insight**: 🎁 **ทุกคนเริ่มจากศูนย์** → คนแรกที่ลง = ชนะ

---

### 2.1 R&D Decisions — อธิบายทุกตัวแปร

> เปรียบเปรย: R&D เหมือน **อัพเกรดเมนูของร้านอาหาร** ให้ตรงรสนิยมลูกค้าที่เปลี่ยนทุกปี

#### ตัวแปร 1: Performance (Pfmn)

**คืออะไร**: ความเร็ว/ความไวของ sensor — แสดงบน Perceptual Map แกน X
- Range: 0-20
- ลูกค้า**ทุก segment ต้องการสูงขึ้น**ทุกปี (drift)

**คำนวณยังไง**:
```
R1 Center = R0 Center + Drift
R1 Ideal  = R1 Center + Offset
```

Drift rates (ปี 2026):
- Thrift: +0.5 | Core: +0.8 | Nano: +0.8 | Elite: +1.1

Offsets (อะไรลูกค้าชอบเทียบกับ center):
- Thrift: +0 | Core: +0.4 | Nano: +0.8 | Elite: +1.1

**สำหรับ Andrews R1**:

| Product | R0 Center Pfmn | + Drift | + Offset | **R1 Ideal Pfmn** | Andrews ปัจจุบัน | Δ ต้อง revise |
|---|---|---|---|---|---|---|
| Attic | 5.7 | +0.5 | +0 | **6.2** | 4.9 | **+1.3** |
| Axe | 7.4 | +0.8 | +0.4 | **8.6** | 7.6 | +1.0 |
| Art | 8.9 | +0.8 | +0.8 | **10.5** | 10.3 | +0.2 |
| Ant | 10.6 | +1.1 | +1.1 | **12.8** | 12.4 | +0.4 |

#### ตัวแปร 2: Size

**คืออะไร**: ขนาดของ sensor — แสดงบน Perceptual Map แกน Y
- Range: 0-20
- ลูกค้าทุก segment ต้องการ**เล็กลง**ทุกปี

**คำนวณ**:
```
R1 Size = R0 Center Size − Drift + Offset
```

| Product | R0 Center Size | − Drift | + Offset | **R1 Ideal Size** | Andrews ปัจจุบัน | Δ |
|---|---|---|---|---|---|---|
| Attic | 14.3 | −0.5 | +0 | **13.8** | 15.1 | −1.3 |
| Axe | 12.6 | −0.8 | −0.4 | **11.4** | 12.4 | −1.0 |
| Art | 9.4 | −1.1 | −1.1 | **7.2** | 7.8 | −0.6 |
| Ant | 11.1 | −0.8 | −0.8 | **9.5** | 9.8 | −0.3 |

#### ตัวแปร 3: MTBF (Mean Time Before Failure)

**คืออะไร**: ความทนทาน หน่วยชั่วโมง — sensor ทำงานได้กี่ชั่วโมงก่อนเสีย
- แต่ละ segment มี **range** ที่ยอมรับ
- ลูกค้าชอบ **top ของ range** (ทุก segment)
- เกิน range = ลูกค้าไม่สนใจเพิ่ม (waste material)
- ต่ำกว่า range = **−16.7% demand ต่อ 1,000 hr**, ที่ −6,000 hr = 0

**ต้นทุน**: $0.30 ต่อ +1,000 hours

**สำหรับ Andrews R1**:

| Product | Segment Range | **ตั้งเป็น** | ปัจจุบัน | Δ | เหตุผล |
|---|---|---|---|---|---|
| Attic | Thrift 14,000-20,000 | **19,000** | 20,000 | −1,000 | ลดลงเล็กน้อย save $0.30 (Thrift price-sensitive) |
| Axe | Core 16,000-22,000 | **22,000** | 22,000 | 0 | top of range ✓ |
| Art | Nano 18,000-24,000 | **24,000** | 24,000 | 0 | top of range ✓ |
| Ant | Elite 20,000-26,000 | **26,000** | 26,000 | 0 | top of range ✓ |

> 💡 ทำไม Attic ลด MTBF? — Thrift Price weight **55%** สำคัญสุด, MTBF weight แค่ 20% → ลด material cost = ลดราคาได้ = ขายดีขึ้น

#### ตัวแปร 4: Age (อายุ product)

**คืออะไร**: เวลาตั้งแต่ revise ครั้งล่าสุด
- หลัง revise → **อายุหารด้วย 2**
- แต่ละ segment ชอบอายุต่างกัน

**ลูกค้าต้องการ age เท่าไหร่**:
- Thrift: **3.0 ปี** (proven product)
- Core: **2.0 ปี**
- Nano: **1.0 ปี**
- Elite: **0.0 ปี** (brand new!)

**สำหรับ Andrews R1** (อายุปัจจุบัน vs target):

| Product | Age R0 | หลัง revise (÷2) | Ideal | Status |
|---|---|---|---|---|
| Attic | **5.1** ⚠️ | 2.55 | 3.0 | 🟡 ใกล้ ideal (2.55 vs 3.0) — ดี |
| Axe | 2.2 | 1.10 | 2.0 | 🔴 หลัง revise จะต่ำเกิน — trade-off |
| Art | 1.1 | 0.55 | 1.0 | 🟡 ต่ำกว่า ideal เล็กน้อย |
| Ant | 1.1 | 0.55 | 0.0 | 🟢 ใกล้ ideal — ดี |

> ⚠️ **Trade-off ของ Axe**: Position weight 16% vs Age weight 20% — revise ดีกว่า เพราะ Position ขยับมากกว่า score gain

#### ตัวแปร 5: Revision Date

**คืออะไร**: วันที่ project R&D เสร็จ
- ก่อนวันนี้ = sensor ขายด้วย spec เก่า
- หลังวันนี้ = sensor ขายด้วย spec ใหม่
- **ต้องตั้งก่อน Dec 31** ของปีนั้นเพื่อขายในปีเดียวกัน
- **ตั้งปลายเดือน ธ.ค.** (Dec 25-31) เพื่อ reset age ก่อนเริ่มปีใหม่

**ค่าใช้จ่าย R&D**:
- 6 เดือน project = $500K
- 1 ปี project = $1M
- 2 ปี project = $2M (ส่วนแรก $1M ปีนี้, ส่วนหลัง $1M ปีถัดไป)

#### 🎯 สรุป R&D สำหรับ Andrews R1

```
═══════════════════════════════════════
ATTIC (Thrift) — Revise ใหญ่
  Pfmn:    4.9 → 6.2   (+1.3)
  Size:    15.1 → 13.8 (−1.3)
  MTBF:    20,000 → 19,000
  Revision Date: 12/28/2026
  คาดการณ์ cost: ~$1.0M

AXE (Core) — Revise ปานกลาง
  Pfmn:    7.6 → 8.6   (+1.0)
  Size:    12.4 → 11.4 (−1.0)
  MTBF:    22,000 (คงเดิม)
  Revision Date: 12/28/2026
  คาดการณ์ cost: ~$700K

ART (Nano) — Revise น้อย
  Pfmn:    10.3 → 10.5 (+0.2)
  Size:    7.8 → 7.2   (−0.6)
  MTBF:    24,000 (คงเดิม)
  Revision Date: 12/28/2026
  คาดการณ์ cost: ~$400K

ANT (Elite) — Revise น้อย-ปานกลาง
  Pfmn:    12.4 → 12.8 (+0.4)
  Size:    9.8 → 9.5   (−0.3)
  MTBF:    26,000 (คงเดิม)
  Revision Date: 12/28/2026
  คาดการณ์ cost: ~$500K

R&D Total: ~$2.6M
═══════════════════════════════════════
```

---

### 2.2 Marketing Decisions — อธิบายทุกตัวแปร

> เปรียบเปรย: Marketing เหมือน **คิดราคาเมนู + การประชาสัมพันธ์ + จัดส่ง**

#### ตัวแปร 1: Price

**คืออะไร**: ราคาขายต่อ unit

**กฎ Comp-XM**:
- แต่ละ segment มี **$10 range**
- ลูกค้าชอบ **bottom of range** (ทุก segment)
- ราคาเกิน range = **−16.7% demand ต่อ $1**
- **$6 เกิน range = demand 0**

**Price ranges (R0 — drop $0 ทุกปี ใน Comp-XM)**:
- Thrift: $14-$26
- Core: $20-$32
- Nano: $28-$40
- Elite: $30-$42

> 📌 หมายเหตุ: Comp-XM price ranges **คงที่** (ไม่ drop $0.50 เหมือน Capstone)

**สำหรับ Andrews R1**:

| Product | Range | Price ปัจจุบัน | **R1 Price** | เหตุผล |
|---|---|---|---|---|
| **Attic** (Thrift) | $14-$26 | $26.00 | **$22.00** | ⭐ Price weight **55%** — ดันต่ำสุดเท่าที่ margin ยอม. ที่ $22 = bottom 1/3 = score เต็ม Price |
| **Axe** (Core) | $20-$32 | $32.00 | **$28.00** | ⭐ Price weight **46%** — bottom 1/3 ($20-$24 = top score, $28 = middle) — เก็บ margin ไว้ |
| **Art** (Nano) | $28-$40 | $40.00 | **$38.00** | Price weight 27% — top 1/3 ok (Position สำคัญกว่า) |
| **Ant** (Elite) | $30-$42 | $42.00 | **$40.00** | Price weight 24% — top 1/3 ok |

> 💡 **Insight**: Andrews ตอนนี้ price สูงสุด range — **กินผลกำไรเต็มที่** แต่เสีย Customer Survey Score ใน Thrift/Core (Chester ตัดราคาอยู่)

#### ตัวแปร 2: Promo Budget

**คืออะไร**: งบโฆษณาต่อ product
- ลงไป → **Awareness สูงขึ้น**
- Awareness = % ลูกค้าที่รู้จัก product

**ตัวเลขสำคัญ**:
- $1,500K = +36% awareness
- $3,000K = +50% (diminishing — $1.5M เพิ่มได้แค่ +14%)
- $1,400K = **maintain 100%** awareness
- Decay: ลด 33%/ปี ถ้าไม่ลง
- Product ใหม่ได้ free +25%

**Andrews ตอนนี้** (จาก Inquirer R0):
- Attic: Awareness 79%
- Axe: 80%
- Art: 78%
- Ant: 77%

**กลยุทธ์ R1**:

| Product | R1 Promo | Result คาดการณ์ |
|---|---|---|
| Attic | **$1,500K** | 79% × (1-0.33) + 36% = 89% |
| Axe | **$1,500K** | 80% × (1-0.33) + 36% = 90% |
| Art | **$1,500K** | 78% × (1-0.33) + 36% = 88% |
| Ant | **$1,500K** | 77% × (1-0.33) + 36% = 88% |
| **รวม** | **$6,000K** | |

> 💡 ทำไมไม่ $3M? — เพิ่ม $1.5M ได้แค่ +14% awareness = ROI ต่ำมาก. ลงทุก product $1.5M ดีกว่า

#### ตัวแปร 3: Sales Budget

**คืออะไร**: งบ sales force ต่อ product
- ทำให้ **Accessibility สูง**
- Accessibility = % ลูกค้าที่ซื้อ/รับบริการได้สะดวก
- ⚠️ **เป็นของ segment** ไม่ใช่ product (ทุก product ใน segment share Accessibility)

**ตัวเลขสำคัญ**:
- $2,000K/product = +22%
- $3,000K/product = ceiling per product (diminishing)
- $4,500K/segment = ceiling per segment (ถ้ามี 2+ products)
- $3,300K/segment = **maintain 100%** accessibility
- ⚠️ ต้องมี **2+ products ใน Fine Cut** ถึงจะ 100%
- Decay 33%/ปี

**Andrews มี 1 product ต่อ segment** → **ceiling แค่ ~22%** ในทางทฤษฎี
- แต่จาก Inquirer: Andrews Accessibility อยู่ที่ 62%/58%/81%/87% — สูงเพราะสะสมมานาน

**กลยุทธ์ R1**:

| Product | R1 Sales |
|---|---|
| Attic | **$2,000K** |
| Axe | **$2,000K** |
| Art | **$2,000K** |
| Ant | **$2,000K** |
| **รวม** | **$8,000K** |

> 💡 ลง $2M ก็เกือบ ceiling แล้ว — ลงเยอะกว่านี้ ROI ต่ำมาก

#### ตัวแปร 4: Forecast (Your Forecast)

**คืออะไร**: ตัวเลขที่คุณคิดว่าจะขายได้ — ใช้คำนวณ revenue ใน proforma

**สูตรพื้นฐาน**:
```
Forecast = (R0 Units Sold) × (1 + Growth Rate) + Bonus
```

**Bonus**:
- +5-10% ถ้า revise positioning ดีกว่าคู่แข่ง
- +5% ถ้า MTBF top of range
- +5% ถ้า Promo เพิ่ม
- −5% ถ้าคู่แข่ง launch product ใหม่

**สำหรับ Andrews R1**:

| Product | R0 Units | Growth | × (1+g) | Bonus | **Forecast Base** | **Pessimistic (90%)** ใส่ใน "Your Forecast" | **Optimistic (115%)** ใส่ใน Production |
|---|---|---|---|---|---|---|---|
| Attic | 1,368 | 11% | 1,518 | +10% (revise + price drop) | 1,670 | **1,500** | **1,920** |
| Axe | 1,827 | 10% | 2,010 | +5% | 2,110 | **1,900** | **2,425** |
| Art | 921 | 14% | 1,050 | +5% | 1,100 | **990** | **1,265** |
| Ant | 772 | 16% | 896 | +10% (age fresh) | 985 | **885** | **1,135** |

> 💡 **เทคนิค Worst/Best Case**: ใส่ Pessimistic ใน "Your Forecast" → proforma revenue ปลอดภัย. ใส่ Optimistic ใน Production Schedule → ไม่ stockout

#### 🎯 สรุป Marketing สำหรับ Andrews R1

```
═══════════════════════════════════════
ATTIC (Thrift)
  Price:       $26 → $22
  Promo:       $1,500K
  Sales:       $2,000K
  Forecast:    1,500 units (pessimistic)

AXE (Core)
  Price:       $32 → $28
  Promo:       $1,500K
  Sales:       $2,000K
  Forecast:    1,900 units

ART (Nano)
  Price:       $40 → $38
  Promo:       $1,500K
  Sales:       $2,000K
  Forecast:    990 units

ANT (Elite)
  Price:       $42 → $40
  Promo:       $1,500K
  Sales:       $2,000K
  Forecast:    885 units

Total Marketing Spend: $14M (Promo $6M + Sales $8M)
═══════════════════════════════════════
```

---

### 2.3 Production Decisions — อธิบายทุกตัวแปร

> เปรียบเปรย: Production = **โรงครัว** — ตัดสินใจว่าทำกี่จาน, ต้องขยายครัวไหม, ซื้อเครื่องอัตโนมัติเพิ่มไหม

#### ตัวแปร 1: Production Schedule

**คืออะไร**: จำนวน units ที่จะผลิตในปีนี้

**สูตร**:
```
Schedule = Forecast + (Target inventory ~5% ของ forecast) − Beginning inventory
```

**สำหรับ Andrews R1** (ใช้ Optimistic forecast):

| Product | Optimistic Forecast | + 5% buffer | − Beginning Inv | **Schedule** |
|---|---|---|---|---|
| Attic | 1,920 | 96 | 761 | **1,255** |
| Axe | 2,425 | 121 | 54 | **2,492** |
| Art | 1,265 | 63 | 267 | **1,061** |
| Ant | 1,135 | 57 | 219 | **973** |

> ⚠️ **ระวัง**: Andrews Attic มี inventory เหลือ 761 units (เพราะปีก่อนผลิตเกิน) — ลด production schedule

#### ตัวแปร 2: Capacity (Buy/Sell)

**คืออะไร**: ความสามารถผลิต 1st shift ต่อปี
- ทำงาน 2 shift = ผลิตได้ 2× ของ 1st shift cap
- 2nd shift labor cost = 1.5× ของ 1st shift

**ราคา**:
- ซื้อใหม่: **$6 + ($4 × automation)** ต่อ unit
- ขายออก: **$0.65** ต่อ $1 ของทุนเดิม (เสีย 35%)
- ใช้ได้ปีถัดไป (ซื้อปีนี้ ใช้ปีหน้า)

**Andrews ตอนนี้**:
| Product | Capacity | Plant Util | Schedule R1 | Needs change? |
|---|---|---|---|---|
| Attic | 1,130 | 188% | 1,255 → 111% | ✅ พอ (ลด util) |
| Axe | 1,200 | 149% | 2,492 → 208% | ⚠️ **เกิน 200%! ต้องซื้อหรือลดผลิต** |
| Art | 728 | 141% | 1,061 → 146% | ✅ พอ |
| Ant | 714 | 121% | 973 → 136% | ✅ พอ |

⚠️ **Axe เกิน capacity** ที่ 208% — แต่ R1 ไม่ทันซื้อ (ใช้ R2) → ต้อง **ลด Schedule เป็น 2,300** (utilization 192% — เกือบเต็มแต่ ok)

> 💡 **กฎ Comp-XM 4 รอบ**: ไม่ซื้อ capacity เพิ่ม R1 — payback ไม่ทัน (ต้อง 2+ ปี). ใช้ 2nd shift แทน

#### ตัวแปร 3: Automation

**คืออะไร**: ระดับ automation ของ line (1.0-10.0)
- เพิ่ม 1 = ลด labor cost ~10%
- เปลี่ยน 1 = **$4/unit ของ capacity**
- สูงเกิน → R&D ช้า (สำคัญสำหรับ Nano/Elite ที่ต้อง revise ทุกรอบ)

**ROI calculation** (จาก Part ก่อนหน้า):
```
Payback (ปี) = $4 / Savings Factor
- ที่ 150% util: payback 2.3 ปี
- ที่ 180% util: payback 1.8 ปี
- ที่ 200% util: payback 1.6 ปี
```

**Comp-XM 4 รอบ — เหลือ 3 รอบหลัง R1** → payback ต้อง < 3 ปี = OK ลงทุน

**สำหรับ Andrews R1**:

| Product | ปัจจุบัน | **R1 New** | Δ | Cost (Cap × $4 × Δ) | เหตุผล |
|---|---|---|---|---|---|
| Attic (Thrift) | 6.0 | **7.0** | +1 | 1,130 × $4 = **$4.52M** | Thrift = Low Tech, ลุยได้ ไม่กระทบ R&D |
| Axe (Core) | 5.0 | **6.0** | +1 | 1,200 × $4 = **$4.80M** | Core = Mid Tech, ลุยได้ |
| Art (Nano) | 4.0 | **4.5** | +0.5 | 728 × $4 × 0.5 = **$1.46M** | Nano = High Tech, ระวัง R&D |
| Ant (Elite) | 4.0 | **4.5** | +0.5 | 714 × $4 × 0.5 = **$1.43M** | Elite = High Tech, ระวัง R&D |
| | | | **รวม** | **$12.21M** | |

#### ตัวแปร 4: Workforce Complement

**คืออะไร**: จำนวนพนักงานทั้งหมด
- ระบบจะแสดง **"Needed Complement"** ที่ Production page
- **ตั้งให้เท่ากับ Needed**

**ผลกระทบ**:
- มากกว่า Needed → คนงานยืน → labor cost พุ่ง
- น้อยกว่า Needed → overtime → labor cost ขึ้น, productivity ลด, turnover เพิ่ม
- น้อยกว่ามาก → **ผลิตไม่ได้ตามแผน** = stockout

> 💡 หลัง set Training Hours แล้ว Needed จะเพิ่ม (เพราะคนงาน train ไม่ทำงาน)

#### 🎯 สรุป Production สำหรับ Andrews R1

```
═══════════════════════════════════════
                Schedule  Capacity     Automation
ATTIC (Thrift)  1,255     hold 1,130   6.0 → 7.0 (+1)
AXE (Core)      2,300     hold 1,200   5.0 → 6.0 (+1)
ART (Nano)      1,061     hold 728     4.0 → 4.5 (+0.5)
ANT (Elite)     973       hold 714     4.0 → 4.5 (+0.5)

Workforce Complement: ตาม Needed (ตั้งหลัง HR/TQM)
Plant Investments: ~$12.2M (Automation only)
═══════════════════════════════════════
```

---

### 2.4 HR Decisions — Comp-XM เวอร์ชันเก่า

> ⚠️ **สำคัญ**: Comp-XM ใช้ HR **เวอร์ชันเก่า** — ต่างจาก Capstone 2.0 ที่คุณเห็น 3 sliders!
>
> Comp-XM HR มี:
> 1. Recruit Spend (ใน HR page)
> 2. Training Hours (ใน HR page)
> 3. Workforce Complement (ใน Production page)

#### ตัวแปร 1: Recruit Spend

**คืออะไร**: เงินใช้ recruit คนใหม่
- **$0-$5,000 ต่อคนใหม่** (+ base $1,000)
- ผล: ↑ Productivity Index, ↓ Turnover
- **Cumulative effect** — ลงทุกรอบ ผลทบ

**กฎทอง**: ลง **$5,000 max ทุกรอบ** ตั้งแต่ R1
- Cost ต่อรอบ ~$50-200K (ขึ้นกับ new employees)
- ROI: labor cost ลด 3-5%/รอบ + turnover ลด

#### ตัวแปร 2: Training Hours

**คืออะไร**: ชั่วโมง training ต่อพนักงานต่อปี
- **0-80 hours**
- **$20/hour**
- ผล: ↑ Productivity Index, ↓ Turnover
- ⚠️ **ระหว่าง training คนงานไม่ทำงาน** → Needed Complement เพิ่ม

**กฎทอง**: ลง **80 hours max ทุกรอบ**
- Cost: 804 พนักงาน × 80 × $20 = $1.29M/ปี
- Workforce ต้องเพิ่ม ~10-15% เพื่อชดเชย training time
- ROI: productivity ขึ้น 5-10%/รอบ

#### ตัวแปร 3: Workforce Complement (ใน Production page)

**คืออะไร**: จำนวนพนักงานทั้งหมด
- ตั้งให้ตรงกับ "Needed Complement" ที่ระบบบอก
- Needed จะคำนวณจาก: Production Schedule + Training Hours + TQM workload

#### 🎯 สรุป HR สำหรับ Andrews R1

```
═══════════════════════════════════════
Recruit Spend:        $5,000 (max)
Training Hours:       80 (max)
Workforce Complement: ตาม Needed (set หลังเสร็จทุก decision อื่น)
HR Cost รวมประมาณ:    ~$1.5M
═══════════════════════════════════════
```

---

### 2.5 TQM Decisions — เลือก initiative ลง

> เปรียบเปรย: TQM = **ลงทุนพัฒนาองค์กร** เพื่อให้บริษัทแข็งแกร่งระยะยาว

#### ภาพรวม TQM

- **10 initiatives** แต่ละตัวลด cost / เพิ่ม demand
- **S-Curve**: <$500K = waste, **$1.5M = sweet spot**, $2M = hard cap
- **Cumulative effect** — ทบทุกรอบ
- **Bundle complementary** เพื่อทะลุ $2M per impact

#### 10 Initiatives — ผลของแต่ละตัว

**Process Management (6 ตัว)**:

| # | Initiative | ผล |
|---|---|---|
| 1 | **CPI Systems** (Continuous Process Improvement) | ↓ Material, ↓ Labor (เล็ก) |
| 2 | **Vendor/JIT** (Just in Time) | ↓ Material, ↓ Admin |
| 3 | **QIT** (Quality Initiative Training) | ↓ Labor |
| 4 | **Channel Support Systems** | ↑ Demand (sales effective) |
| 5 | **Concurrent Engineering** | ↓ R&D Cycle, ↓ R&D Cost |
| 6 | **UNEP Green Program** | ↑ Demand, ↓ Material |

**TQM (4 ตัว)**:

| # | Initiative | ผล |
|---|---|---|
| 7 | **Benchmarking** | ↓ Admin |
| 8 | **Quality Function Deployment (QFD)** | ↓ R&D Cycle, ↑ Promo/Sales |
| 9 | **CCE / 6 Sigma Training** | ↓ Material, ↓ Labor |
| 10 | **GEMI TQEM Sustainability** | ↓ Material, ↓ Labor |

#### Max Cumulative Impacts (ลงครบทุกตัวทุกรอบ)

| Impact | Max |
|---|---|
| Material Cost | **−11.8%** |
| Labor Cost | **−14%** |
| Admin Cost | **−60%** |
| Demand | **+14.4%** |
| R&D Cycle Time | **−40%** |

#### กลยุทธ์ TQM สำหรับ Andrews (Broad Strategy)

**ลง 6 initiatives × $1.5M = $9M**

| Initiative | Spend | Impact หลักที่ได้ |
|---|---|---|
| CPI Systems | $1,500K | ↓ Material (Nano/Elite ที่ material สูง) |
| Vendor/JIT | $1,500K | ↓ Material + ↓ Admin |
| QIT | $1,500K | ↓ Labor |
| Concurrent Engineering | $1,500K | ↓ R&D Cycle (revise ทันรอบ) |
| Channel Support | $1,500K | ↑ Demand |
| UNEP Green | $1,500K | ↑ Demand + ↓ Material |
| **Total** | **$9,000K** | |

> 💡 **ทำไมลง 6 ตัว**: bundle complementary impacts → ทะลุ $2M/impact cap. ลง 6 ตัว $1.5M ดีกว่าลง 3 ตัว $3M

#### 🎯 สรุป TQM สำหรับ Andrews R1

```
═══════════════════════════════════════
CPI Systems:            $1,500K
Vendor/JIT:             $1,500K
QIT (Quality Init.):    $1,500K
Concurrent Engineering: $1,500K
Channel Support:        $1,500K
UNEP Green Program:     $1,500K
Benchmarking:           $0
QFD:                    $0
CCE/6 Sigma:            $0
GEMI TQEM:              $0

Total TQM Spend: $9,000K
═══════════════════════════════════════
```

---

### 2.6 Finance Decisions — อธิบายทุกตัวแปร

> เปรียบเปรย: Finance = **ฝ่ายบัญชี** — บริหารเงินสด, หนี้, ปันผล, การลงทุน

#### ตัวแปร 1: Issue Stock

**คืออะไร**: ออกหุ้นใหม่ขายในตลาด
- **Max 20% ของ shares outstanding/ปี**
- **5% brokerage fee**
- เงินสดเข้า แต่ EPS dilute → กดราคาหุ้น

**สำหรับ Andrews R1**: **$0** (cash พอ + ราคาหุ้นสูง — ไม่อยาก dilute)

#### ตัวแปร 2: Stock Retire (Buyback)

**คืออะไร**: ซื้อหุ้นคืน → ลด shares outstanding
- **Max = lesser of (5% of shares OR total equity)**
- **1.5% brokerage fee**
- ดัน EPS → ดันราคาหุ้น

**สำหรับ Andrews R1**: **$0** (รอ R3-R4 ที่ cash ล้นและราคาหุ้นสูง buyback คุ้มกว่า)

#### ตัวแปร 3: Current Debt (Short-term)

**คืออะไร**: เงินกู้ 1 ปี ดอกเบี้ยตาม credit rating
- Max ~75% AR + 50% inventory + 20% growth
- **ไม่มี brokerage fee**
- ใช้สำหรับ working capital

**สำหรับ Andrews R1**: **$5M** (ถ้าจำเป็น) — รอดูจาก proforma

#### ตัวแปร 4: Issue Long-term Bond

**คืออะไร**: ออกพันธบัตร 10 ปี
- ดอกเบี้ย = Current Debt rate + 1.4% (~9.4% ที่ prime 8%)
- **5% brokerage fee**
- Max 80% ของ Plant & Equipment value
- ใช้สำหรับ capital expenditure

**สำหรับ Andrews R1**: **$0** (มีหนี้ 3 ก้อนแล้ว, ดอกเบี้ย 13.5% เก่ายังสูง — รอ retire ก่อน)

#### ตัวแปร 5: Retire Long-term Bond (Early)

**คืออะไร**: ไถ่บอนด์ก่อนกำหนด
- **1.5% brokerage fee**

**Andrews มี 3 bonds**:
1. **13.5S2027** — face $11.3M, ดอกเบี้ย 13.5%, ครบ R2
2. 11.2S2032 — face $8.84M, ดอกเบี้ย 11.2%, ครบ R7
3. 11.9S2033 — face $7.07M, ดอกเบี้ย 11.9%, ครบ R8

**คำนวณ Retire 13.5S2027 R1**:
- ดอกเบี้ย/ปี = $11.3M × 13.5% = **$1.53M**
- Fee retire = $11.3M × 1.5% = **$170K**
- เหลือ R1 + R2 = 2 ปี × $1.53M = **$3.06M ที่จะจ่าย**
- **Save $3.06M − $170K = $2.89M** ✅

> 💡 **คุ้มมาก** — retire R1 เลย

**สำหรับ Andrews R1**: **Retire 13.5S2027 = $11.3M**

#### ตัวแปร 6: Dividend

**คืออะไร**: จ่ายปันผลให้ผู้ถือหุ้น
- ห้ามเกิน EPS (ตลาด ignore ส่วนเกิน)
- Dividend สม่ำเสมอ = ดันราคาหุ้น

**Andrews EPS R0**: $9.80

**สำหรับ Andrews R1**: **$2.00/share** = 2,051,289 × $2.00 = **$4.10M**

#### ตัวแปร 7: A/R Lag (Accounts Receivable)

**คืออะไร**: ลูกค้าจ่ายเงินกี่วันหลังซื้อ

**กระทบ Customer Survey Score**:
- 90 วัน: 0 (baseline)
- 60 วัน: **−0.7%**
- 30 วัน: **−7%**
- 0 วัน: **−40%**

**สำหรับ Andrews R1**: **30 วัน** (เสีย score 7% แต่ working capital ดี — Comp-XM 4 รอบสั้น cash flow สำคัญ)

#### ตัวแปร 8: A/P Lag (Accounts Payable)

**คืออะไร**: เราจ่าย supplier กี่วันหลังรับของ

**กระทบ Production** (supplier withhold material):
- 30 วัน: −1% material
- 60 วัน: −8%
- 90 วัน: −26%
- 140 วัน: −100% (production หยุด!)

**สำหรับ Andrews R1**: **30 วัน** (safe — เสียแค่ 1%)

#### Cash Flow Check ก่อนตัดสินใจ Finance

ตามแผน R1:
```
ต้องการเงิน:
+ R&D ($2.6M)
+ Marketing ($14M) — promo+sales
+ HR ($1.3M training + $0.2M recruit)
+ TQM ($9M)
+ Automation ($12.2M)
+ Bond retire ($11.3M + $170K fee)
+ Dividend ($4.1M)
─────────────────
รวม cash out: ~$54.9M

มีเงิน:
+ Net Income คาดการณ์ ($24-28M)
+ Cash R0 ($31.5M)
+ Depreciation ($6.5M non-cash)
+ AR collection
─────────────────
เงินที่มี (ไม่รวม debt): ~$62M

ส่วนต่าง: ปลอดภัย ~$7M
```

ถ้าเช็คใน proforma แล้วเงินไม่พอ → **ออก Current Debt $5M**

#### 🎯 สรุป Finance สำหรับ Andrews R1

```
═══════════════════════════════════════
Issue Stock:           $0
Issue Long-term Bond:  $0
Current Debt:          $5M (เผื่อ buffer)
Retire 13.5S2027:      $11.3M (early) — save $2.9M long-run
Dividend:              $2.00/share = $4.1M
A/R Lag:               30 days
A/P Lag:               30 days
═══════════════════════════════════════
```

---

### 2.7 Proforma Review — เช็คก่อน Submit

> เปรียบเปรย: เหมือน **ตรวจการบ้านก่อนส่ง** — ตรวจให้ไม่ผิดพลาด

#### Checklist 9 ข้อ

**1. ✅ Dec 31 Cash ≥ $5M?**
- ดูใน Finance page → "December 31 Cash Position"
- Target $15-30M (safe)
- ถ้าติดลบ → ออก Current Debt เพิ่ม

**2. ✅ No Emergency Loan?**
- ติดสีแดง? → cash ติดลบ → แก้ Finance

**3. ✅ Income Statement Net Margin > 0 ทุก product?**
- ไปที่ Proforma → Income Statement
- ถ้า product ไหน margin ลบ → ตรวจ price/cost

**4. ✅ Contribution Margin ≥ 30% ทุก product?**
- Production page หรือ Income Statement
- ถ้าต่ำ → revise price ขึ้น หรือ ลด material/labor

**5. ✅ Inventory Carrying Cost < $1M?**
- ถ้าเยอะ → ลด Production Schedule

**6. ✅ No Stockout ที่ projected?**
- ดูใน Forecast vs Production
- ถ้าผลิตน้อยกว่า forecast → เพิ่ม schedule

**7. ✅ Days Working Capital 30-90?**
- Proforma → Balance Sheet
- ถ้า > 90 → cash ล้น → เพิ่ม dividend / retire bond
- ถ้า < 30 → cash ตึง → ออก stock/debt

**8. ✅ Leverage 1.8-2.8?**
- = Total Assets ÷ Equity
- ถ้าสูง → retire bond
- ถ้าต่ำ → ออก bond (ใช้ debt มากขึ้น = ROA สูง)

**9. ✅ Balanced Scorecard Preview**
- Proforma → Balanced Scorecard
- ดู projected score แต่ละ quadrant
- ถ้า Customer score ต่ำ → ตรวจ Awareness/Accessibility

---

## Part 3: Round 2-4

### Routine ทุกรอบ (R2, R3, R4)

**เปรียบเปรย**: เหมือน **doctor round** — ตรวจอาการคนไข้ทุกวัน แล้วปรับยา

#### ขั้นตอนที่ 1: เปิด Comp-XM Inquirer

อ่านครบ 11 หน้า (ใช้เวลา ~10 นาที):

```
Page 1   Front Page (Andrews นำไหม? Profit?)
Page 2   Stocks & Bonds (Stock เราขึ้นไหม? Bond rating?)
Page 3   Financial Summary (ROS/ROE vs คู่แข่ง)
Page 4   Production Analysis (capacity/auto/util คู่แข่ง)
Page 5   Thrift Segment Analysis ⭐
Page 6   Core Segment Analysis ⭐
Page 7   Nano Segment Analysis ⭐
Page 8   Elite Segment Analysis ⭐
Page 9   Market Share Report
Page 10  Perceptual Map (เรา vs คู่แข่ง)
Page 11  HR/TQM Report (cumulative impacts)
```

#### ขั้นตอนที่ 2: ตอบ 7 คำถาม

ตอบลงกระดาษ:

```
□ 1. Andrews ยังนำไหม? เสีย market share ที่ segment ไหน?
□ 2. คู่แข่งทำท่าอะไร?
   - Baldwin (Niche High Tech) — revise/launch ใน Nano/Elite ไหม?
   - Chester (Niche Low Tech) — ตัดราคา Thrift/Core ไหม?
   - Digby (Broad — คู่แข่งตรง) — ทำอะไรเหมือนเรา?
□ 3. Product เราอยู่นอก Fine Cut ไหม? (ดู Perceptual Map)
□ 4. Stockout? (ดู Production Analysis → ใครหมด)
□ 5. Inventory เหลือเยอะ? → ลด production
□ 6. Cash Dec 31 ที่ผ่านมา = เท่าไหร่?
□ 7. Bond ใกล้ครบ → retire?
```

#### ขั้นตอนที่ 3: Big 7 Decisions ตามลำดับ (เหมือน R1)

```
1. R&D → 2. Marketing → 3. Production → 4. HR → 5. TQM → 6. Finance → 7. Proforma
```

---

### 🟢 Round 2 (R2) — Theme: Scale Up

> เปรียบเปรย: เหมือน **เก็บผลตอบแทนจากเมล็ดที่ปลูกใน R1** + ปลูกเพิ่ม

#### R&D R2

**คำนวณ R2 Ideal** (จาก ตาราง Part 1 — R2 ideals):

| Product | R2 Ideal (Pfmn/Size) | สำหรับ Andrews | Action |
|---|---|---|---|
| Attic | 6.7/13.3 | Pfmn 6.2 → **6.7**, Size 13.8 → **13.3** | Revise (Δ +0.5/-0.5) |
| Axe | 9.4/10.6 | Pfmn 8.6 → **9.4**, Size 11.4 → **10.6** | Revise (Δ +0.8/-0.8) |
| Art | 11.3/6.1 | Pfmn 10.5 → **11.3**, Size 7.2 → **6.1** | Revise (Δ +0.8/-1.1) |
| Ant | 13.9/8.7 | Pfmn 12.8 → **13.9**, Size 9.5 → **8.7** | Revise (Δ +1.1/-0.8) |

MTBF: ทุก product **คงเดิม** (ไม่ลด ไม่เพิ่ม) — เน้น position
Revision Date: **12/28/2027** ทุก product

#### Marketing R2

- Promo: $1,500K × 4 = **$6M** (continue)
- Sales: $2,000K × 4 = **$8M** (continue)
- Price: **คง R1 price** (ไม่ลดเพิ่ม)
- Forecast: คำนวณตาม R1 actual × (1 + growth) + bonus

#### Production R2

**Automation push**:

| Product | R1 → R2 | Cost |
|---|---|---|
| Attic | 7.0 → **8.0** | 1,130 × $4 = $4.52M |
| Axe | 6.0 → **7.0** | 1,200 × $4 = $4.80M |
| Art | 4.5 → **5.0** | 728 × $4 × 0.5 = $1.46M |
| Ant | 4.5 → **5.0** | 714 × $4 × 0.5 = $1.43M |
| **รวม** | | **$12.21M** |

**Capacity**: ดู Axe — ถ้า R1 ผลิตเต็มแล้ว → **ซื้อเพิ่ม 300 units** ($300 × $34 = $10.2M)

#### HR R2
- Recruit $5,000, Training 80 hrs (continue max)

#### TQM R2
- $1.5M × 6 initiatives (continue same) = $9M

#### Finance R2

**สถานะ Bond ตอนนี้**: ถ้า retire 13.5S2027 ใน R1 แล้ว → เหลือ 2 bonds
- 11.2S2032 ($8.84M) — ยังอีก 5 ปี
- 11.9S2033 ($7.07M) — ยังอีก 6 ปี

**Action R2**:
- ออก Current Debt: $5M (ถ้าจำเป็น จาก capacity ที่ซื้อ)
- Dividend: **$2.50/share** (ขึ้นนิดหน่อย — สะท้อนกำไรดี)
- A/R 30 days, A/P 30 days

#### 🎯 Target R2
| Metric | Target |
|---|---|
| Stock Price | **$110+** |
| Net Profit | **$27M+** |
| Cumulative Profit | $212M |
| Market Share | 32%+ |
| Productivity Index | 105-110% |

---

### 🟡 Round 3 (R3) — Theme: Lock-In Margin

> เปรียบเปรย: เหมือน **บีบกำไรให้สุด** ก่อนปลายเกม

#### R&D R3

**คำนวณ R3 Ideal**:

| Product | R3 Ideal | Action |
|---|---|---|
| Attic | 7.2/12.8 | Revise (Δ +0.5/-0.5) |
| Axe | 10.2/9.8 | Revise (Δ +0.8/-0.8) |
| Art | 12.1/5.0 | Revise (Δ +0.8/-1.1) |
| Ant | 15.0/7.9 | Revise (Δ +1.1/-0.8) |

⚠️ **Ant Pfmn ใกล้ 15** — ระวัง map ขอบที่ 20

#### Marketing R3
- Promo: $1,500K × 4 = $6M
- Sales: $2,000K × 4 = $8M
- Price: คงเดิม

#### Production R3

**Automation final push**:

| Product | R2 → R3 | Cost |
|---|---|---|
| Attic | 8.0 → **9.0** | $4.52M |
| Axe | 7.0 → **7.5** | $2.40M (Δ 0.5) |
| Art | 5.0 → **5.5** | $1.46M |
| Ant | 5.0 → **5.5** | $1.43M |
| **รวม** | | **$9.81M** |

#### HR R3
- Recruit $5,000, Training 80 hrs (continue)

#### TQM R3
- $1.5M × 6 initiatives ($9M) — cumulative ใกล้ cap แล้ว
- หรือสลับเป็น CCE + GEMI + QFD + Benchmarking (ที่ยังไม่เคยลง) เพื่อ unlock impact ใหม่
- ตรวจ Cumulative Impacts ใน HR/TQM page

#### Finance R3

**Action**:
- **Buyback Stock**: 5% ของ shares = ~100K shares × $115 = **$11.5M** (ดัน EPS)
- Dividend: **$3.00/share** = $6M
- Continue maintain debt

#### 🎯 Target R3
| Metric | Target |
|---|---|
| Stock Price | **$120+** |
| Net Profit | **$30M+** |
| Cumulative Profit | $242M |
| Market Share | 33%+ |
| Productivity | 110%+ |
| EPS | $12+ |

---

### 🟠 Round 4 (R4) — Theme: Harvest

> เปรียบเปรย: รอบสุดท้าย = **เก็บเกี่ยวข้าวให้หมดนา** ไม่ต้องปลูกใหม่
>
> ⚠️ **กฎพิเศษ R4**: หลายอย่างที่ปกติทำ ห้ามทำใน R4

#### R&D R4 — Revise น้อย

**คำนวณ R4 Ideal**:

| Product | R4 Ideal |
|---|---|
| Attic | 7.7/12.3 |
| Axe | 11.0/9.0 |
| Art | 12.9/3.9 |
| Ant | 16.1/7.1 |

**กฎ**: Revise ให้พอดี R4 ideal — โครงการสั้น (cost น้อย $300-500K/product)

#### Marketing R4 — **Dump Price**

- **Price ลด $1.00-$1.50** ทุก product → กระตุ้น demand รอบสุดท้าย
- Promo: ลด → **$1,400K** (maintain awareness พอ)
- Sales: ลด → **$1,650K** (maintain accessibility พอ)
- Forecast: **Optimistic** (รับ demand surge จากการลดราคา)

#### Production R4 — **No Capacity, No Automation**

| Decision | Action | เหตุผล |
|---|---|---|
| Capacity | **ห้ามซื้อ** | ใช้ไม่ทันรอบ |
| Automation | **ห้ามขึ้น** | ใช้ไม่ทันรอบ |
| Schedule | สูงสุดเท่าที่ขายได้ | dump inventory |
| 2nd Shift | **ดันถึง 100%** (utilization 200%) | ไม่กังวลรอบหน้า |

#### HR R4 — ลดลง

| Decision | Value | เหตุผล |
|---|---|---|
| Recruit | **$3,000** (ลดจาก $5K) | ไม่ต้องลงทุนเพิ่ม |
| Training | **60 hrs** (ลดจาก 80) | productivity gain ไม่ทันใช้ |

#### TQM R4 — ลด (Conservative — ใหม่!)

> **อัพเดต**: ลดจากเดิม $4.5M เหลือ **$1.5M** (เฉพาะ QFD)

| Initiative | Spend | ทำไม |
|---|---|---|
| **QFD** (Quality Function Deployment) | **$1,500K** | Immediate effect — ↑ Promo/Sales effectiveness ใน R4 |
| ❌ CCE / 6 Sigma | $0 | ROI marginal — ผลใน R4 ปีเดียวไม่คุ้ม |
| ❌ GEMI TQEM | $0 | ROI marginal |
| ❌ Benchmarking | $0 | Admin cap จาก Vendor/JIT แล้ว |
| **Total R4 TQM** | **$1,500K** | |

**ประหยัด $3M จากเดิม → เอาไปทำ**:
- Buyback stock +$3M = ดัน EPS → Stock Price ↑
- หรือ Retire bond +$3M = ลด debt → Leverage ↓

**เหตุผล**:
- R4 = รอบสุดท้าย → benefit แค่ 1 ปี
- TQM cumulative cap → initiative ที่ลง R1-R3 cap แล้ว
- Initiative ใหม่ R4 ROI < 1.0 (ไม่คุ้ม) ยกเว้น **QFD** (immediate marketing effect)

#### Finance R4 — **Max Distribution**

| Decision | Action | เหตุผล |
|---|---|---|
| **Buyback Stock max** | 5% × shares × price | ดัน EPS สุด → stock price สุด |
| **Retire bond ที่เหลือ** | 11.2S2032 + 11.9S2033 ทั้ง 2 ก้อน | ลด debt → improve Balance Sheet |
| **Dividend** | **$4.00-$5.00/share** | max sustainable |
| A/R | 60 days (relax) | เพิ่ม Customer Survey Score |
| A/P | 30 days | safe |

#### 🎯 Target R4 (Final)
| Metric | Target |
|---|---|
| Stock Price | **$140-150** |
| Net Profit | **$32M+** |
| Cumulative Profit (R1-R4) | **$100M+** |
| Market Share | **35%+** |
| Bond Rating | A or AA |
| Final Scorecard | **460+/500** |
| + Board Queries | **440+/500** |
| **Grand Total** | **900+/1000** 🏆 |

---

## Part 4: Board Queries

### Workflow แนะนำ

```
1. หลังจบแต่ละรอบ → กดดู Inquirer ใหม่ทันที
2. เปิด Excel pre-built (Part 5) → ใส่ตัวเลขจาก Inquirer
3. เปิด Board Query → อ่านคำถามทั้งหมดก่อน
4. ทำข้อง่ายๆ ก่อน (ที่คำนวณตรงไปตรงมา)
5. ข้ามข้อยาก ทำต่อท้าย
6. ตอบครบทุกข้อ (ตอบผิดไม่หัก)
7. Save Answer → Submit
```

### หัวข้อยอดฮิต + วิธีตอบ

#### 1. Strategic Analysis

**ตัวอย่าง**: "Andrews ใช้กลยุทธ์อะไร?"

**วิธีตอบ**:
- ดู product portfolio (Andrews มี 4 product, 1/segment) → **Broad Strategy**
- ดู price positioning (ไม่ใช่ bottom-low ไม่ใช่ top-high) → **Differentiator (กลางๆ)**
- = **Broad Differentiator**

#### 2. Financial Calculations

**ตัวอย่าง**: "What is Andrews' ROS in Round X?"

**สูตร**: ROS = Net Income ÷ Sales

**วิธีตอบ**:
1. เปิด Inquirer → Annual Report Andrews → Income Statement
2. หา Net Profit (ตัวสุดท้าย)
3. หา Sales (ตัวบนสุด)
4. หาร → %

#### 3. Forecasting

**ตัวอย่าง**: "Forecast Nano next round if growth is 14%?"

**สูตร**: Current Units × (1 + growth)

**วิธีตอบ**:
1. ดู Page 7 (Nano Segment Analysis) → Total Industry Unit Demand
2. คูณด้วย 1.14

#### 4. Production Decisions

**ตัวอย่าง**: "Should Andrews buy capacity or use 2nd shift?"

**วิธีคิด**:
- ถ้าเหลือ 1-2 รอบ → 2nd shift (ไม่คุ้มซื้อ)
- ถ้าเหลือ ≥3 รอบ + util > 200% + demand จะโต → ซื้อ capacity

#### 5. Bond Rating

**ตัวอย่าง**: "What bond rating if Andrews D/E = 1.2?"

**กฎ**:
- D/E < 0.5 → AAA
- 0.5-1.0 → AA
- 1.0-1.5 → A
- 1.5-2.0 → BBB
- 2.0+ → BB or junk

#### 6. Product Analysis

**ตัวอย่าง**: "Which Andrews product has highest CM%?"

**วิธีตอบ**:
1. เปิด Income Statement → ดูแต่ละ product
2. CM% = (Sales − Variable Cost) ÷ Sales
3. คำนวณทุก product แล้วเปรียบ

### Pre-built Excel Template (เตรียมก่อนสอบ)

```
                Andrews  Baldwin  Chester  Digby
Sales              [_]    [_]     [_]      [_]
Net Income         [_]    [_]     [_]      [_]
Total Assets       [_]    [_]     [_]      [_]
Equity             [_]    [_]     [_]      [_]
Shares             [_]    [_]     [_]      [_]
Stock Price        [_]    [_]     [_]      [_]

Calculated:
ROS = NI/Sales     [auto] [auto]  [auto]   [auto]
ROA = NI/Assets    [auto] [auto]  [auto]   [auto]
ROE = NI/Equity    [auto] [auto]  [auto]   [auto]
AT  = Sales/Assets [auto] [auto]  [auto]   [auto]
Lev = Assets/Eq    [auto] [auto]  [auto]   [auto]
EPS = NI/Shares    [auto] [auto]  [auto]   [auto]
Mkt Cap = Px×Sh    [auto] [auto]  [auto]   [auto]
```

**Per Product**:
```
Product  | Units | Price | Material | Labor | CM/unit | CM% | CM$
[Attic]  | [_]   | [_]   | [_]      | [_]   | [auto]  | [a] | [a]
[Axe]    | ...
```

---

## Part 5: Cheatsheet

### ⚡ ตารางอ้างอิงพิมพ์ไว้ข้างตัว

#### Buying Criteria — Dominant Criterion

```
Thrift  → PRICE 55% (ตั้ง bottom 1/3)
Core    → PRICE 46% (ตั้ง bottom 1/3)
Nano    → POSITION 35% (ใกล้ ideal spot เป๊ะ)
Elite   → AGE 34% (revise ทุกรอบ ให้ age ~0)
```

#### Growth Rate

```
Thrift 11% | Core 10% | Nano 14% | Elite 16%
```

#### Drift Rates (Pfmn+/Size−)

```
Thrift 0.5/0.5 | Core 0.8/0.8 | Nano 0.8/1.1 | Elite 1.1/0.8
```

#### Ideal Spot Offsets

```
Thrift 0/0 | Core +0.4/-0.4 | Nano +0.8/-1.1 | Elite +1.1/-0.8
```

#### R1-R4 Ideal Spots (พิมพ์ไว้!)

| Round | Thrift | Core | Nano | Elite |
|---|---|---|---|---|
| R0 | 5.7/14.3 | 7.8/12.2 | 9.7/8.3 | 11.7/10.3 |
| R1 | 6.2/13.8 | 8.6/11.4 | 10.5/7.2 | 12.8/9.5 |
| R2 | 6.7/13.3 | 9.4/10.6 | 11.3/6.1 | 13.9/8.7 |
| R3 | 7.2/12.8 | 10.2/9.8 | 12.1/5.0 | 15.0/7.9 |
| R4 | 7.7/12.3 | 11.0/9.0 | 12.9/3.9 | 16.1/7.1 |

#### Comp-XM Hard Cap

```
Price $6 outside range = demand 0
MTBF 6,000 hr below = demand 0
Each $1 over/under = −16.7% demand
HR Module: OLD VERSION (Recruit + Training + Workforce)
```

### ⚡ Big 7 Order

```
1. R&D → 2. Marketing → 3. Production → 4. HR → 5. TQM → 6. Finance → 7. Proforma
```

### ⚡ Andrews R1 Decisions Quick Reference

```
═══════════════════════════════════════════════════
R&D:                Pfmn   Size   MTBF   Revision
  Attic (Thrift)    6.2    13.8   19000  12/28/2026
  Axe (Core)        8.6    11.4   22000  12/28/2026
  Art (Nano)        10.5   7.2    24000  12/28/2026
  Ant (Elite)       12.8   9.5    26000  12/28/2026

MARKETING:          Price  Promo  Sales  Forecast
  Attic             $22    $1500  $2000  1500
  Axe               $28    $1500  $2000  1900
  Art               $38    $1500  $2000  990
  Ant               $40    $1500  $2000  885

PRODUCTION:         Sched  Cap    Auto
  Attic             1255   1130   7.0
  Axe               2300   1200   6.0
  Art               1061   728    4.5
  Ant               973    714    4.5
  Workforce: ตาม Needed

HR:
  Recruit Spend: $5,000
  Training: 80 hours

TQM ($1,500K each):
  ✓ CPI Systems
  ✓ Vendor/JIT
  ✓ QIT
  ✓ Concurrent Engineering
  ✓ Channel Support
  ✓ UNEP Green
  Total: $9M

FINANCE:
  Retire 13.5S2027:   $11.3M
  Issue Current Debt: $5M (if needed)
  Dividend:           $2.00/share = $4.1M
  A/R: 30 days | A/P: 30 days
═══════════════════════════════════════════════════
```

### ⚡ Targets Per Round

| Round | Stock | Profit | Cumulative | Market Share |
|---|---|---|---|---|
| R0 | $95 | $20M | $163M | 30.6% |
| **R1** | **$100+** | **$22M+** | $185M | 31%+ |
| **R2** | **$110+** | **$27M+** | $212M | 32%+ |
| **R3** | **$120+** | **$30M+** | $242M | 33%+ |
| **R4** | **$140+** | **$32M+** | **$274M** ⭐ | **35%+** ⭐ |

### ⚡ R4 Special Rules

```
❌ ห้ามซื้อ capacity ใหม่
❌ ห้ามขึ้น automation > +0.5
❌ TQM ลดเหลือ QFD $1.5M เท่านั้น  (Conservative)
❌ HR ลด → Recruit $5K (max), Train 60 hrs
✅ Buyback stock max (5% shares)
✅ Retire bond ที่เหลือ
✅ Max dividend $4-5
✅ Drop price $1-1.5
✅ 2nd shift 100%
✅ A/R 60 days (relax — เพิ่ม Customer Score)
```

### ⚡ HR + TQM Schedule (สรุปทั้ง 4 รอบ)

| Round | HR Recruit | HR Training | TQM | **Total HR+TQM** |
|---|---|---|---|---|
| **R1** | $5,000 | 80 hrs | **$9M** (6 init × $1.5M) | $10.5M |
| **R2** | $5,000 | 80 hrs | **$9M** (6 init × $1.5M) | $10.5M |
| **R3** | $5,000 | 80 hrs | **$6M** (6 init × $1.0M close cap) | $7.5M |
| **R4** | $5,000 | 60 hrs | **$1.5M** (QFD only) | $2.7M |
| **รวม** | | | **$25.5M** | **$31.2M** |

**R4 ประหยัด $3M จาก TQM** → ไปลง Buyback stock หรือ Retire bond แทน

### ⚡ Red Flags ที่เห็นแล้วต้องแก้

```
🔴 Cash Dec 31 < $5M → ออก stock/debt เพิ่ม
🔴 Stockout ใน Courier → เพิ่ม Production Schedule
🔴 Inventory > 200K units → ลด production
🔴 Product นอก Fine Cut → revise ด่วน R&D
🔴 Bond rating ตก > 1 grade → retire debt
🔴 Customer Survey Score < 20 → ตรวจ Position/Price/MTBF/Age
🔴 Emergency Loan = ห้ามให้เกิด (penalty 7.5%)
```

### ⚡ Excel Formulas (เตรียมก่อนสอบ)

```
ROS              = Net Income / Sales
ROA              = Net Income / Total Assets
ROE              = Net Income / Equity
Asset Turnover   = Sales / Total Assets
Leverage         = Total Assets / Equity
EPS              = Net Income / Shares Outstanding
Market Cap       = Stock Price × Shares
CM%              = (Price − Material − Labor) / Price
CM$              = (Price − Material − Labor) × Units
Days WC          = (Current Assets − Current Liab) / (Sales/365)
Forecast         = Current Units × (1 + Growth)
Plant Util       = Production / 1st Shift Capacity × 100%
Payback Auto     = $4 / Plant Utilization Multiplier
```

---

## ภาคผนวก: ลำดับการทำในห้องสอบ R1 (สำหรับ Self-paced)

```
[09:00-09:20] อ่านเอกสาร (20 นาที)
  □ Industry Conditions Report (5 นาที)
    - growth rates: Thrift 11%, Core 10%, Nano 14%, Elite 16%
    - drift rates
    - ideal spot offsets
  □ Comp-XM Inquirer R0 (15 นาที)
    - หน้า 1 Front Page (Andrews นำ)
    - หน้า 2 Stocks & Bonds (13.5S2027 ใกล้ครบ)
    - หน้า 4 Production (capacity/util)
    - หน้า 5-8 Segment Analysis × 4
    - หน้า 11 HR/TQM (ทุกคนยังเป็น 0)

[09:20-10:30] R1 Decisions (70 นาที)
  □ R&D (10 นาที) — set ตามตาราง R1 Ideal
  □ Marketing (10 นาที) — Price/Promo/Sales/Forecast
  □ Production (10 นาที) — Schedule/Automation
  □ HR (5 นาที) — Recruit $5K, Train 80 hrs
  □ TQM (10 นาที) — 6 initiatives × $1.5M
  □ Finance (10 นาที) — Retire bond + dividend
  □ Workforce Complement (5 นาที) — set ตาม Needed
  □ Proforma Review (10 นาที) — checklist 9 ข้อ

[10:30-10:50] Board Query #1 (20 นาที)
  □ เปิด Excel pre-built
  □ ใส่ข้อมูลจาก Inquirer
  □ อ่านคำถามทั้งหมดก่อน
  □ ทำข้อง่ายก่อน
  □ ตอบครบทุกข้อ

[10:50] Submit & Advance to R2
```

---

## ภาคผนวก: ลำดับการทำในห้องสอบ R2-R4 (จังหวะเดียวกัน)

```
[หลังจบรอบก่อน] เปิด Inquirer ใหม่
  □ อ่าน 11 หน้า (10 นาที)
  □ ตอบ 7 คำถาม (5 นาที)
  □ จดลงกระดาษ:
    - Andrews ยังนำไหม?
    - คู่แข่งทำอะไร?
    - Product นอก Fine Cut?
    - Stockout?

[R2-R3] Big 7 Decisions (70 นาที)
  □ R&D (calculate R-ideal จากตาราง)
  □ Marketing
  □ Production (automation push)
  □ HR (continue max)
  □ TQM (continue $9M)
  □ Finance (review bonds)
  □ Proforma Review

[R4] Big 7 Decisions (40 นาที)
  □ R&D (revise พอดี R4 ideal)
  □ Marketing (drop price $1-$1.5)
  □ Production (no capacity, no auto, 2nd shift 100%)
  □ HR (ลด recruit/training)
  □ TQM (ลด)
  □ Finance (buyback, retire bonds, max dividend)
  □ Proforma Review

[Board Query] (เหลือเวลาเท่าที่มี)
  □ Excel + Inquirer
  □ ตอบครบ
```

---

*สร้างจากข้อมูล Comp-XM 2026 จริง — 2026-05-27*
*สอบ 30 พฤษภาคม 2026 — 3 attempts*
*ขอให้ได้ 900+ ครับ! 🏆*
