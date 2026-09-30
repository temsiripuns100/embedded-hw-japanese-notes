# Advanced PCB Stackup - Part 1: Core Principles & Material Selection

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การออกแบบ Stackup ที่ดีเริ่มต้นที่ความเข้าใจในวัสดุ พื้นฐานที่สุดคือ Core และ Prepreg ค่าความต้านทานและคุณสมบัติทางไฟฟ้าขึ้นอยู่กับ Dielectric Constant (Dk) และ Dissipation Factor (Df)
- **Core (コア):** ชั้นวัสดุแข็งที่มีทองแดงเคลือบมาให้แล้ว (Copper-clad laminate - CCL)
- **Prepreg (プリプレグ):** วัสดุเชื่อมประสาน (Resin-impregnated glass cloth) ที่ยังไม่แข็งตัวเต็มที่ ใช้เพื่อยึด Core แต่ละชั้นเข้าด้วยกันเมื่อผ่านความร้อนและแรงดัน
- **Glass Weave Effect:** การทอใยแก้ว (เช่น 1080, 2116) มีผลต่อความเร็วของสัญญาณใน High-speed design หาก Trace วิ่งพาดผ่านช่องว่างระหว่างใยแก้ว (Resin-rich) สลับกับใยแก้ว (Glass-rich) จะทำให้เกิด Skew ใน Differential pair เรียกว่า "Fiber Weave Effect" วิธีแก้มีทั้งหลีกเลี่ยงการเดินเส้นตรงเป๊ะ (Zig-zag routing) หรือเลือกใช้การทอแบบแน่น เช่น 3313, 1078

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **ระวัง Resin Starvation:** เวลาอัด Prepreg ในชั้นที่มีทองแดงเหลืออยู่น้อย (เช่น ใช้วงจรความหนาแน่นต่ำ) Resin จาก Prepreg ต้องไหลไปเติมเต็มช่องว่าง หากเลือก Prepreg ผิดสเปค หรือจำนวนแผ่นน้อยไป จะเกิดรูพรุน (Void) หรือบอร์ดแยกชั้น (Delamination) ได้ แนะนำให้ใส่ Dummy copper (Thieving) ในชั้นที่ว่างมากๆ เสมอ
- **ความหนาสุดท้ายไม่ตรงเป๊ะ:** ความหนาของ Prepreg ที่ผู้ผลิตระบุคือค่าตอนยังไม่อัด (Unpressed) ความหนาหลังอัด (Pressed thickness) จะลดลงตามเปอร์เซ็นต์ทองแดงที่เหลือในชั้นข้างเคียง ต้องคำนวณ Pressed thickness ให้ดีเพื่อให้ Impedance ได้ตามสเปค

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **基板構成 (Kiban kousei):** Stackup / โครงสร้างชั้นบอร์ด
- **板厚 (Ita-atsu):** Board thickness / ความหนาของบอร์ดรวม
- **層間厚 (Soukan-atsu):** Dielectric thickness / ความหนาระหว่างชั้น
- **銅箔厚 (Douhaku-atsu):** Copper thickness / ความหนาทองแดง
- **ボイド (Boido):** Void / รูอากาศที่เกิดตอนอัดบอร์ด
- **デラミ (Derami):** Delamination / บอร์ดแยกชั้น

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** การใส่ Dummy Copper (銅残し) ในชั้น Layer ที่มีการกัดทองแดงออกไปเยอะ มีข้อดีหลักๆ อย่างไรที่เกี่ยวข้องกับ Stackup?
1. เพื่อให้สวยงาม
2. เพื่อลดค่า Dk ลง
3. ป้องกันการเกิด Resin Starvation และช่วยลดการบิดงอของบอร์ด (Warpage)
4. เพิ่มความเร็วให้สัญญาณ

*เฉลย: 3*
