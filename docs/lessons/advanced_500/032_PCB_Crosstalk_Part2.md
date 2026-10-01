# 032: PCB Crosstalk เจาะลึก Part 2 - NEXT (Near-End) vs FEXT (Far-End)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เมื่อสัญญาณเดินทางบน Aggressor การรบกวนจะถูกส่งไปที่ Victim ทั้งด้านต้นทาง (Near-End Crosstalk - NEXT) และปลายทาง (Far-End Crosstalk - FEXT):
- **NEXT:** คือผลรวมของ Inductive และ Capacitive coupling ($I_{NEXT} \propto I_{L_m} + I_{C_m}$) รูปแบบสัญญาณของ NEXT จะเป็นก้อนพัลส์ (Pulse) แบนกว้างเท่ากับ $2 \times T_{delay}$ (เวลาเดินทางไป-กลับของ Coupled length) และ Amplitude จะไม่อิ่มตัวจนกว่าความยาวคัปปลิ้งจะมากกว่าสัดส่วน Rise time ของสัญญาณ
- **FEXT:** คือผลต่างระหว่าง Inductive และ Capacitive coupling ($V_{FEXT} \propto C_m - L_m / Z_0$) รูปแบบสัญญาณ FEXT จะเป็นพัลส์แหลม (Derivative-like spike) ที่เกิดขึ้นพร้อมกับ Edge ของสัญญาณ Aggressor 
- **กรณี Stripline (Homogeneous Medium):** ในทางทฤษฎี $C_m = L_m / Z_0^2$ ส่งผลให้ FEXT = 0! (ยกเว้นมี Asymmetry)
- **กรณี Microstrip (Inhomogeneous Medium):** สนามไฟฟ้าบางส่วนผ่านอากาศ (Er=1) บางส่วนผ่าน FR4 (Er~4.3) ทำให้สัญญาณส่วน Capacitive เดินทางเร็วกว่า Inductive ส่งผลให้ FEXT ไม่เป็นศูนย์ มักเป็นค่าลบ

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **ระวัง FEXT ใน Bus ยาวๆ:** เช่น DDR Memory ที่วิ่งบน Layer นอก (Microstrip) การมี FEXT ลบจะกดระดับ High-level ลง (Eye Diagram ปิดด้านบน) การแก้คือต้องใช้ Stripline Routing แทนสำหรับ Bus ความเร็วสูง
- **NEXT Saturation:** ถ้าลากเส้นตีคู่กันยาวเกินกว่าระยะ Saturation length (ระยะที่สัญญาณวิ่งเท่ากับ Rise time / 2) การเพิ่มระยะขนานจะไม่ทำให้ NEXT สูงขึ้นอีก แต่ FEXT จะสูงขึ้นเรื่อยๆ ตามความยาว!

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **近端クロストーク (Kintan Kurosutōku):** NEXT (Near-End Crosstalk)
- **遠端クロストーク (Entan Kurosutōku):** FEXT (Far-End Crosstalk)
- **伝搬遅延 (Denpan chien):** Propagation Delay
- **波形 (Hakei):** Waveform (รูปคลื่น)
- **飽和 (Hōwa):** Saturation (การอิ่มตัวของ NEXT)

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** เหตุใด Stripline จึงแทบไม่มีปัญหา FEXT เมื่อเทียบกับ Microstrip?
**คำตอบ:** เพราะ Stripline เป็น Homogeneous Medium (ฝังอยู่ใน Dielectric ชนิดเดียวกันทั้งหมด) ทำให้ความเร็วในการเดินทางของสนามไฟฟ้าและแม่เหล็กเท่ากัน ส่งผลให้ผลรวมทางคณิตศาสตร์ของ Capacitive และ Inductive FEXT หักล้างกันเป็นศูนย์ (หรือใกล้เคียงศูนย์)
