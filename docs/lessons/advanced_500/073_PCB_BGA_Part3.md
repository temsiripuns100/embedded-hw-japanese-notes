# Lesson 073: BGA Thermal Management & Power Integrity

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
IC ที่ใช้แพ็กเกจ BGA มักจะกินไฟสูงและสร้างความร้อนมาก (เช่น CPU/FPGA)
- **Thermal Vias**: การจัดวาง Thermal Vias จำนวนมากใต้ Die (หรือบน Ground/Power Pads) ช่วยถ่ายเทความร้อนลงสู่แผ่นทองแดงชั้นใน (Inner copper planes) ยิ่งแผ่นทองแดงหนา (เช่น 2oz) ยิ่งกระจายความร้อนได้ดี
- **Power Integrity (PI)**: การจัดวาง Decoupling Capacitors ต้องอยู่ใกล้กับขา Power ของ BGA ให้มากที่สุด (มักจะวางที่ฝั่งตรงข้ามของบอร์ด - Bottom side) เพื่อลด Loop Inductance และป้องกันแรงดันตก (Voltage Drop/Ripple) ที่ความถี่สูง

## ทริคหน้างาน OJT (OJT Field Tricks)
- เมื่อวาง Thermal Vias หากไม่ได้ทำ Via Filling (POFV) อย่าเจาะ Via ลงไปที่ Pad เด็ดขาด (ต้องใช้ Dog-bone) แต่ถ้าเป็น Thermal Pad ขนาดใหญ่ตรงกลาง (QFN/Thermal BGA) สามารถเจาะ Via แล้วปล่อยทิ้งได้ (Tent หรือ Un-tent ตามความเหมาะสม)
- วาง Capacitor ตัวเล็ก (ความจุต่ำ, SRF สูง) ไว้ใกล้ BGA ที่สุด และตัวใหญ่ (Bulk cap) วางถัดออกไป

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **放熱ビア (Hōnetsu bia)** - Thermal Via
- **パスコン (Pasukon)** - Decoupling Capacitor (Bypass Capacitor)
- **電源層 (Dengen sō)** - Power Plane
- **GND層 / グランド層 (Gurando sō)** - Ground Plane
- **電圧降下 (Den'atsu kōka)** - IR Drop / Voltage Drop

## ควิซท้ายบท (Quiz)
**คำถาม:** การวาง Decoupling Capacitor ไว้ใต้ BGA (ฝั่งตรงข้ามของ PCB) มีจุดประสงค์หลักเพื่ออะไร?
<details>
<summary>ดูเฉลย</summary>
**คำตอบ:** เพื่อลด Loop Inductance ให้เหลือน้อยที่สุด ทำให้ Capacitor สามารถจ่ายกระแสชั่วขณะ (Transient current) ให้กับ BGA ได้อย่างรวดเร็ว รักษาเสถียรภาพของแรงดันไฟ (Power Integrity)
</details>
