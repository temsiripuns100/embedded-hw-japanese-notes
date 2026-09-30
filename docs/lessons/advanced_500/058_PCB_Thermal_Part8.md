# บทที่ 58: การวิเคราะห์และปรับแต่ง Airflow (Convection Cooling) ในระดับบอร์ด

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
การระบายความร้อนด้วยการพาความร้อน (Convection) แบ่งเป็น Natural Convection (ธรรมชาติ) และ Forced Convection (ใช้พัดลม)
สมการของ Newton's Law of Cooling: $q = h \cdot A \cdot (T_s - T_{\infty})$
- **h**: Heat transfer coefficient (ขึ้นอยู่กับความเร็วลม ทิศทาง และลักษณะของไหล)
สำหรับระบบ Forced Air, การวางตำแหน่งชิ้นส่วน (Component Placement) มีผลอย่างมากต่อ Aerodynamics
ถ้ามีชิ้นส่วนตัวใหญ่บังทิศทางลม จะเกิด "Shadow Effect" ทำให้ชิ้นส่วนด้านหลังได้รับลมน้อยและเกิดการสะสมความร้อน (Hotspot)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Component Staggering**: แทนที่จะวางชิ้นส่วนที่แผ่ความร้อนไว้ในแนวเส้นตรง (Inline) ตามทิศทางลม ให้วางแบบฟันปลา (Staggered) เพื่อให้ลมสัมผัสกับ Heatsink ของทุกตัวได้ทั่วถึง
- **Baffle & Shroud**: ถ้าลมจากพัดลมกระจายออกไปโดยไม่ผ่าน Heatsink ให้สร้างกำแพงกั้นลม (Baffle) ในกล่อง (Enclosure) หรือบน PCB เพื่อบังคับทิศทางลมให้วิ่งเข้าหาเป้าหมาย

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **気流 (Kiryuu)**: Airflow
- **風抜け (Kazenuke)**: Ventilation / Air passage (การระบายอากาศ)
- **温度分布 (Ondobunpu)**: Temperature distribution (การกระจายตัวของอุณหภูมิ)
- **熱だまり (Netsudamari)**: Heat accumulation / Hotspot

## ควิซท้ายบท (End of Chapter Quiz)
**Q: Shadow Effect ในการออกแบบ Airflow คืออะไร?**
1. การที่ชิ้นส่วนขนาดใหญ่บังลม ทำให้ชิ้นส่วนด้านหลังร้อนขึ้น
2. การที่แสงสว่างเข้าไม่ถึงชิ้นส่วนบน PCB
3. ผลกระทบของคลื่นแม่เหล็กไฟฟ้าต่ออุณหภูมิ
4. ปรากฏการณ์ที่ลมพัดแรงเกินไปจนทำให้อุปกรณ์สั่น

*เฉลย: 1. การที่ชิ้นส่วนขนาดใหญ่บังลม ทำให้ชิ้นส่วนด้านหลังร้อนขึ้น*
