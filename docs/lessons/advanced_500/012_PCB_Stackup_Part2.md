# Advanced PCB Stackup - Part 2: Material Selection & Dielectric Properties (Senior Level)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การเลือกใช้วัสดุ (Material Selection) สำหรับบอร์ดความถี่สูงมีความสำคัญอย่างยิ่ง
- **Dk (Dielectric Constant / 誘電率):** ค่านี้ไม่ใช่ค่าคงที่ แต่แปรผันตามความถี่ (Frequency dependent) การเลือกวัสดุต้องดู Dk ที่ Operating frequency ของสัญญาณ
- **Df (Dissipation Factor / 誘電正接):** หรือ Loss Tangent ยิ่งความถี่สูง สัญญาณจะสูญเสียพลังงานไปในรูปของความร้อนในเนื้อ Dielectric วัสดุอย่าง FR4 ทั่วไป (Df ~0.02) ไม่เหมาะกับสัญญาณเกิน 3-5 Gbps ต้องเปลี่ยนไปใช้ Mid-loss หรือ Low-loss material เช่น Megtron 6 (Df ~0.002) หรือ Rogers
- **Copper Foil Types:** ขรุขระ (Roughness) ของฟอยล์ทองแดงส่งผลต่อ Skin Effect ที่ความถี่สูง Standard ED (Electrodeposited) copper จะมีความขรุขระสูง ทำให้ Loss มาก สำหรับ High-speed design ต้องใช้ VLP (Very Low Profile) หรือ HVLP (Hyper Very Low Profile) copper

## 2. ทริคหน้างาน OJT (Field Tricks)
- **OJT Trick 1:** ระวัง "Glass Weave Effect" (Fiber weave effect) ในวัสดุ FR4 ที่ใช้เส้นใยแก้วแบบหลวม (เช่น 106 หรือ 1080) Differential pair ที่วิ่งขนานกับแนวเส้นใยอาจเจอค่า Dk ไม่เท่ากัน ทำให้เกิด Skew (สัญญาณถึงไม่พร้อมกัน) ทางแก้คือให้ Route เฉียง 10-15 องศา หรือใช้เส้นใยแก้วแบบทอแน่น (Spread glass) เช่น 3313 หรือ 2116
- **OJT Trick 2:** อย่าเชื่อ Datasheet Dk/Df แบบตาบอด ค่าพวกนี้มักวัดด้วยวิธีที่ต่างจากการใช้งานจริงบนบอร์ด ควรใช้ค่า Dk/Df ที่สกัดมาจาก "Effective" measurement (เช่น การทำ test coupon แบบ TDR/VNA)

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **誘電率 (Yūdenritsu):** Dielectric Constant (Dk)
- **誘電正接 (Yūdenshōsetsu):** Dissipation Factor (Df)
- **銅箔 (Dōhaku):** Copper foil
- **表面粗さ (Hyōmen arosa):** Surface roughness
- **ガラス繊維 (Garasu sen'i):** Glass fiber / Glass weave
- **材料選定 (Zairyō sentei):** Material selection

**ตัวอย่างประโยคตรวจแบบ:**
"10Gbps以上の信号線には、FR-4ではなく、低損失材料（例：Megtron 6）を使用し、銅箔はHVLPを指定してください。" 
(สำหรับสัญญาณเกิน 10Gbps อย่าใช้ FR-4 กรุณาใช้วัสดุ Low-loss (เช่น Megtron 6) และระบุใช้ทองแดงแบบ HVLP ครับ)

## 4. ควิซท้ายบท (Quiz)
**Q1:** ทำไม Copper Roughness (ความขรุขระของทองแดง) จึงทำให้เกิด Loss มากขึ้นที่ความถี่สูง?
A) เพราะทองแดงขรุขระจะทำให้ Dk ของ Dielectric เปลี่ยนไป
B) เพราะ Skin effect ทำให้กระแสวิ่งที่ผิว ซึ่งผิวที่ขรุขระมีระยะทาง (Path length) ยาวกว่าผิวเรียบ
C) เพราะทำให้เกิด Cross-talk มากขึ้น
*(เฉลย: B) กระแสความถี่สูงจะวิ่งตามขอบผิว (Skin effect) ผิวที่ขรุขระทำให้กระแสต้องวิ่งขึ้นลงตามความขรุขระ ระยะทางรวมจึงเพิ่มขึ้น ทำให้ R สูงขึ้นและ Loss มากขึ้น)*
