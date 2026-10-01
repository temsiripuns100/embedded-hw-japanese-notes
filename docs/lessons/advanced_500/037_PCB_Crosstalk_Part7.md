# 037: PCB Crosstalk เจาะลึก Part 7 - SerDes (PCIe, USB3) Mitigation

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ใน SerDes interface (Serializer/Deserializer) เช่น PCIe Gen4/5 (16-32 GT/s) หรือ USB 3.2:
- **TX-to-RX Crosstalk (NEXT รุนแรงสุด):** สัญญาณ TX มี Amplitude สูงมาก (~800mV-1V) ขณะที่ RX มีการลดทอนจาก Channel Loss ทำให้เหลือ Amplitude ต่ำมาก (ระดับสิบ mV) หากจัดวาง TX ใกล้ RX, พลังงานจาก TX (NEXT) จะกลบสัญญาณ RX ที่อ่อนแออย่างสิ้นเชิง (Signal-to-Noise Ratio พัง)
- **AC Coupling Capacitor Pad:** บริเวณแผ่น Pad ของ Capacitor 0402/0201 ที่ต่ออนุกรมเพื่อ AC Coupling จะมีความกว้างมากกว่า Trace ปกติ ทำให้ Parasitic Capacitance ($C_p$) ต่อ GND สูง (Impedance drop) และลด Spacing ระหว่างคู่ข้างเคียง เพิ่ม Capacitive Crosstalk

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **TX/RX Grouping:** แบ่งโซนบนบอร์ดชัดเจน! มัดกลุ่ม TX ไว้ด้วยกัน และ มัดกลุ่ม RX ไว้ด้วยกัน ห้ามเอา TX ของเลน 0 ไปเดินขนานกับ RX ของเลน 1 เด็ดขาด
- **AC Cap Voiding:** เพื่อแก้ปัญหา Impedance drop และ Crosstalk ที่บริเวณ AC Coupling Cap ให้ทำการ "เจาะรู" (Void / Cut-out) ที่ Reference plane ชั้นที่ 1 ตรงใต้ Pad ของ Cap พอดี เพื่อให้ Reference plane ลึกลงไปที่ชั้น 2 หรือ 3 เป็นการชดเชย Capacitance ที่เกินมา และทำให้ Field lines ไม่ไปกวนด้านข้าง

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **送受信干渉 (Sōjushin kanshō):** TX/RX Interference
- **ACカップリング (AC kappuringu):** AC Coupling
- **ボイド (Boido):** Void / Cut-out (การเจาะรูที่ Plane)
- **損失 (Sonshitsu):** Loss (Attenuation)
- **配置配線 (Haichi haisen):** Placement and Routing

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** เพราะเหตุใดในระบบ SerDes ความเร็วสูง จึงต้องเข้มงวดในการแยกสาย TX ออกจาก RX อย่างเด็ดขาด?
**คำตอบ:** เพราะสัญญาณฝั่ง TX เป็นสัญญาณต้นทางที่มีพลังงานสูงมาก (High Amplitude) ในขณะที่สัญญาณฝั่ง RX เดินทางผ่านสายยาวจนถูกลดทอนและมีพลังงานต่ำมาก (Low Amplitude) หากเดินสายใกล้กัน NEXT จาก TX จะกลบสัญญาณ RX (ทำลาย SNR จนรับข้อมูลไม่ได้)
