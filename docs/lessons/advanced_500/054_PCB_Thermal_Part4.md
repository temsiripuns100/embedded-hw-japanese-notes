# 054: PCB Thermal Management - Part 4: Thermal Simulation and Measurement
## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
1. **Thermal Simulation (熱流体解析):** การใช้ CFD (Computational Fluid Dynamics) อย่าง Flotherm หรือ IcePak ในการจำลอง. Senior Engineer ต้องกำหนด Boundary conditions ให้ถูกต้อง เช่น Ambient Temp, Gravity direction (สำหรับ Natural convection), และ Power dissipation ของ IC แต่ละตัว. โมเดลของ IC (เช่น 2-Resistor model หรือ Delphi model) มีผลต่อความแม่นยำสูง.
2. **Thermal Measurement:** การวัดจริงใน Lab. Thermocouple (Type K, T) เป็นที่นิยม ต้องระวังขนาดของปลาย Thermocouple ยิ่งใหญ่ยิ่งดึงความร้อนจากจุดที่วัด ทำให้ค่าที่วัดได้ต่ำกว่าความเป็นจริง (Observer effect). การใช้ Thermal Camera (IR Camera) ต้องระวังค่า Emissivity ของโลหะสะท้อนแสง ให้ทาสีดำทับหรือใช้เทปกาวดำแปะก่อนวัด.

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **Ghetto Emissivity Fix:** ตอนส่องกล้อง IR กล้องมักจะวัดอุณหภูมิทองแดงเงาๆ พลาด ให้เอา Marker สีดำด้านระบายทับจุดที่ต้องการส่องกล้อง จะได้ค่าที่แม่นยำขึ้นมาก.
- **Corner Case Testing:** การจำลองในซอฟต์แวร์มักสวยงาม แต่อย่าลืมทดสอบจริงในตู้จำลองสภาพอากาศ (Thermal Chamber) พร้อมรันโหลดสูงสุด (Full load) เป็นเวลานาน (Soak test).

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **熱解析 (Netsukaiseki):** Thermal simulation / analysis
- **熱電対 (Netsudentui):** Thermocouple
- **放射率 (Housharitsu):** Emissivity
- **恒温槽 (Kouonsou):** Thermal chamber

## ควิซท้ายบท (Quiz)
1. เมื่อใช้กล้องถ่ายภาพความร้อน (IR Camera) วัดอุณหภูมิผิวของบัดกรีหรือชิ้นส่วนโลหะเงาๆ ทำไมค่าที่ได้มักไม่ถูกต้อง?
   a) เพราะกล้องเสีย
   b) เพราะโลหะมีค่า Emissivity ต่ำและสะท้อนความร้อนจากสภาพแวดล้อม
   c) เพราะโลหะไม่แผ่ความร้อนเลย
   d) เพราะคลื่น IR ไม่สามารถทะลุอากาศได้
*(เฉลย: b)*
