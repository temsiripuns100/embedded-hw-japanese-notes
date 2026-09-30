# 3.1 組み合わせ論理と順序論理 (Combinational vs Sequential Logic)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
ในการออกแบบวงจรดิจิทัลและ FPGA เราแบ่งลอจิกออกเป็น 2 ประเภทหลัก:
1. **組み合わせ論理 (Combinational Logic):** วงจรที่ Output ขึ้นอยู่กับ Input "ณ ขณะนั้น" เท่านั้น (เช่น AND, OR, XOR, Multiplexer) ไม่มีหน่วยความจำ ไม่มีสัญญาณนาฬิกา (Clock) เข้ามาเกี่ยวข้อง
2. **順序論理 (Sequential Logic):** วงจรที่มี "หน่วยความจำ" (เช่น D-Flip-Flop) Output จะขึ้นอยู่กับทั้ง Input ณ ขณะนั้น และ "สถานะเดิม" ในอดีต การเปลี่ยนสถานะจะเกิดขึ้นเมื่อมีขอบสัญญาณนาฬิกา (Clock Edge) เท่านั้น

## 💡 ทริคหน้างาน (OJT Tricks)
- **อย่าสร้าง Clock ด้วย Combinational Logic:** มือใหม่มักเอาสัญญาณมาผ่านเกต AND/OR แล้วต่อตรงเข้าขา Clock ของ Flip-Flop สิ่งนี้คือหายนะ! เพราะ Combinational Logic จะสร้างสัญญาณขยะเส้นเล็กๆ (Glitch) ออกมาเสมอ ซึ่งจะทำให้ Flip-Flop ทริกเกอร์มั่ว กฎเหล็กคือ ขา Clock ต้องมาจาก Clock Network (PLL/Oscillator) โดยตรงเท่านั้น!
- **Gated Clock ควรใช้ Clock Enable (CE):** หากต้องการหยุดการทำงานของวงจรบางส่วนเพื่อประหยัดไฟ อย่าเอาเกต AND ไปบล็อค Clock แต่ให้ใช้ขา `Clock Enable (CE)` ของ Flip-Flop แทน

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **組み合わせ論理 (Kumiawase Ronri):** Combinational Logic (วงจรลอจิกเชิงจัดหมู่)
- **順序論理 (Junjo Ronri):** Sequential Logic (วงจรลอจิกเชิงลำดับ)
- **フリップフロップ (Furippu Furoppu):** Flip-Flop
- **グリッチ (Guritchi):** Glitch (สัญญาณรบกวนขยะชั่วขณะ)

**ประโยคที่ใช้บ่อย:**
> 「クロックラインに組み合わせ論理を入れると、グリッチで誤動作する恐れがあります。」
> *(Kurokku rain ni kumiawase ronri o ireru to, guritchi de godōsa suru osore ga arimasu.)*
> "หากนำ Combinational logic ไปแทรกในสายสัญญาณ Clock เกรงว่าจะทำให้เกิดการทำงานผิดพลาดจาก Glitch ได้ครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** เพราะเหตุใดวงจร Combinational Logic (เช่น ประตู AND 2 ขา ที่รับสัญญาณ Input มาจากต่างแหล่งกัน) จึงมักสร้างสัญญาณ Glitch ออกมาที่ Output ในขณะที่ Input เปลี่ยนแปลงสถานะ?
