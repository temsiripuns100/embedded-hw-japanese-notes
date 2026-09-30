# 5.5 推奨回路と未処理ピンの指摘 (การอ้างอิงวงจรแนะนำและการจัดการขา IC ที่ไม่ได้ใช้)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**推奨回路 (Reference Design / Recommended Circuit):** คือวงจรตัวอย่างที่ผู้ผลิต IC ระบุไว้ใน Data Sheet ถือเป็นคัมภีร์ศักดิ์สิทธิ์ที่ผ่านการทดสอบมาแล้วจากโรงงาน หากคุณทำตาม Reference Design อย่างเคร่งครัด โอกาสที่วงจรจะทำงานได้ปกติก็มีสูงกว่า 90%
**未処理ピン (Unused Pins / NC - No Connect):** ขาของ IC ที่ไม่ได้ถูกนำไปใช้งาน ถือเป็นระเบิดเวลาชั้นดีหากจัดการไม่ถูกต้อง!
- ขา Input ของวงจร CMOS: ห้ามปล่อยลอย (Floating) เด็ดขาด เพราะมันจะทำตัวเป็นเสาอากาศรับ Noise และทำให้ Transistor ภายในทำงานสลับไปมาครึ่งๆ กลางๆ กระแสไฟจะทะลุ (Shoot-through current) ทำให้ IC ร้อนและกินไฟมหาศาล ต้องจัดการดึงขึ้น (Pull-up) หรือดึงลง (Pull-down) เสมอ
- ขา Output: มักจะแนะนำให้ปล่อยลอย (Open) ไว้ เพื่อไม่ให้เกิดการดึงกระแส

## 💡 ทริคหน้างาน (OJT Tricks)
- **"ทำไมถึงไม่ทำตาม Reference?":** นี่คือคำถามแรกที่รุ่นพี่จะถามคุณในห้อง Design Review ถ้าวงจรคุณแปลกไปจาก Data Sheet ทริคคือ ถ้าคุณจะออกแบบแหวกแนว คุณต้องมีเหตุผลทางวิศวกรรมที่แน่นพอ (เช่น คำนวณแล้วว่าค่า C ต้องน้อยกว่านี้เพื่อความเร็ว) ถ้าไม่มี... "ลอก Data Sheet ซะ!"
- **ระวังขาลับใน Data Sheet:** ขาที่เขียนว่า NC (No Connect) บางครั้ง Data Sheet ดอกจันตัวเล็กๆ ไว้ว่า *"NC pin must be tied to GND for thermal dissipation"* (ต้องต่อลงกราวด์เพื่อระบายความร้อน) อ่านให้จบทุกบรรทัด!

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **推奨回路 (Suishō Kairo):** Recommended Circuit / Reference Design
- **データシート (Dētashīto):** Data Sheet
- **未処理ピン (Mishori Pin):** Unused Pin (ขาที่ไม่ได้จัดการ/ไม่ได้ใช้งาน)
- **オープン / 浮き (Ōpun / Uki):** Open / Floating (ปล่อยลอยไว้ไม่ต่ออะไร)
- **プルアップ処理 / プルダウン処理 (Puruappu Shori / Purudaun Shori):** Pull-up / Pull-down process

**ประโยคที่ใช้บ่อย:**
> 「メーカーの推奨回路に合わせて、未使用の入力ピンはGNDにプルダウン処理をしておきました。」
> *(Mēkā no suishō kairo ni awasete, mishiyō no nyūryoku pin wa Gurando ni purudaun shori o shite okimashita.)*
> "เพื่อให้สอดคล้องกับวงจรแนะนำของผู้ผลิต ขา Input ที่ไม่ได้ใช้งาน ผมจึงได้ทำการ Pull-down ลงกราวด์ไว้ให้เรียบร้อยแล้วครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** เพราะเหตุใดการปล่อยขา Input ของวงจรตรรกะแบบ CMOS (Complementary Metal-Oxide-Semiconductor) ให้ลอยไว้เฉยๆ (Floating) จึงทำให้ชิป IC ร้อนขึ้นและกินกระแสไฟฟ้ามากกว่าปกติ?
