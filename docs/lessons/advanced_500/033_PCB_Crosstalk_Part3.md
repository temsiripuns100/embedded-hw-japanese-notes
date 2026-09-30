# Lesson 033: PCB Crosstalk - Part 3: NEXT vs FEXT (近端と遠端クロストーク)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Crosstalk แบ่งตามทิศทางการเดินทาง:
- **NEXT (Near-End Crosstalk - 近端クロストーク):** สัญญาณรบกวนเดินทางย้อนกลับไปหาต้นทาง (Driver) ของ Victim net แอมพลิจูดมักจะคงที่แต่กินเวลายาวนาน (2 * T_delay)
- **FEXT (Far-End Crosstalk - 遠端クロストーク):** สัญญาณรบกวนเดินทางไปหาปลายทาง (Receiver) ของ Victim net แอมพลิจูดจะสะสมและแปรผันตรงกับความยาวของ Trace (Coupled length)
ใน Stripline (สายสัญญาณที่ถูกขนาบด้วย Ground ทั้งบนและล่าง) FEXT จะมีค่าเกือบเป็นศูนย์เพราะ Capacitive และ Inductive coupling หักล้างกันสมบูรณ์ แต่ใน Microstrip (สายบนผิว PCB) FEXT มักเป็นปัญหาใหญ่เพราะความเร็วคลื่นในอากาศกับใน FR4 ไม่เท่ากัน

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Stripline for High-Speed:** ถ้าสัญญาณเร็วมากๆ (> 5 Gbps) และกังวลเรื่อง FEXT ให้พยายาม route ให้อยู่ในชั้น Stripline (Inner layers)
- **Spacing > Length:** การลด Coupled length (ระยะที่เดินขนานกัน) ช่วยลด FEXT ได้ แต่ไม่ช่วยลดแอมพลิจูดของ NEXT การเพิ่ม Spacing (เว้นระยะห่าง) เป็นวิธีที่ได้ผลดีที่สุดสำหรับทั้งคู่

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **近端クロストーク (Kintan Kurosutooku):** NEXT (Near-End Crosstalk)
- **遠端クロストーク (Entan Kurosutooku):** FEXT (Far-End Crosstalk)
- **平行配線長 (Heikou Haisenchou):** Parallel routing length / Coupled length
- **ストリップライン (Sutorippu Rain):** Stripline (สายสัญญาณชั้นใน)
- **マイクロストリップ (Maikuro Sutorippu):** Microstrip (สายสัญญาณชั้นนอก)

## ควิซท้ายบท (Quiz)
**Q1:** ทำไม Stripline ถึงลด FEXT ได้ดีกว่า Microstrip?
**A:** เพราะสภาพแวดล้อม Dielectric เป็นเนื้อเดียวกัน (Homogeneous) ทำให้ Capacitive และ Inductive coupling หักล้างกันพอดี
**Q2:** การลด Parallel routing length จะส่งผลอย่างไรต่อ NEXT?
**A:** ไม่ทำให้แอมพลิจูด (Peak voltage) ของ NEXT ลดลง (ตราบใดที่ยาวเกิน Saturation length) แต่จะลดระยะเวลาของ NEXT
