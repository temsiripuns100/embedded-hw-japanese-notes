# บทที่ 19: Thermal Management & Material Selection for Extreme Environments

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
การออกแบบ Stackup สำหรับอุปกรณ์ที่ใช้งานในสภาวะสุดโหด (เช่น Automotive, Aerospace หรือ High-Power LED) จำเป็นต้องคำนึงถึงพารามิเตอร์ด้านความร้อน:
- **Tg (Glass Transition Temperature)**: อุณหภูมิที่วัสดุเริ่มเปลี่ยนสภาพจากของแข็งเป็นยาง (Rubber-like) ควรเลือก High Tg (>= 170°C)
- **Td (Decomposition Temperature)**: อุณหภูมิที่เรซินเริ่มสลายตัว (สูญเสียน้ำหนัก 5%)
- **CTE (Coefficient of Thermal Expansion)**: อัตราการขยายตัวเมื่อได้รับความร้อน โดยเฉพาะแกน Z (Z-axis CTE) มีผลอย่างมากต่อความแข็งแรงของ Plated Through Hole (PTH) การขยายตัวที่มากเกินไปจะทำให้เกิด Barrel Crack (ผนัง Via ขาด)

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick #1**: สำหรับบอร์ด High Power อย่าพึ่งพาแค่ทองแดงหนา (Heavy Copper เช่น 2oz, 3oz) ให้พิจารณาเรื่อง Thermal Vias ใต้จุดกำเนิดความร้อน และจัดให้เชื่อมต่อกับชั้น Ground Plane ด้านในที่มีพื้นที่กว้างขวางเพื่อระบายความร้อน
- **OJT Trick #2**: บอร์ด High Tg มักจะมีความเปราะ (Brittle) กว่าปกติ ดังนั้นการทำ V-Score หรือ Routing ต้องระมัดระวังเรื่อง Micro-crack ที่ขอบบอร์ด

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ガラス転移温度 (Garasu Ten'i Ondo)**: Glass Transition Temperature (Tg)
- **熱膨張係数 (Netsubōchō Keisū)**: Coefficient of Thermal Expansion (CTE)
- **放熱ビア (Hōnetsu Bia)**: Thermal Via
- **耐熱性 (Tainetsusei)**: Heat Resistance
- **剥離 (Hakuri)**: Delamination (การหลุดลอกของชั้น PCB)

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: ค่าพารามิเตอร์ใดของวัสดุ PCB ที่หากมีค่าสูงเกินไป จะทำให้เกิดความเสี่ยง Plated Through Hole (PTH) ร้าวหรือขาดในแนวแกน Z มากที่สุดเมื่อได้รับความร้อนสูง?
1. Glass Transition Temperature (Tg)
2. Decomposition Temperature (Td)
3. Z-axis Coefficient of Thermal Expansion (CTE-Z)
4. Dielectric Constant (Dk)

*เฉลย: 3. Z-axis Coefficient of Thermal Expansion (CTE-Z) เพราะถ้าขยายตัวเยอะในแนวตั้ง จะดึงรั้งผิวชุบทองแดงในรูจนขาด*
