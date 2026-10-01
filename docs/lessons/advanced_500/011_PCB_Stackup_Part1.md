# Advanced PCB Stackup Part 1: High-Frequency Material Selection (高周波基板材料の選定)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในงานระดับ High-Speed (เช่น PCIe Gen5+, 112G PAM4) การเลือกใช้วัสดุ FR-4 ทั่วไปไม่เพียงพออีกต่อไป ค่า Dk (Dielectric Constant) และ Df (Dissipation Factor) มีผลโดยตรงต่อ Insertion Loss และ Dispersion วัสดุอย่าง Megtron 6/7 หรือ Tachyon 100G กลายเป็นมาตรฐาน 
วิศวกรระดับ Senior ต้องเข้าใจว่า Dk ไม่ใช่ค่าคงที่ แต่แปรผันตามความถี่ (Frequency-dependent) ส่งผลให้เกิด Phase velocity mismatch ใน Differential pair การเลือกใช้ Copper foil แบบ HVLP (Hyper Very Low Profile) ก็จำเป็นเพื่อลด Skin Effect roughness loss ในย่านความถี่สูง 

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Glass Weave Skew:** ระวังการใช้ผ้าไฟเบอร์กลาส (Glass weave) แบบ 1080 หรือ 106 ในเส้นทางสัญญาณความถี่สูง สัญญาณที่วิ่งบนช่องว่างของเรซินกับเส้นใยแก้วจะเจอ Dk ที่ต่างกัน ทำให้เกิด Skew ในคู่ Differential แนะนำให้ใช้แบบ Spread Glass เช่น 1067 หรือ 1086 หรือการทำ Zig-zag routing (เส้นทแยงมุม)

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **誘電率 (Yūdenritsu):** Dielectric Constant (Dk) - ค่าคงที่ไดอิเล็กทริก
- **誘電正接 (Yūdenshōsetsu):** Dissipation Factor (Df) - ค่าการสูญเสียพลังงาน
- **銅箔粗さ (Dōhaku arasa):** Copper foil roughness - ความขรุขระของฟอยล์ทองแดง
- **ガラスクロス (Garasukurosu):** Glass cloth / Glass weave - ใยแก้วใน PCB

## ควิซท้ายบท (Quiz)
**Q:** การเปลี่ยนจาก RTF (Reverse Treated Foil) เป็น HVLP (Hyper Very Low Profile) ช่วยแก้ปัญหาใดมากที่สุดในสัญญาณ 28 Gbps?
1. ลด Crosstalk
2. ลด Conductor Loss จาก Skin Effect
3. ลด Dielectric Loss
**Ans:** 2. ลด Conductor Loss จาก Skin Effect
