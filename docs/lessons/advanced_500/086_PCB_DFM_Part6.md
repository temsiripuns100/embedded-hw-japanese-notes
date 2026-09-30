# Lesson 86: PCB DFM Part 6 - High-Speed Signal Integrity & Controlled Impedance

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
ในระดับ High-Speed Design การควบคุม Impedance (インピーダンス制御) เป็นสิ่งสำคัญที่ไม่สามารถมองข้ามได้ ปัญหาหลักที่มักพบในกระบวนการผลิตคือ ค่า Tolerance ของความหนา Dielectric, ความกว้าง Trace (Line Width/Space), และค่า Dk (Dielectric Constant) ของวัสดุ การออกแบบที่เหมาะสมจะต้องคำนึงถึง TDR (Time Domain Reflectometry) Yield และกำหนด Stackup ที่สามารถผลิตได้จริง (Manufacturability) โดยทั่วไปโรงงานจะขอปรับแก้ความกว้างเส้น (Trace width adjustment) เพื่อให้ได้ค่า Impedance ตามเป้าหมาย (±10%) ดังนั้นเราจึงต้องเว้น Space เผื่อไว้สำหรับการขยายเส้น (Etch factor compensation)

## ทริคหน้างาน OJT (OJT Practical Tricks)
- เวลาสั่งทำบอร์ดที่มี Controlled Impedance อย่าลืมส่ง Impedance Profile หรือ Stackup Requirement ให้โรงงานประเมินล่วงหน้า (Pre-CAM) 
- ถ้าเป็นบอร์ดความถี่สูงมากๆ (เช่น PCIe Gen4/5) ควรพิจารณาสั่งใช้ทองแดงแบบ Low Profile (ロープロファイル銅箔) เพื่อลด Skin Effect loss
- การทำ Differential Pair ควรกำหนดระยะห่างให้สม่ำเสมอ และหลีกเลี่ยงการเดินผ่าน Split plane

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **インピーダンス制御 (Inpiidansu Seigyo):** Controlled Impedance (การควบคุมอิมพีแดนซ์)
- **エッチングファクター (Etchingu Fakutaa):** Etch Factor (แฟกเตอร์การกัดกรด)
- **層構成 (Sou Kousei) / スタックアップ:** Stackup (โครงสร้างชั้น PCB)
- **特性インピーダンス (Tokusei Inpiidansu):** Characteristic Impedance (อิมพีแดนซ์ลักษณะเฉพาะ)
- **配線幅 (Haisen Haba):** Trace width (ความกว้างเส้นทองแดง)

## ควิซท้ายบท (Quiz)
**คำถาม:** การที่โรงงานขอปรับแก้ความกว้างเส้นทองแดงในกระบวนการ CAM เพื่อควบคุม Impedance เรียกว่าอะไรในภาษาญี่ปุ่น และทำไมถึงต้องทำ?
**เฉลย:** เกี่ยวข้องกับ エッチングファクター (Etch factor) หรือการชดเชยการกัดกรด (Compensation) เพราะในกระบวนการกัดกรด เส้นทองแดงจะเล็กลงจากแบบ จึงต้องทำเส้นเผื่อให้ใหญ่ขึ้น เพื่อให้หลังกัดกรดแล้วได้ความกว้างและ Impedance ตามที่ออกแบบไว้
