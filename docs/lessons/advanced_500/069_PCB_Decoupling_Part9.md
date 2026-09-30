# PCB Decoupling Part 9: High-Frequency Decoupling & ESL Reduction

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
สมการของ Loop Inductance: $L_{loop} = L_{cap} + L_{trace} + L_{via} + L_{plane}$
ในย่านความถี่สูง ค่า Inductance เป็นตัวแปรหลักที่บล็อกกระแส Transient ไม่ให้ส่งไปยัง IC ทันเวลา การเลือกใช้ Capacitor แบบ Low-ESL เช่น Reverse Geometry (0402 vs 0204) หรือ X2Y capacitors เป็นเทคนิคขั้นสูงที่ช่วยลด $L_{cap}$
อย่างไรก็ตาม $L_{via}$ และ $L_{plane}$ มักจะมีสัดส่วนสูงที่สุด ดังนั้นการเจาะ Via แบบหลายรูขนานกัน (Multiple vias) และการวางชิ้นส่วนให้ชิด IC pin มากที่สุด จึงเป็นหลักการที่ฝ่าฝืนไม่ได้ในวงจร High-Speed

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Via in Pad:** สำหรับ IC BGA ระดับ High-end วิศวกรจะใช้เทคนิค Via in Pad (VIP) เพื่อต่อ Capacitor ใต้บอร์ด (Bottom layer) ตรงกับขา Power/GND ของ BGA พอดี วิธีนี้จะทำให้ $L_{trace}$ เป็นศูนย์ และลด Loop Inductance ได้มากที่สุด
- **Reverse Geometry C:** ถ้างบถึงและพื้นที่จำกัด การใช้ C แบบ 0306 หรือ 0204 (หน้ากว้างแต่ตัวสั้น) จะช่วยลด ESL ได้มากกว่า 50% เมื่อเทียบกับเบอร์ 0603 หรือ 0402 ทั่วไป

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
1. **Loop Inductance:** ループインダクタンス (Ruupu indakutansu)
2. **Via in Pad:** パッドオンビア / ビアインパッド (Paddo on bia / Bia in paddo)
3. **BGA (Ball Grid Array):** BGAパッケージ (BGA pakkeeji)
4. **Reverse Geometry:** リバース形状 (Ribaasu keijou)
5. **Transient Response:** 過渡応答 (Kato outou)

## ควิซท้ายบท (Quiz)
**คำถาม:** การใช้ Capacitor ขนาด 0204 (Reverse Geometry) แทน 0402 มีข้อดีอย่างไร?
1. ทนแรงดันได้สูงกว่า
2. ความจุมากกว่าในขนาดเท่ากัน
3. ESL ต่ำกว่า ทำให้มีประสิทธิภาพในการ Decoupling ที่ความถี่สูงได้ดีกว่า
4. บัดกรีได้ง่ายกว่าด้วยคลื่นความร้อน (Wave Soldering)

*เฉลย:* ข้อ 3 (ESL ต่ำกว่า เนื่องจากมีระยะทางที่กระแสไหลผ่านตัวเก็บประจุสั้นกว่าและหน้ากว้างกว่า)
