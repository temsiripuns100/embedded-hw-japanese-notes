# Lesson 054: PCB Thermal Part 4 - Metal Core PCB (MCPCB) and High Power

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
Metal Core PCB (MCPCB) ประกอบด้วยชั้นโลหะฐาน (มักเป็นอลูมิเนียม หรือทองแดง), ชั้น Dielectric ที่มีการนำความร้อนสูง (Thermal Dielectric), และชั้นวงจรทองแดง MCPCB เหนือกว่า FR4 ในแง่การระบายความร้อน (Dielectric มีค่า K = 1-8 W/mK) มักใช้ในงาน High Power LED, Automotive Electronics, และ Power Converter สิ่งที่ต้องระวังคือ Dielectric Breakdown Voltage เพราะฉนวนบางมาก

## ทริคหน้างาน OJT
MCPCB ทำ Vias ข้ามชั้นยากมากและแพง มักออกแบบเป็น 1-Layer เท่านั้น ถ้าต้องเดินข้ามเส้นจริงๆ แนะนำให้ใช้ Jumper (0-ohm resistor) บนบอร์ดช่วยลดต้นทุน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図)
- **アルミ基板 (Arumi Kiban):** Aluminum Substrate Board (MCPCB)
- **絶縁層 (Zetsuen Sou):** Dielectric / Insulation Layer
- **耐電圧 (Taiden'atsu):** Withstand Voltage / Breakdown Voltage

## ควิซท้ายบท
Q: ข้อจำกัดที่สำคัญอย่างหนึ่งของการใช้ MCPCB 1-layer คืออะไร?
A: ไม่สามารถมี Via เพื่อลากวงจรข้ามไปด้านล่างได้ ต้องเดินลายวงจรในระนาบเดียวหรือใช้ Jumper
