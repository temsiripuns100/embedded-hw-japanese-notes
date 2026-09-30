# บทที่ 20: DFM/DFA and Yield Optimization in Mass Production (การเพิ่ม Yield ในการผลิตจริง)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
Stackup Design ต้องมาพร้อมกับ DFM (Design for Manufacturing) ขั้นสูง:
- **Prepreg Selection for Fill**: การเลือกชนิด Prepreg (เช่น 106, 1080, 2116, 3313, 7628) และจำนวนแผ่น ต้องสอดคล้องกับ Copper Coverage Area หากพื้นที่ที่ต้องเติมเต็ม (Resin Fill) มีมากเกินไป อาจเกิด Void (ช่องว่าง) ทำให้เกิดความชื้นสะสมและ Delaminate (CAF failure)
- **Sequential Lamination Limitations**: จำนวนรอบ Lamination มีผลต่อ Yield (รอบการอัดชั้นยิ่งเยอะ บอร์ดยิ่งแพงและมีโอกาสเสียมาก) การ Optimize Stackup ต้องพยายามลด Lamination Cycle ให้เหลือ 1-2 ครั้งถ้าทำได้

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick #1**: อย่าใช้ Prepreg เบอร์ 106 เดี่ยวๆ (Single Ply) ในชั้นที่เป็น Signal Layer ติดกับ Power/GND ที่มีพื้นที่ว่างกว้างๆ เพราะเรซินอาจไหลไม่พอ เกิด Glass Weave โผล่มาแตะทองแดง (CAF risk) ควรใช้สองแผ่นหรือเบอร์ที่หนาขึ้น
- **OJT Trick #2**: ก่อนส่งแบบเข้า Mass Production ให้ทำ Copper Thieving (การเติมจุดทองแดงที่ไม่ได้ใช้) บริเวณพื้นที่ที่ว่างเปล่า เพื่อบาลานซ์ความหนาแน่นของทองแดงให้สม่ำเสมอ ลดอาการบอร์ดโก่งตัว และช่วยให้กระบวนการกัดแผ่น (Etching) สม่ำเสมอขึ้น

## 3. คำศัพท์ภาษาญี่ปุ่นที่シーในการตรวจแบบ (検図 - Kenzu)
- **歩留まり (Budomari)**: Yield (ผลได้ของการผลิต, % ของดี)
- **ボイド (Boido)**: Void (ช่องว่าง/โพรงอากาศ)
- **プレス工程 (Puresu Kōtei)**: Press/Lamination Process (กระบวนการอัดชั้น)
- **銅箔残存率 (Dōhaku Zanzon-ritsu)**: Copper Remaining Rate / Copper Density
- **製造性考慮設計 (Seizōsei Kōryo Sekkei)**: Design for Manufacturing (DFM)

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: การใช้ Prepreg เพียง 1 แผ่น (Single Ply) ชนิดที่มีเนื้อเรซินต่ำ เช่น 106 ระหว่างชั้นที่มีลายทองแดงน้อยๆ มักจะนำไปสู่ปัญหาข้อใดในกระบวนการ Lamination?
1. ทำให้ความเร็วของสัญญาณเพิ่มขึ้นอย่างควบคุมไม่ได้
2. เรซินไม่เพียงพอต่อการเติมเต็มช่องว่าง เกิด Void และเสี่ยงต่อการเกิด CAF (Conductive Anodic Filament)
3. ค่า Impedance ของแผ่นจะต่ำลงมากเกินไป
4. ลดโอกาสการเกิดบอร์ดโก่ง (Warpage) ได้ดีที่สุด

*เฉลย: 2. เรซินไม่เพียงพอ ส่งผลให้เกิด Resin Starvation หรือ Voids ทำให้เสี่ยงเรื่องความชื้นและชอร์ตข้ามเส้น (CAF)*
