# Advanced PCB Stackup - Part 2: Impedance Control & Transmission Lines

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ High-speed การควบคุม Impedance เป็นหัวใจหลัก ไม่ใช่แค่การตั้งกฎในโปรแกรม แต่คือการจัด Stackup เพื่อให้ค่า Z0 และ Zdiff ได้ตามที่กำหนด (เช่น 50Ω single-ended, 100Ω differential)
- **Microstrip (Top/Bottom Layer):** สายสัญญาณอยู่ผิวนอก อ้างอิงกับระนาบ (Reference plane) ชั้นถัดไป สัญญาณวิ่งเร็วกว่าเพราะด้านหนึ่งสัมผัสอากาศหรือ Solder mask (ซึ่งมี Dk ต่ำ)
- **Stripline (Inner Layers):** สายสัญญาณอยู่ชั้นใน ถูกขนาบด้วยระนาบทั้งด้านบนและล่าง (Symmetrical หรือ Asymmetrical) ข้อดีคือมีการทำ Shielding ที่ดีกว่า สัญญาณวิ่งช้าลงเล็กน้อยเพราะล้อมรอบด้วย Dielectric เต็มรูปแบบ
- **Coplanar Waveguide (CPW):** การมีระนาบ Ground ขนาบข้างในชั้นเดียวกัน ช่วยลดความหนาของบอร์ดได้ในกรณีที่ชั้นอ้างอิงอยู่ไกลเกินไป

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Reference Plane ที่ดีต้องไม่ขาด:** ข้อผิดพลาดคลาสสิกคือการเดินสาย High-speed ข้ามรอยแยก (Split plane) ของชั้นอ้างอิง ทำให้ Return path ต้องอ้อมไกล เกิดเป็น Inductance และแผ่คลื่น EMI ทันที หากเลี่ยงไม่ได้ต้องมี Stitching capacitor ข้ามรอยแยกนั้น 
- **การชดเชย Etch Factor (エッチングファクタ):** รูปทรงของลายทองแดงบนบอร์ดจริงไม่ได้เป็นสี่เหลี่ยมผืนผ้า (Rectangular) แต่จะเป็นสี่เหลี่ยมคางหมู (Trapezoidal) เวลาผู้ผลิต (Fab) คำนวณ Impedance เขาจะต้องปรับชดเชยความกว้างเส้น (Line width compensation) เราควรให้ความกว้างเส้นเผื่อไว้เล็กน้อย หรือยอมรับการปรับแต่งของ Fab

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **特性インピーダンス (Tokusei Inpiidansu):** Characteristic Impedance / คาแรคเตอริสติกอิมพีแดนซ์
- **リファレンス層 (Rifarensu-sou):** Reference layer / ชั้นระนาบอ้างอิง
- **スリット跨ぎ (Suritto-matagi):** Routing over a split plane / การเดินสายข้ามรอยแยกของระนาบ
- **エッチング残り (Etchingu nokori):** Under-etching / การกัดทองแดงออกไม่หมด
- **線幅 (Sen-haba):** Line width / ความกว้างเส้น (Trace width)

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** เหตุใด Stripline จึงมักมี EMI ที่ต่ำกว่า Microstrip?
1. เพราะวิ่งในอากาศ
2. เพราะถูก Shielding ด้วยระนาบ (Plane) ทั้งด้านบนและด้านล่าง
3. เพราะมีความต้านทานกระแสตรงสูงกว่า
4. เพราะความเร็วในการรับส่งสัญญาณสูงกว่า

*เฉลย: 2*
