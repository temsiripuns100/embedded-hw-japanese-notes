# 3.2 クロックドメインクロッシング（CDC）の基礎 (พื้นฐานการข้ามโดเมนของสัญญาณนาฬิกา)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**Clock Domain Crossing (CDC)** คือการส่งสัญญาณข้ามจากวงจรที่ทำงานด้วย Clock หนึ่ง (Source Domain) ไปยังวงจรที่ทำงานด้วยอีก Clock หนึ่ง (Destination Domain) ซึ่งทั้งสอง Clock นี้ไม่ซิงค์กัน (Asynchronous) 
เมื่อ Clock ไม่ซิงค์กัน เราจะไม่สามารถรับประกัน Setup Time และ Hold Time ของ Flip-Flop ฝั่งรับได้ ทำให้มีความเสี่ยงสูงมากที่ฝั่งรับจะอ่านค่าสัญญาณผิดพลาด หรือเกิด Metastability

## 💡 ทริคหน้างาน (OJT Tricks)
- **ห้ามส่ง Combinational Signal ข้ามโดเมน:** กฎเหล็กของ CDC คือสัญญาณที่ถูกส่งข้ามโดเมน จะต้องออกมาจากขา Q ของ Flip-Flop ฝั่งส่งเท่านั้น (Register Output) ห้ามเป็นสัญญาณที่ทะลุออกมาจาก AND/OR Gate เด็ดขาด เพราะ Glitch เล็กๆ ที่ข้ามไปอาจถูกจับโดย Clock ฝั่งรับในจังหวะนรกพอดี
- **Multi-bit ห้ามใช้แค่ Flip-Flop:** การส่งสัญญาณ 1 บิต ข้ามโดเมนสามารถใช้ Synchronizer ได้ แต่ถ้าเป็นบัสข้อมูล (Data Bus) หลายบิต ห้ามใช้ Synchronizer กับทุกบิตพร้อมกันเด็ดขาด! เพราะ Skew จะทำให้แต่ละบิตข้ามโดเมนไม่พร้อมกัน (ได้ข้อมูลขยะ) ต้องใช้ **Asynchronous FIFO** หรือการทำ Handshaking เสมอ

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **非同期 (Hidōki):** Asynchronous (ไม่ซิงโครนัส / ไม่พร้อมกัน)
- **クロックドメイン / クロック乗せ換え (Kurokku Domein / Kurokku Nosekae):** Clock Domain Crossing (การข้ามโดเมนสัญญาณนาฬิกา)
- **同期化 (Dōkika):** Synchronization (การซิงโครไนซ์)
- **セットアップ時間 (Settoappu Jikan):** Setup Time
- **ホールド時間 (Hōrudo Jikan):** Hold Time

**ประโยคที่ใช้บ่อย:**
> 「非同期クロック間のデータ転送には、必ず非同期FIFOかハンドシェイク回路を使用してください。」
> *(Hidōki kurokku-kan no dēta tensō ni wa, kanarazu hidōki faifo ka handosheiku kairo o shiyō shite kudasai.)*
> "สำหรับการส่งข้อมูลระหว่าง Clock ที่เป็น Asynchronous กรุณาใช้ Asynchronous FIFO หรือวงจร Handshake เสมอด้วยครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** การพยายามส่งบัสข้อมูล (Data Bus) ขนาด 8 บิต ข้ามโดเมนสัญญาณนาฬิกา (CDC) โดยใช้วงจร 2-Stage Synchronizer กับสายแต่ละเส้นแยกกัน จะทำให้เกิดความผิดพลาดใดที่ฝั่งรับเมื่อค่าข้อมูลมีการเปลี่ยนจาก `00001111` เป็น `11110000`?
