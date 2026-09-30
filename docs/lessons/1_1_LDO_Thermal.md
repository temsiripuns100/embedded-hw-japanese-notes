# 1.1 リニアレギュレータ（LDO）の原理と熱計算 (หลักการทำงานของ LDO และการคำนวณความร้อน)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**LDO (Low Dropout Regulator)** เป็นวงจรแปลงแรงดันไฟฟ้า (Voltage Regulator) แบบเชิงเส้นที่สามารถรักษาแรงดัน Output ให้คงที่ได้แม้แรงดัน Input จะใกล้เคียงกับ Output มากๆ โดยปกติ LDO จะประกอบด้วย Error Amplifier, Voltage Reference และ Pass Transistor (มักจะเป็น P-ch MOSFET หรือ PNP BJT)

**การสูญเสียพลังงาน (Power Dissipation)**
ข้อเสียหลักของ LDO คือประสิทธิภาพ (Efficiency) ขึ้นอยู่กับส่วนต่างของแรงดัน Input และ Output พลังงานส่วนที่เหลือจะถูกแปลงสภาพเป็นความร้อน (Heat)
สมการคำนวณความร้อน:
> $P_d = (V_{in} - V_{out}) \times I_{out} + (V_{in} \times I_q)$
*เมื่อ $I_q$ คือ Quiescent Current (กระแสที่ IC กินเอง มักมีค่าน้อยมากจนบางครั้งละทิ้งได้)*

**การคำนวณอุณหภูมิ (Thermal Calculation)**
ในการออกแบบจริง เราต้องตรวจสอบว่า Junction Temperature ($T_j$) ของ IC จะไม่เกินค่าสูงสุดที่ทนได้ (มักจะเป็น 125°C หรือ 150°C)
> $T_j = T_a + (P_d \times \theta_{JA})$
*เมื่อ $T_a$ คือ Ambient Temperature (อุณหภูมิแวดล้อม) และ $\theta_{JA}$ คือ Thermal Resistance Junction-to-Ambient (°C/W)*

## 💡 ทริคหน้างาน (OJT Tricks)
- **อย่าไว้ใจ Data Sheet เรื่อง $\theta_{JA}$ เพียงอย่างเดียว:** ค่า $\theta_{JA}$ ในสเปคมักวัดบนบอร์ดมาตรฐาน JEDEC (เช่น 4 layers) ถ้าบอร์ดของคุณมีแค่ 2 layers หรือมีทองแดงน้อยกว่า ค่าความต้านทานความร้อนจะสูงขึ้น ส่งผลให้ IC ร้อนกว่าที่คำนวณได้
- **การใช้ Thermal Via:** ควรใส่ Thermal Via ใต้ Thermal Pad ของ LDO เพื่อกระจายความร้อนลงสู่ชั้น GND ภายใน ช่วยลด $\theta_{JA}$ ได้อย่างมีนัยสำคัญ
- **Dropout Voltage:** ต้องเผื่อ Dropout Voltage ($V_{drop}$) ไว้เสมอ ถ้า $V_{in}$ ตกจนทำให้ $V_{in} - V_{out} < V_{drop}$ LDO จะไม่สามารถคุมแรงดันได้ (Regulation Loss)

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **リニアレギュレータ (Rinia Regyurēta):** Linear Regulator (LDO)
- **ドロップアウト電圧 (Doroppuauto Den'atsu):** Dropout Voltage
- **熱計算 (Netsukeisan):** การคำนวณความร้อน (Thermal calculation)
- **ジャンクション温度 (Jankushon Ondo):** Junction Temperature ($T_j$)
- **放熱 (Hōnetsu):** การระบายความร้อน (Heat dissipation)

**ประโยคที่ใช้บ่อย:**
> 「LDOの熱計算を実施しましたが、ワーストケースでジャンクション温度がスペックを超過する懸念があります。」
> *(LDO no netsukeisan o jisshi shimashita ga, wāsutokēsu de jankushon ondo ga supekku o chōka suru kenen ga arimasu.)*
> "ได้ทำการคำนวณความร้อนของ LDO แล้ว แต่มีความกังวลว่าใน Worst-case อุณหภูมิ Junction จะเกินสเปคครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** หากวงจรใช้ LDO แปลงไฟจาก 5V เป็น 3.3V จ่ายกระแสสูงสุดที่ 500mA และใช้งานในสภาพแวดล้อมที่ $T_a = 60^\circ C$ หาก IC มีค่า $\theta_{JA} = 40^\circ C/W$ อุณหภูมิ Junction ($T_j$) จะเป็นเท่าใด? และหากสเปคระบุ $T_{j(max)} = 125^\circ C$ การออกแบบนี้ปลอดภัยหรือไม่? (กำหนดให้ $I_q = 0$)
