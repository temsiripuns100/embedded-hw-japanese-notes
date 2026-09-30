# PCB DFA Part 7: Thermal Profiling & Reflow Optimization

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การออกแบบ PCB ที่ดีต้องคำนึงถึง Thermal Profiling ภายในเตา Reflow. บอร์ดที่มีการกระจายทองแดง (Copper distribution) ไม่สม่ำเสมอ จะเกิดความแตกต่างของอุณหภูมิ (ΔT) ทั่วทั้งบอร์ด. 
- **Thermal Imbalance:** หากมีโซนที่เป็น Solid Copper Plane ใหญ่ๆ อยู่ติดกับโซนที่มีแค่ Trace เล็กๆ โซนทองแดงเยอะจะดึงความร้อนไปหมด (Heat Sink Effect) ทำให้โซนนั้นอาจเกิด Cold Solder Joint ในขณะที่โซนทองแดงน้อยอาจจะไหม้ (Overheating) หรือเกิด Void ใน BGA
- **Board Warpage:** ความเครียดจากความร้อนไม่เท่ากัน (Thermal Stress) สามารถทำให้บอร์ดโก่งตัว (Warpage / Bow & Twist) ซึ่งร้ายแรงมากสำหรับอุปกรณ์ Fine-pitch

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Copper Thieving/Pouring:** การใส่ Dummy Copper (Thieving) ในพื้นที่ว่าง ไม่ได้มีผลดีแค่เรื่อง Etching (การกัดลายวงจร) แต่ยังช่วย Balance Thermal Mass ตอนอบ Reflow ด้วย
- **Thermocouple placement:** เวลาทำ Thermal Profile ควรฝัง TC อย่างน้อย 3 จุด: จุดที่หนา/ใหญ่ที่สุด (Cold spot), จุดที่เล็กที่สุด (Hot spot), และใต้ BGA (Critical component)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **温度プロファイル (Ondo Purofairu):** Thermal profile / โปรไฟล์อุณหภูมิ
- **基板の反り (Kiban no sori):** Board warpage / บอร์ดโก่ง
- **銅箔残存率 (Douhaku zanzon ritsu):** Copper remaining rate / อัตราส่วนทองแดงที่เหลือ (ช่วยเรื่อง Thermal balance)
- **ボイド (Boido):** Void / ฟองอากาศในจุดบัดกรี
- **吸熱 (Kyuunetsu):** Heat absorption / การดูดซับความร้อน

## ควิซท้ายบท (Quiz)
**Q:** การใส่ Copper Pour (Dummy copper) บนชั้น Layer นอกสุด มีประโยชน์หลักๆ ในแง่ของ DFA อย่างไร?
A) เพิ่มความสวยงาม
B) ป้องกันคลื่นแม่เหล็กไฟฟ้า (EMI) เท่านั้น
C) ลดปัญหาบอร์ดโก่ง (Warpage) และช่วยเกลี่ย Thermal Mass ให้สมดุล
**เฉลย:** C) ช่วย Balance อุณหภูมิและลดความเครียดเชิงกลขณะผ่านความร้อน
