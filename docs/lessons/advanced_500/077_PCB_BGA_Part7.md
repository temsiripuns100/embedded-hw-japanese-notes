# Lesson 077: BGA Signal Integrity - Crosstalk and Impedance Control

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
สัญญาณความเร็วสูงที่วิ่งผ่าน BGA breakout region มักเจอการเปลี่ยนแปลงของอิมพีแดนซ์ (Impedance Discontinuity) เนื่องจากการลดขนาดความกว้างของเส้นทองแดง (Neck-down) หรืออิทธิพลของ Via.
- **Crosstalk**: ในบริเวณ BGA ที่มีสัญญาณเบียดกันแน่นหนา (Tight coupling) FEXT (Far-End Crosstalk) และ NEXT (Near-End Crosstalk) จะสูงขึ้น การลด Crosstalk สามารถทำได้โดยการใช้ Stripline routing แทน Microstrip หรือเพิ่มระยะห่าง 3W rule (หากพื้นที่เอื้ออำนวย)
- **Impedance Profile**: TDR (Time Domain Reflectometry) มักจะโชว์จุดที่เป็น Capacitive dip บริเวณ BGA pad การชดเชย (Compensation) ทำได้โดยลดขนาด Reference plane ใต้ Pad (Anti-pad cutout) เพื่อลด Parasitic capacitance

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick**: ตอนทำ Neck-down เข้าไปใต้ BGA อย่าลืม Simulation ดูว่า Impedance ตกไปเยอะแค่ไหน บางครั้งยอมให้ Impedance แกว่งได้นิดหน่อยในระยะทางสั้นๆ (Electrically short) ถ้าระยะทางน้อยกว่า 1/10 ของความยาวคลื่นของสัญญาณนั้นๆ
- **Layer Transition**: พยายามรักษา Ground return path ให้ต่อเนื่องเวลาเจาะ Via เลเยอร์ใน BGA. ใช้ Ground transfer via วางไว้ใกล้ๆ Signal via เสมอ

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **インピーダンス整合 (Inpiidansu seigou)**: Impedance matching
- **クロストーク (Kurosutooku)**: Crosstalk
- **リターンパス (Ritaan pasu)**: Return path
- **層間移動 (Soukan idou)**: Layer transition
- **内層 (Naisou)**: Inner layer

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: เพื่อลด Parasitic Capacitance ของ BGA Pad ควรทำอย่างไรกับชั้น Ground (Reference plane) ที่อยู่ติดกัน?
A. เพิ่มความหนาของทองแดง
B. ทำ Anti-pad cutout ให้ใหญ่กว่า Pad ด้านบน
C. เจาะ Microvia ให้มากที่สุด
D. เปลี่ยนไปใช้ Dielectric ที่มีค่า Dk สูงขึ้น
**เฉลย**: B (ทำ Anti-pad cutout) การเอาทองแดงในระนาบอ้างอิงตรงใต้ BGA Pad ออกจะช่วยลด Capacitance ลง ทำให้อิมพีแดนซ์ที่ตกลงไปบริเวณนั้นกลับมาสมดุลใกล้เคียงเป้าหมายมากขึ้น
