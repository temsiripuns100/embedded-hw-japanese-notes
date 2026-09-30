# 2.4 反射（Reflection）とダンピング抵抗 (การสะท้อนกลับของคลื่นและการใช้ Damping Resistor)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**反射 (Reflection)** เมื่อสัญญาณไฟฟ้าเดินทางไปตามลายปริ้นท์ที่มี Characteristic Impedance ($Z_0$) สมมติว่า $50\Omega$ แล้วเจอจุดที่อิมพีแดนซ์เปลี่ยนไป (Impedance Mismatch) พลังงานส่วนหนึ่งจะสะท้อนกลับมาหาต้นทาง คล้ายคลื่นน้ำที่ชนขอบสระ คลื่นสะท้อนนี้จะไปรวมกับคลื่นลูกใหม่ ทำให้เกิดการกระเพื่อม (Ringing) และ Overshoot/Undershoot

**ダンピング抵抗 (Damping Resistor / Series Termination)** คือการต่อตัวต้านทานอนุกรมที่ฝั่งขาออก (Source/Driver) เพื่อดูดซับคลื่นที่สะท้อนกลับมาและปรับอิมพีแดนซ์ต้นทางให้เท่ากับสาย
> $R_{out} (\text{ของ IC}) + R_{damp} = Z_0 (\text{ของสาย PCB})$

## 💡 ทริคหน้างาน (OJT Tricks)
- **ใกล้ฝั่งส่ง (TX) ให้มากที่สุด:** ตำแหน่งของ Damping Resistor ต้องวางให้ชิดขา Output ของ IC ฝั่งส่งให้มากที่สุด! ถ้าย้ายไปวางไกล ลายปริ้นท์ก่อนถึงตัวต้านทานจะกลายเป็น "Stub" หรือเสาอากาศที่สร้างคลื่นสะท้อนซะเอง
- **ค่ามาตรฐานที่ต้องลอง:** ขา I/O ของ IC ส่วนใหญ่มี $R_{out}$ ภายในประมาณ $15\Omega - 25\Omega$ ดังนั้นถ้า PCB ออกแบบมา $50\Omega$ ค่า Damping Resistor ที่วิศวกรนิยมหยิบมาแปะตอนเทสต์บอร์ดคือ $22\Omega, 33\Omega$ หรือ $47\Omega$ 

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **反射 (Hansha):** Reflection (การสะท้อน)
- **ダンピング抵抗 (Danpingu Teikō):** Damping Resistor (ตัวต้านทานลดการสั่น)
- **特性インピーダンス (Tokusei Inpīdansu):** Characteristic Impedance
- **インピーダンス不整合 (Inpīdansu Fuseigō):** Impedance Mismatch
- **送信端 (Sōshintan):** Source end / TX end

**ประโยคที่ใช้บ่อย:**
> 「波形のオーバーシュートを抑えるために、送信端の直近に33Ωのダンピング抵抗を追加してください。」
> *(Hakei no ōbāshūto o osaeru tame ni, sōshintan no chokkin ni sanjūsan-ōmu no danpingu teikō o tsuika shite kudasai.)*
> "เพื่อระงับการเกิด Overshoot ของรูปคลื่น กรุณาเพิ่ม Damping Resistor ขนาด $33\Omega$ ลงไปให้ชิดกับฝั่งส่งที่สุดด้วยครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** ในวงจร Single-ended ที่มี Characteristic Impedance บน PCB เท่ากับ $50\Omega$ หากตรวจสอบ Data Sheet แล้วพบว่าขาส่งสัญญาณของ IC มี Output Impedance ภายใน ($R_{out}$) เท่ากับ $10\Omega$ คุณควรเลือกใช้ Damping Resistor ค่าประมาณเท่าใดเพื่อป้องกันการสะท้อน (Reflection)?
