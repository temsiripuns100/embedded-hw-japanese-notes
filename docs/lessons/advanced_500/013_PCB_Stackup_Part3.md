# Advanced PCB Stackup - Part 3: Via Structures & Crosstalk Mitigation (Senior Level)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
- **Via Stub Effect:** เมื่อเดินสายสัญญาณความถี่สูงผ่าน Via (เช่น จาก Top ไป Layer 3 บนบอร์ด 8 ชั้น) ส่วนของ Via ที่เหลือ (จาก Layer 3 ถึง Bottom) จะกลายเป็น "Stub" หรือเสาอากาศเปิด (Open stub) ที่ความถี่เรโซแนนซ์ (Quarter-wave resonance) Stub นี้จะดึงสัญญาณให้ยุบตัว (Dip) อย่างรุนแรงใน Insertion Loss (S21) ต้องทำ Backdrilling หรือใช้ Blind/Buried Vias เพื่อกำจัด Stub
- **Crosstalk (NEXT & FEXT):** 
  - NEXT (Near-End Crosstalk) เกิดจากการเหนี่ยวนำข้ามสายที่ฝั่งต้นทาง 
  - FEXT (Far-End Crosstalk) เกิดที่ฝั่งปลายทาง 
  ใน Stripline, FEXT มักจะต่ำมากเพราะ Homogeneous dielectric แต่ใน Microstrip (ผิวหน้า) FEXT จะเด่นชัดกว่า การจัดการระยะห่าง (Spacing > 3W rule) เป็นพื้นฐาน แต่ระดับ Senior ต้องพิจารณาถึง Z-axis crosstalk จาก Via ด้วย

## 2. ทริคหน้างาน OJT (Field Tricks)
- **OJT Trick 1:** การสั่งทำ Backdrill จะมี "Stub Clearance" หรือระยะเผื่อในการเจาะ (มักจะราวๆ 10-15 mil) หมายความว่าเราไม่สามารถเจาะทิ้งจนเกลี้ยงสนิทได้ จะยังเหลือ Stub สั้นๆ เสมอ ต้องนำความยาวนี้ไปจำลอง (Simulate) ดูว่ามีผลกับแบนด์วิดท์หรือไม่
- **OJT Trick 2:** ถ้าต้องเดินสาย Differential Pair เปลี่ยนชั้นผ่าน Via อย่าลืมวาง "Ground Return Vias" ไว้ข้างๆ คู่สัญญาณเสมอ (อย่างน้อย 1-2 รู) เพื่อให้ Return Current วิ่งตามไปได้อย่างราบรื่น ป้องกัน Impedance Mismatch

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ビアスタブ (Bia Sutabu):** Via stub
- **バックドリル (Bakku Doriru):** Backdrilling
- **クロストーク (Kurosutōku):** Crosstalk
- **層間移動 (Sōkan idō):** Layer transition (การเปลี่ยนชั้นเดินสาย)
- **グラウンドリターンビア (Guraundo Ritān Bia):** Ground Return Via
- **ブラインドビア (Buraindo bia):** Blind Via

**ตัวอย่างประโยคตรวจแบบ:**
"高速信号の層間移動箇所にリターンビアがありません。信号ビアの近くにGNDビアを配置してください。" 
(บริเวณที่มีการเปลี่ยนชั้นของสัญญาณ High-speed ไม่มี Return via กรุณาวาง GND Via ไว้ใกล้ๆ กับ Signal via ด้วยครับ)

## 4. ควิซท้ายบท (Quiz)
**Q1:** วิธีใดที่มีประสิทธิภาพที่สุดในการลด Far-End Crosstalk (FEXT) ระหว่างสายสัญญาณคู่ขนานยาวๆ?
A) เปลี่ยนไปเดินสายที่ชั้น Top/Bottom (Microstrip)
B) ย้ายสายไปเดินที่ชั้นภายใน (Stripline)
C) เพิ่มขนาด Via ให้ใหญ่ขึ้น
*(เฉลย: B) Stripline จะถูกล้อมรอบด้วย Dielectric แบบเดียวกันหมด ทำให้ความเร็วคลื่นแม่เหล็ก (Inductive) และคลื่นไฟฟ้า (Capacitive) เท่ากัน ส่งผลให้ FEXT หักล้างกันจนเกือบเป็นศูนย์)*
