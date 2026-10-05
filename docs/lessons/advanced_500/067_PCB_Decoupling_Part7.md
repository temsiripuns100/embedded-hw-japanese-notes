# PCB Decoupling Part 7: Antiresonance Mitigation

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Antiresonance (反共振) เกิดจากการขนานตัวเก็บประจุต่างค่ากัน ซึ่งความถี่เรโซแนนซ์ของ C ตัวหนึ่ง (ที่มีสมบัติด้าน Inductive) ไปทำงานร่วมกับสมบัติด้าน Capacitive ของ C อีกตัว ส่งผลให้เกิด Peak ของ Impedance ที่สูงมากในโดเมนความถี่ หากความถี่สัญญาณ (เช่น Clock harmonics) ไปตรงกับจุดนี้ จะทำให้เกิด Noise มหาศาลบน Power Plane
การลด Antiresonance สามารถทำได้โดยใช้ C ที่มี ESR เหมาะสม (ESR damping) หรือออกแบบให้ระยะห่างระหว่างความถี่เรโซแนนซ์ของ C แต่ละค่าน้อยลง (ใช้ C ค่าไล่เลี่ยกันแทนที่จะกระโดดข้ามค่า)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **ESR Damping:** บางครั้งเราจงใจเลือกใช้ Tantalum capacitor หรือ C ที่มี ESR สูงกว่าเล็กน้อยมาขนานกับ Ceramic C เพื่อกด Peak ของ Antiresonance ไม่ให้ทะลุ $Z_{target}$
- **Simulation Validation:** อย่าเชื่อค่า C ที่แนะนำใน Datasheet แบบหลับหูหลับตา เพราะ Layout ESL จะเปลี่ยนพฤติกรรมทั้งหมด วิศวกรซีเนียร์จะสกัดพารามิเตอร์ของ PCB (S-parameters) และรัน AC sweep simulation ร่วมกับ C-models เสมอ

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
1. **Antiresonance Peak:** 反共振ピーク (Hankyoushin piiku)
2. **ESR Damping:** ESRダンピング (ESR danpingu)
3. **Power Plane:** 電源プレーン (Dengen pureen)
4. **Resonance Frequency:** 共振周波数 (Kyoushin shuuhasuu)
5. **Datasheet:** データシート (Deetashiito)

## ควิซท้ายบท (Quiz)
**คำถาม:** วิธีใดต่อไปนี้เป็นวิธีแก้ปัญหา Antiresonance peak ที่เกิดจากการต่อ Capacitor สองค่าขนานกัน?
1. เปลี่ยนไปใช้ Capacitor ค่าเดียวกันทั้งหมด
2. เพิ่มตัวต้านทานอนุกรมขนาดใหญ่ 1kOhm
3. ใช้ Capacitor ที่มี ESR สูงขึ้นในตำแหน่งที่เหมาะสม (ESR Damping)
4. ถูกทั้งข้อ 1 และ 3

*เฉลย:* ข้อ 4 (การใช้ Capacitor ค่าเดียวกันทั้งหมดช่วยลดจุดตัด หรือการใช้ ESR damping ก็ช่วยลด peak ได้)
