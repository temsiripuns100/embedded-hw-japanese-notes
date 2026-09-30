# Lesson 24: Vias, Stubs, and Discontinuities (ビア、スタブと不連続点)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ทุกครั้งที่สัญญาณความถี่สูงมุดผ่าน **Via (ビア)** จะเกิด **Impedance Discontinuity (インピーダンス不連続)** เนื่องจาก Via มีคุณสมบัติเป็น Parasitic Capacitance และ Inductance
ปัญหาที่ร้ายแรงที่สุดคือ **Via Stub (スタブ)**: หากสัญญาณวิ่งจากชั้น Top ไปชั้น 2 แต่ใช้ Through-Hole Via รูที่ทะลุต่อไปยังชั้น Bottom จะทำตัวเป็นสายอากาศปลายเปิด (Open-ended transmission line) สัญญาณจะวิ่งลงไปที่ปลาย Stub แล้วสะท้อนกลับมาหักล้างกับสัญญาณหลัก เกิดปัญหาที่เรียกว่า **Quarter-wave resonance**
วิธีแก้คือใช้ **Blind/Buried Vias** หรือเทคนิค **Backdrilling (バックドリル)** เพื่อเจาะเอาทองแดงส่วนที่เป็น Stub ทิ้งไป

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Return Via / Stitching Via:** ทุกครั้งที่สัญญาณเปลี่ยนชั้น Reference Plane ก็เปลี่ยนตาม ดังนั้น "ต้อง" เจาะ GND via (หรือ Stitching capacitor ถ้าข้าม Power plane) ไว้ข้างๆ Via สัญญาณเสมอ เพื่อให้ Return path กระโดดตามมาได้
- **Anti-pad Size:** ขนาดของรูหลบ (Anti-pad) บน Plane รอบๆ Via มีผลต่อ Impedance ของ Via ปรับให้ใหญ่ขึ้นจะช่วยลด Parasitic Capacitance ได้
- **Test Points:** อย่าใส่ Test point บนเส้น High-speed โดยตรง เพราะมันคือ Stub ชนิดหนึ่ง

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ビア (Bia):** Via
- **スタブ (Sutabu):** Stub (ส่วนปลายที่เหลือของ Via)
- **バックドリル (Bakku Doriru):** Backdrill (เทคนิคเจาะเอา Stub ออก)
- **リターンビア (Ritaan Bia):** Return Via / Stitching Via
- **アンチパッド (Anchipaddo):** Anti-pad (Clearance รอบๆ Via)

## ควิซท้ายบท (End of Chapter Quiz)
**Q:** ปรากฏการณ์ใดที่เกิดจาก Via Stub ในวงจรความถี่สูงระดับ Multi-Gigabit?
1. Ground Bounce
2. Signal Resonance (ทำให้สัญญาณบางความถี่หายไป)
3. Thermal Runaway

*เฉลย: 2*
