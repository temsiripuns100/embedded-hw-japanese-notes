# FPGA State Machine - Part 4: Pipelining State Machines for Timing Closure

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior Engineer การออกแบบ FSM จะไม่ใช้ก้อน Logic ใหญ่ๆ ก้อนเดียวเมื่อต้องทำงานที่ความถี่สูงลิบลิ่ว (เช่น 300MHz+) แต่จะใช้เทคนิค **Pipelining**
- เป็นการซอย Combinational Logic ที่ใช้คำนวณ Next State หรือ Output ออกเป็นส่วนย่อยๆ แล้วแทรก Flip-Flop เข้าไปตรงกลาง
- แม้ว่าจะทำให้เกิด Latency เพิ่มขึ้น (ทำงานเสร็จช้าลงเป็นจำนวน Clock Cycle) แต่ Throughput จะสูงขึ้นมาก และแก้ปัญหา Timing Violation (Negative Slack) ได้ชะงัด
- การจัดการ Pipeline Stall และ Flush เป็นสิ่งที่ขาดไม่ได้ เมื่อ FSM ทำงานผิดพลาด หรือต้องรอข้อมูล (Data dependency)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Senior Trick**: เวลาแยก Pipeline stage ใน FSM ที่ซับซ้อน ให้ใช้ `valid` signal ควบคู่กับ data เสมอ (เหมือน AXI Stream `tvalid` / `tready`) ถ้าระบบปลายทางบอกว่าไม่ว่าง (`ready=0`) FSM ต้นทางต้องสามารถหยุด Pipeline (Stall) ได้โดยไม่ทำข้อมูลหาย
- ระวังปัญหา "Pipeline Bubble" เมื่อ Stall บ่อยเกินไป ทำให้ Throughput โดยรวมตกลง ควรเช็คว่าคอขวด (Bottleneck) อยู่ที่ Stage ไหน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- パイプライン処理 (Paipurain Shori) - Pipelining Processing
- スループット (Suruuputto) - Throughput
- 遅延 (Chien) - Latency / Delay
- 処理待ち (Shorimachi) - Wait / Stall
- 妥当性 (Datousei) - Validity (เช่น valid signal)

## ควิซท้ายบท (Quiz)
**Q1**: การทำ Pipelining ให้กับ FSM Logic มีผลอย่างไรต่อระบบ?
1) ลด Latency และลด Throughput
2) เพิ่ม Latency แต่เพิ่ม Fmax และ Throughput
3) ไม่กระทบ Latency แต่ลด Power Consumption
4) ทำให้ FSM เปลี่ยน State ได้เร็วขึ้นภายใน 1 Clock
**เฉลย**: 2) การแทรก Register จะเพิ่ม Latency เสมอ (ใช้ Clock มากขึ้นในการทำงานจบ) แต่ช่วยลด Delay ต่อ Cycle ทำให้เร่ง Clock ได้เร็วขึ้น (Fmax เพิ่ม)
