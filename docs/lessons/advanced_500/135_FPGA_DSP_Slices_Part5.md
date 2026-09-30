# Lesson 135: FPGA DSP Slices - Part 5 (Power Optimization & Resource Sharing)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
DSP Slices กินพลังงานแบบ Dynamic สูงเมื่อมีการสวิตช์สถานะ การลด Power คือการป้องกันไม่ให้ข้อมูลเข้า DSP เมื่อไม่จำเป็น (Operand Isolation) นอกจากนี้ หากมีตัวคูณหลายตัวแต่ทำงานใน Time Slot ที่ต่างกัน (เช่น TDM - Time Division Multiplexing) Senior Engineer จะทำการ Resource Sharing ใช้ DSP ตัวเดียวทำงานหลายอย่างที่ความถี่สูงขึ้น เพื่อลดจำนวน DSP ที่ต้องใช้

## ทริคหน้างาน OJT (OJT Tricks)
- **Clock Enable is Your Friend:** ใช้พอร์ต CE (Clock Enable) ของ DSP Registers เสมอเมื่อข้อมูลยังไม่พร้อม (Valid = 0) เพื่อแช่แข็งสถานะภายในและลด Dynamic Power
- **Overclocking for TDM:** รัน DSP ที่คล็อกเร็วกว่า Logic อื่นๆ (เช่น 2x หรือ 4x) เพื่อให้ DSP 1 ตัวสามารถประมวลผลข้อมูลได้หลาย Channel ประหยัดพื้นที่บนชิป

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **消費電力 (Shouhi Denryoku):** Power Consumption (การใช้พลังงาน)
- **資源共有 (Shigen Kyouyuu):** Resource Sharing (การแชร์ทรัพยากร)
- **時分割多重化 (Jibunkatsu Tajuuka):** Time Division Multiplexing / TDM (มัลติเพล็กซ์แบบแบ่งเวลา)
- **クロックゲーティング (Kurokku Geetingu):** Clock Gating (การควบคุมคล็อกเกต)

## ควิซท้ายบท (Quiz)
**Q:** การทำ Time Division Multiplexing (TDM) กับ DSP Slices ส่งผลอย่างไรต่อการออกแบบ?
**A:** ช่วยลดจำนวน DSP Slices ที่ใช้ แต่แลกมาด้วยความซับซ้อนของ Control Logic ที่เพิ่มขึ้นและต้องรัน DSP ที่ความถี่ (Clock) สูงขึ้น
