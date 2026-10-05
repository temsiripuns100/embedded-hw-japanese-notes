# FPGA State Machine - Part 5: FSM Verification & SystemVerilog Assertions

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
งานระดับ Senior ไม่ใช่แค่เขียน RTL ได้ แต่ต้องยืนยันได้ว่าไร้บั๊ก (Bug-Free) การใช้ SystemVerilog Assertions (SVA) ควบคู่กับ Code Coverage เป็นสิ่งจำเป็น
- **SVA (SystemVerilog Assertions)**: ใช้เขียนเงื่อนไขตรวจสอบ (Checker) ฝังเข้าไปใน RTL หรือ Testbench เช่น ตรวจสอบว่า `FSM จะไม่เข้าสู่ State A และ B พร้อมกัน` หรือ `ถ้ามี Request เข้ามา ต้องมี Acknowledge ตอบกลับภายใน 5 Cycle เสมอ`
- **FSM Coverage**: EDA Tools สามารถคำนวณได้ว่า Testbench ที่เราเขียน ครอบคลุม State ทั้งหมดกี่เปอร์เซ็นต์ (State Coverage) และคลอบคลุมเส้นทางการเปลี่ยน State ทุกเส้นทางหรือไม่ (Transition Coverage)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Senior Trick**: ก่อนส่งแบบไปเข้ากระบวนการ Synthesis ต้องเช็ค FSM Coverage ให้ได้ 100% ถ้ามี State ไหนที่ไม่ถูกแตะเลย (Unreachable State) ต้องหาสาเหตุว่าเป็นบั๊กของ Logic หรือเราตั้งใจใส่ไว้เป็น Safe State ถ้าเป็นอย่างหลัง ให้ใส่ comment pragma เพื่อ exclude ออกจาก Coverage Report
- เวลาเขียน SVA สำหรับ FSM ให้เน้นเช็คเงื่อนไขที่ "ห้ามเกิดขึ้นเด็ดขาด" (Safety property) และ "ต้องเกิดขึ้นแน่ๆ ภายในเวลาจำกัด" (Liveness property)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- 検証 (Kenshou) - Verification
- 網羅率 (Mouraritsu) - Coverage Rate
- アサーション (Asaashon) - Assertion
- 期待値 (Kitaichi) - Expected Value
- 仕様漏れ (Shiyoumore) - Missing Specification / Design Flaw

## ควิซท้ายบท (Quiz)
**Q1**: ข้อใดคือประโยชน์หลักของการวัด Transition Coverage ใน FSM?
1) เพื่อให้รู้ว่าใช้ Flip-Flop ไปกี่ตัว
2) เพื่อดูว่าสายไฟ (Routing) มีการติดขัดหรือไม่
3) เพื่อยืนยันว่า Testbench ของเราสามารถสั่งให้ FSM เปลี่ยน State ตามเส้นทางที่เป็นไปได้ครบถ้วนแล้ว
4) เพื่อบอก Timing Violation ที่เกิดขึ้น
**เฉลย**: 3) Transition Coverage บ่งบอกว่าเงื่อนไขการเปลี่ยน State (Edges ใน State Diagram) ถูกกระตุ้นครบหรือยัง
