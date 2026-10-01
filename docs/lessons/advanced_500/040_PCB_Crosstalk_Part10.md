# 040: PCB Crosstalk เจาะลึก Part 10 - Manufacturing Variations (Etch Factor & Glass Weave)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในโลกแห่งความจริง (Real-world Fabrication) การผลิต PCB ทำให้เกิดปัจจัยที่ Rule of Thumb และ Simulation (แบบ Ideal) คาดไม่ถึง:
- **Etch Factor (Trapezoidal Trace):** กรดกัดปริ้นจะกัดขอบด้านบนของทองแดงมากกว่าด้านล่าง ทำให้หน้าตัด Trace เป็นรูปสี่เหลี่ยมคางหมู (Trapezoid) ไม่ใช่สี่เหลี่ยมผืนผ้า (Rectangle) ส่งผลให้ Capacitive Coupling ($C_m$) จริงลดลง (เพราะสันด้านบนห่างกันมากขึ้น) แต่ก็ทำให้ Impedance ผิดเพี้ยนจากที่คำนวณไว้
- **Glass Weave Skew (Fiber Weave Effect):** วัสดุ FR4 หรือวัสดุ High-speed ประกอบด้วยเส้นใยแก้ว (Glass Weave, $Er \approx 6.0$) และเรซิน ($Er \approx 3.0$) สานกัน หาก Differential Pair P และ N วางขนานเป๊ะๆ ไปตามแนวเส้นใย (X หรือ Y) เส้น P อาจทับเส้นใยแก้วเต็มๆ (ความเร็วช้า) ส่วนเส้น N อาจตกในร่องเรซิน (ความเร็วสูง) เกิด Skew ในสายเดียวกัน เปลี่ยน Differential เป็น Common-mode และกลายเป็นแหล่งกำเนิด Crosstalk ชั้นดี!

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **ปราบ Glass Weave:** ในบอร์ดที่วิ่งระดับ 25 Gbps+ (PAM4) ห้ามเดิน Differential แบบ Orthogonal ตรงๆ 90 องศากับขอบบอร์ด ให้เอียงสาย (Zig-zag routing) ประมาณ 10-15 องศา หรือสั่งโรงงานให้ตัดแผ่น PCB แบบทำมุม (Off-angle board routing) เพื่อเฉลี่ยให้เส้น P และ N พาดผ่านใยแก้วสลับกันเท่าๆ กัน
- **Design for Manufacturing (DFM):** ถ้าต้องเผื่อ Etch Factor ตอนตรวจแบบ ให้ถาม Fab House เสมอว่าเขาใช้ Etch Compensation เท่าไหร่ บางครั้งโรงงานแอบขยายเส้นเรา (Pre-compensation) จนไปบีบ Clearance ให้แคบลง ส่งผลให้ Crosstalk เพิ่มขึ้นในหน้างานจริง!

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **製造ばらつき (Seizō baratsuki):** Manufacturing variations
- **エッチングファクター (Etchingu fakutā):** Etch factor
- **ガラス繊維 (Garasu sen'i):** Glass weave / Glass fiber
- **基板反り (Kiban sori):** Board warpage
- **台形 (Daikei):** Trapezoid (รูปหน้าตัดของเส้นทองแดงหลังกัดกรด)

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** ปรากฏการณ์ Glass Weave Effect ส่งผลเสียต่อ Differential Pair ในระบบ High-Speed อย่างไร และจะแก้ไขที่ระดับ PCB Layout ได้อย่างไร?
**คำตอบ:** ใยแก้วและเรซินมีค่า Dielectric Constant (Er) ไม่เท่ากัน หากสายเส้น P และ N พาดผ่านวัสดุต่างชนิดกันไปตลอดทาง จะเกิดความเร็วในการเดินทางไม่เท่ากัน (Phase Skew) ทำให้เกิด Common-mode noise แก้ไขโดยการเดินเส้นทำมุมเอียง (เช่น 10-15 องศา) กับแกนใยแก้ว (หรือหมุนบอร์ดตอนตัด) เพื่อเฉลี่ยผลกระทบให้เท่ากันทั้งคู่
