# Lesson 052: PCB Thermal Part 2 - Thermal Vias Design and Placement

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
Thermal Vias ใช้สำหรับนำความร้อนจาก Component Pad ทะลุไปยัง Plane ด้านล่างหรือ Heatsink ทองแดงมีค่าการนำความร้อนสูง (ประมาณ 385 W/mK) ขณะที่ FR4 ต่ำมาก (0.25 W/mK) การเจาะ Thermal Vias หนาแน่นใต้ Thermal Pad (Exposed Pad) จะช่วยได้มาก ขนาด Via นิยมใช้รูเจาะ 0.2-0.3 mm ระยะ Pitch 1.0-1.2 mm และควรพิจารณาความหนาของการชุบทองแดงในรูให้หนาที่สุดเท่าที่ทำได้

## ทริคหน้างาน OJT
ระวังอย่าใส่ Thermal Via รูใหญ่เกินไป (เช่น 0.5 mm) หรือปล่อยทะลุโดยไม่ทำ Tenting / Solder Masking ด้านล่าง เพราะตอนบัดกรี ตะกั่วจะไหลทะลุรูหนีไปด้านล่างหมด (Wicking) ทำให้จุดสัมผัสใต้ชิปเกิด Void สูงกว่า 20%

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図)
- **サーマルビア (Saamaru Bia):** Thermal Via
- **熱伝導率 (Netsudendou Ritsu):** Thermal Conductivity
- **放熱パッド (Hounetsu Paddo):** Thermal Pad

## ควิซท้ายบท
Q: ขนาดรูเจาะของ Thermal via โดยทั่วไปควรเป็นเท่าใดเพื่อป้องกันปัญหาตะกั่วไหลลงรูโดยไม่จงใจ?
A: ประมาณ 0.2-0.3 mm
