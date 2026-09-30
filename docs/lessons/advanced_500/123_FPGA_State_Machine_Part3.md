# FPGA State Machine - Part 3: Handling Metastability & Asynchronous Inputs

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เมื่อ FSM รับสัญญาณที่เป็น Asynchronous (เช่น สัญญาณจากปุ่มกด, สัญญาณจาก Clock Domain อื่น) จะเกิดความเสี่ยงต่อปรากฏการณ์ **Metastability** คือการที่ Flip-Flop เก็บค่าแรงดันไว้ที่ระดับกลาง (ไม่เป็น 0 และไม่เป็น 1) ทำให้ FSM ทำงานผิดพลาด (เข้าสู่ Illegal State)
- การป้องกัน: ต้องใช้ **Synchronizer** (โดยทั่วไปคือ Flip-Flop 2-3 ตัวต่อกันแบบ Shift Register) เพื่อปรับสัญญาณให้เข้ากับ Clock Domain ของ FSM ก่อนนำไปใช้
- Mean Time Between Failures (MTBF): การเพิ่มจำนวน Stage ของ Synchronizer จะเพิ่ม MTBF แบบทวีคูณ ช่วยลดความเสี่ยงให้เหลือน้อยมากๆ ในอายุการใช้งานของระบบ

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Senior Trick**: อย่าเอา Asynchronous Input ไปเข้า Logic Gate เพื่อตัดสินใจเปลี่ยน State โดยตรงเด็ดขาด! ให้ผ่าน 2-FF Synchronizer ก่อนเสมอ และใช้แอตทริบิวต์บอก Synthesis tool (เช่น `(* ASYNC_REG = "TRUE" *)` ใน Vivado) เพื่อบังคับให้ FF ทั้งสองตัววางติดกัน (Placement) ลด Routing Delay ระหว่างกันให้เหลือน้อยที่สุด
- การทำ Debounce สำหรับปุ่มกด ก็เป็นส่วนหนึ่งของการจัดการ Asynchronous input เช่นกัน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- メタスタビリティ (Metasutabiriti) - Metastability
- 非同期信号 (Hidouki Shingou) - Asynchronous Signal
- 同期化 (Doukika) - Synchronization
- 信頼性 (Shinraisei) - Reliability
- チャタリング (Chataringu) - Bouncing (ปุ่มกด), Chattering

## ควิซท้ายบท (Quiz)
**Q1**: ข้อใดคือวิธีที่ถูกต้องในการนำสัญญาณจาก Clock Domain 50MHz มาใช้เป็นเงื่อนไขใน FSM ที่ทำงานที่ 100MHz?
1) ต่อตรงเข้า FSM ได้เลยเพราะความถี่ต่างกัน
2) ผ่าน Inverter 1 ตัวก่อน
3) ผ่าน 2-FF Synchronizer ที่ทำงานด้วย Clock 100MHz ก่อน
4) ใช้ Combinational Logic แปลงสัญญาณ
**เฉลย**: 3) ต้องผ่าน Synchronizer ใน Domain ปลายทางก่อนเสมอเพื่อป้องกัน Metastability
