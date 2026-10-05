# Lesson 130: FPGA State Machine Part 10 - Timing Closure & Retiming (タイミングクロージャとリタイミング)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เมื่อระบบ FSM มีความซับซ้อนมาก และเจอปัญหา Timing Violation (Negative Slack) การทำ Timing Closure เป็นความท้าทายระดับ Senior เทคนิค **Retiming** หรือ **Register Balancing** จะช่วยย้าย Flip-Flops ข้าม Combinational Logic เพื่อกระจาย Delay ให้สม่ำเสมอในทุกๆ Path หากการออกแบบ FSM ซับซ้อนจน Next-State Logic มี Delay มากเกิน การแบ่ง FSM ออกเป็นหลายส่วน (FSM Decomposition) หรือการใส่ Pipeline Stage แทรกการคำนวณ เป็นแนวทางที่หลีกเลี่ยงไม่ได้

## ทริคหน้างาน OJT (OJT Field Tricks)
- เมื่อเจอ Negative Slack ใน State Machine ให้เปิด Schematic Viewer เพื่อดู Logic Path เสมอ อย่าพึ่งแค่ Report
- ถ้า State ใดมีการเช็คเงื่อนไขยาวเหยียดระดับ `if (A & B & C & ...)` ให้ดึงเงื่อนไขเหล่านั้นไปคำนวณล่วงหน้า (Pre-calculate) แล้วเก็บใส่ Register ก่อนเอาเข้ามาใช้เป็นเงื่อนไขในการเปลี่ยน State (Input Registering) จะช่วยลด Critical Path ได้มหาศาล
- บางครั้งปัญหาไม่ใช่โค้ดเรา แต่เป็นค่า Fan-out ที่เยอะไป ให้ทำ Register Replication (หรือตั้งค่า Max Fanout ใน Tool)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **タイミング違反 (Taimingu Ihan)** - Timing Violation (การผิดพลาดด้านไทม์มิ่ง)
- **パイプライン化 (Paipurain-ka)** - Pipelining (การทำไพพ์ไลน์)
- **経路遅延 (Keiro Chien)** - Path Delay (ความหน่วงของเส้นทาง)
- **リタイミング (Ritaimingu)** - Retiming (การจัดตารางเวลาใหม่/กระจายเรจิสเตอร์)

## ควิซท้ายบท (Quiz)
**คำถาม:** การทำ "Input Registering" หรือพรีแคลคูเลชั่นสำหรับเงื่อนไข State Transition ช่วยแก้ปัญหา Timing ได้อย่างไร?
1. ช่วยลดจำนวน State ของ FSM
2. ลด Logic Depth ของ Combinational Logic ภายใน Cycle ของ FSM นั้น ทำให้ลด Delay ลง
3. เพิ่มความเร็วของ Clock Frequency (Fmax) ของทั้งชิปโดยตรง
4. ช่วยแก้ปัญหา Metastability

**เฉลย:** 2. ลด Logic Depth ของ Combinational Logic ภายใน Cycle ของ FSM นั้น ทำให้ลด Delay ลง
