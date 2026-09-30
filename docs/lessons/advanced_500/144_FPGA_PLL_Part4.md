# FPGA PLL Deep Dive - Part 4: Dynamic Phase Alignment and SerDes Applications

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
ในการส่งข้อมูลความเร็วสูง (High-Speed IO เช่น DDR, LVDS, SerDes) Data window (Data Eye) จะเล็กมาก (ระดับ picosecond)
การใช้ Static Phase Shift ใน PLL ไม่เพียงพอ เนื่องจาก Temperature และ Voltage Variations สามารถทำให้ Delay เปลี่ยนแปลงได้
**Dynamic Phase Alignment (DPA)** เข้ามาแก้ปัญหานี้ โดยใช้ PLL หลายเฟส (Multi-phase outputs เช่น $0^\circ, 45^\circ, 90^\circ, 135^\circ$) ร่วมกับ Phase Selector logic ตรวจจับขอบของ Data (Data Transition) และเลือก Clock Phase ที่อยู่ตรงกลางของ Data Eye แบบ Real-time
ในสถาปัตยกรรม SerDes, PLL มักจะเป็นประเภท **Ring Oscillator** หรือ **LC Tank** (สำหรับความถี่สูงระดับ GHz) ซึ่งต้องการ Clock/Data Recovery (CDR) วงจรย่อยเพื่อ Extract Clock จากสายสัญญาณที่ถูก Scramble มา

## 2. ทริคหน้างาน OJT (現場のOJTテクニック)
- **Eye Diagram Analysis**: เวลา Debug ปัญหา SerDes, ตา (Eye) ที่ปิดมักเกิดจาก ISI (Intersymbol Interference) จากบอร์ด มากกว่าตัว FPGA ให้ลองปรับ Pre-emphasis (ฝั่งส่ง) หรือ Equalization (ฝั่งรับ) ก่อนไปโทษ PLL
- **Spread Spectrum Clocking (SSC)**: ถ้าระบบใช้ SSC เพื่อลด EMI (เช่น PCIe) PLL ที่ทำหน้าที่ Receiver (CDR) ต้องมีความสามารถในการ Tracking (Loop Bandwidth กว้างพอ) ที่จะตาม Profile ของ SSC ทัน (มักจะเป็น Triangular Modulation $30-33$ kHz)
- **Phase Shift Resolution**: การหมุนเฟสของ PLL มักจะอิงจากคาบของ VCO ($1 / (8 \times F_{vco})$) ถ้าต้องการ Resolution ที่ละเอียดขึ้น ต้องปรับให้ VCO ทำงานที่ความถี่สูงขึ้น

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語)
- **動的位相調整 (どうてきいそうちょうせい, Douteki Isou Chousei)**: Dynamic Phase Alignment (DPA)
- **波形等化 (はけいとうか, Hakei Touka)**: Equalization
- **アイパターン (あいぱたーん, Ai Pataan)**: Eye Diagram / Eye Pattern
- **電磁干渉 (でんじかんしょう, Denji Kanshou)**: EMI (Electromagnetic Interference)
- **分解能 (ぶんかいのう, Bunkainou)**: Resolution

## 4. ควิซท้ายบท (理解度チェック)
**Q4:** หากระบบส่งข้อมูล PCIe มีการใช้ Spread Spectrum Clock (SSC) ที่ฝั่งส่ง ฝั่งรับควรปรับ PLL (CDR) อย่างไรเพื่อให้ตามสัญญาณได้ทัน?
A) ลด Loop Bandwidth ให้แคบที่สุด
B) เพิ่ม Loop Bandwidth ให้เพียงพอกับความถี่ Modulation ของ SSC (เช่น > 33kHz)
C) ปิดการใช้งาน Charge Pump
D) ใช้ LC Tank VCO แทน

*เฉลย:* B) ต้องมี Loop Bandwidth กว้างพอ (十分な帯域幅) เพื่อให้ PLL สามารถ Track ความถี่ที่แกว่งไปมาของ SSC ได้
