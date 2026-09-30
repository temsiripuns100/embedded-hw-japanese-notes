# 4.2 代替品評価（Alternative Part Evaluation） (การประเมินและทดสอบชิ้นส่วนทดแทน)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**代替品評価 (Alternative Part / Second Source Evaluation)** เป็นงานที่วิศวกรหลีกเลี่ยงไม่ได้ เมื่ออุปกรณ์เดิมที่ใช้บนบอร์ดเกิดเหตุการณ์ "เลิกผลิต (EOL - End of Life)", "ของขาดตลาด", หรือ "ต้องการลดต้นทุน (Cost Down)"
การประเมินต้องทำใน 3 มิติ:
1. **電気的特性 (Electrical Specs):** แรงดัน, กระแส, ความถี่, ความต้านทานภายใน ฯลฯ ตรงกันหรือไม่?
2. **物理的特性 (Mechanical/Physical Specs):** ขนาดแพ็กเกจ (Footprint), Pin-out (Pin-to-pin compatible) เสียบแทนกันได้เลยหรือไม่?
3. **熱特性 (Thermal Specs):** ความสามารถในการระบายความร้อน ($\theta_{JA}$) เท่าเดิมหรือแย่ลง?

## 💡 ทริคหน้างาน (OJT Tricks)
- **ระวังกับดัก "Pin-to-Pin Compatible":** ผู้ผลิตมักโฆษณาว่า "เสียบแทนค่ายคู่แข่งได้เลย!" (Drop-in replacement) แต่ความจริงอาจมี "ขาที่เคยเป็น NC (No Connect)" ในไอซีตัวเก่า ถูกนำไปใช้เป็นขาฟังก์ชันลับในไอซีตัวใหม่ หากลายปริ้นท์เก่าเราเอาขานั้นไปต่อลง GND บอร์ดอาจจะช็อตพังได้ทันที! ทริคคือต้องกาง Data Sheet เทียบกันแบบขาต่อขา (Pin-by-pin)
- **อย่าลืมเรื่องซอฟต์แวร์:** การเปลี่ยนชิป I2C/SPI (เช่น EEPROM หรือ Sensor) ถึงแม้สเปคไฟฟ้าจะเหมือนกันเป๊ะ แต่อาจจะมี "Device ID" ในรีจิสเตอร์ที่ต่างกัน ทำให้ซอฟต์แวร์เดิมบูตไม่ขึ้น ต้องแจ้งทีม SW เสมอ!

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **代替品 (Daitaihin):** Alternative Part (ชิ้นส่วนทดแทน)
- **セカンドソース (Sekando Sōsu):** Second Source (ผู้ผลิตรายที่สอง)
- **生産中止 (Seisan Chūshi) / ディスコン (Disukon):** EOL / Discontinued (เลิกผลิต)
- **ピン互換 (Pin Gokan):** Pin-to-pin Compatible (พินตรงกันเสียบแทนได้เลย)
- **コストダウン (Kosuto Daun):** Cost Down (การลดต้นทุน)

**ประโยคที่ใช้บ่อย:**
> 「既存のLDOがディスコンになったため、ピン互換のある代替品の評価を実施します。」
> *(Kizon no LDO ga disukon ni natta tame, pin gokan no aru daitaihin no hyōka o jisshi shimasu.)*
> "เนื่องจาก LDO ตัวเดิมถูกประกาศเลิกผลิต (Discon) จึงจะดำเนินการประเมินชิ้นส่วนทดแทนที่มี Pin-to-pin compatible ครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** คุณกำลังหา Alternative part มาแทน MOSFET ตัวเก่าที่ขาดตลาด MOSFET ตัวใหม่มีสเปค $V_{DS}$, $I_D$, และ $R_{DS(on)}$ เท่ากันเป๊ะแถมราคาถูกกว่า แต่ค่า Total Gate Charge ($Q_g$) สูงกว่าตัวเก่าถึง 3 เท่า หากนำไปใส่ในวงจร Switching ความถี่สูง จะส่งผลเสียอย่างไร?
