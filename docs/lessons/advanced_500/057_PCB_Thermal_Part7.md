# บทที่ 57: การเลือกใช้ TIM (Thermal Interface Materials) และ Heatsink (ระบบระดับลึก)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
Thermal Interface Materials (TIM) เป็นตัวกลางสำคัญที่ช่วยลด Contact Thermal Resistance ระหว่างผิวของ IC และ Heatsink
โดยปกติผิววัสดุในระดับไมโครสโคปจะมีความขรุขระ (Surface Roughness) ทำให้เกิดช่องอากาศ (Air gaps) ซึ่งอากาศเป็นฉนวนความร้อนที่แย่มาก (k ~ 0.026 W/m·K)
TIM ที่มีค่า k สูง (เช่น 3-10 W/m·K) จะเข้าไปอุดช่องว่างเหล่านี้
สิ่งสำคัญที่ Senior ต้องประเมินคือ **Bond Line Thickness (BLT)** - ยิ่งบางยิ่งดี แต่ถ้าบางไปแล้วชิ้นส่วนถูกกดทับ (Mounting pressure) ไม่สม่ำเสมอ อาจเกิดการแตกร้าว (Die cracking) ได้

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Pump-out Effect**: ในผลิตภัณฑ์ที่มีการเปลี่ยนแปลงอุณหภูมิบ่อยๆ (Thermal Cycling) การใช้ Thermal Paste อาจทำให้เกิดปรากฏการณ์ Pump-out คือซิลิโคนโดนรีดออกด้านข้างหมดตามกาลเวลา ในกรณีแบบนี้ให้ใช้ **Phase Change Material (PCM)** หรือ Thermal Pad แทน
- **Compression Rate**: เวลาเลือก Thermal Pad ต้องดู % การบีบอัด (Compression) ที่สเปกผู้ผลิตแนะนำ (ปกติราวๆ 20-30%) หากบีบมากเกินไป Pad จะสูญเสียความยืดหยุ่น ยิ่งบอร์ดมีการโก่งตัว (Warpage) จะทำให้ตัว Pad ขาดหรือหลุด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **熱伝導シート (Netsudendou Shiito)**: Thermal Pad / TIM sheet
- **ヒートシンク (Hiitoshinku)**: Heatsink
- **密着性 (Mitchakusei)**: Adhesion / Contact quality (การแนบสนิท)
- **ポンプアウト現象 (Ponpu-auto Genshou)**: Pump-out effect

## ควิซท้ายบท (End of Chapter Quiz)
**Q: หากอุปกรณ์ต้องเจอกับวัฏจักรอุณหภูมิที่รุนแรง (-40°C ถึง 105°C) เป็นเวลาหลายปี วัสดุ TIM แบบใดที่ควรหลีกเลี่ยง?**
1. Thermal Pad (Silicone based)
2. Phase Change Material (PCM)
3. Thermal Grease (Silicone paste)
4. Graphite Sheet

*เฉลย: 3. Thermal Grease เพราะจะเกิดปัญหา Pump-out effect ได้ง่ายที่สุดเมื่ออุณหภูมิเหวี่ยงไปมา*
