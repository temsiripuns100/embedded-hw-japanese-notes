# Advanced PCB Stackup - Part 1: High-Speed Impedance Control & Core Concepts (Senior Level)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior Engineer การออกแบบ Stackup ไม่ใช่แค่การเรียงชั้น Copper และ Dielectric แต่เป็นการควบคุม Electromagnetic Field (EM Field) ที่แผ่กระจายรอบๆ Trace 
- **Impedance Control (特性インピーダンス制御):** การคำนวณ Z0 สำหรับ Single-ended และ Zdiff สำหรับ Differential pair จะต้องคำนึงถึงปัจจัยแฝงอย่าง Etch Factor (Trapezoidal cross-section) และ Resin Starvation บริเวณขอบ Trace 
- **Return Path (リターンパス):** กฎเหล็กของการออกแบบ High-speed คือกระแสไฟฟ้าความถี่สูงจะไหลกลับในเส้นทางที่มี Inductance ต่ำที่สุด (Least Inductance Path) ซึ่งก็คือระนาบอ้างอิง (Reference Plane) ที่อยู่ติดกันตรงๆ หากมี Slot หรือ Split plane จะทำให้เกิด Common-mode noise

## 2. ทริคหน้างาน OJT (Field Tricks)
- **OJT Trick 1:** เวลาให้โรงงาน (Fab house) คำนวณ Impedance เผื่อ อย่าลืมขอ Stackup report ก่อนเสมอ โรงงานมักจะปรับ Trace width หรือ Dielectric thickness เล็กน้อยเพื่อให้เข้าเป้า yield หากไม่ตรวจตรงนี้ อาจเจอปัญหาขัดแย้งกับข้อจำกัด DFM ของ Component บางตัว
- **OJT Trick 2:** สำหรับบอร์ดที่ความเร็วเกิน 10 Gbps (เช่น PCIe Gen 4/5) ควรพิจารณาใช้ "Non-Solder Mask Defined (NSMD)" pad เพื่อลด Capacitance แฝงที่ทำให้ Impedance drop บริเวณจุดบัดกรี

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **層構成 (Sōkōsei - โซโคเซ):** Stackup / ชั้นของบอร์ด
- **特性インピーダンス (Tokusei Inpīdansu):** Characteristic Impedance
- **リターンパス (Ritān Pasu):** Return Path
- **エッジファクタ (Ejji Fakuta):** Etch factor (ความลาดเอียงของรอยกัดทองแดง)
- **検図 (Kenzu):** การตรวจสอบแบบ/วงจร (Design Review)
- **承認 (Shōnin):** อนุมัติ (Approve)

**ตัวอย่างประโยคตรวจแบบ:**
"レイヤ3のリターンパスが分断されています。特性インピーダンスの不連続が発生するので、プレーンを修正してください。" 
(Return path ที่ Layer 3 ถูกตัดขาด จะทำให้เกิด Impedance discontinuity กรุณาแก้ไข Plane ด้วยครับ)

## 4. ควิซท้ายบท (Quiz)
**Q1:** ในกรณีที่ Trace อยู่ระหว่าง Plane สองชั้น (Stripline) การขยับ Trace ให้เข้าใกล้ Plane ใด Plane หนึ่งมากขึ้น (Asymmetric Stripline) จะส่งผลต่อ Z0 อย่างไร?
A) Z0 เพิ่มขึ้น
B) Z0 ลดลง
C) Z0 ไม่เปลี่ยนแปลง
*(เฉลย: B) Z0 จะลดลง เนื่องจาก Capacitance ต่อความยาวเพิ่มขึ้นเมื่อระยะห่างกับ Plane ใกล้ขึ้น)*
