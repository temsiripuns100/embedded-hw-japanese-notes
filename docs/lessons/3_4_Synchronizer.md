# 3.4 2段同期化回路（2-Stage Synchronizer） (การสร้างวงจรซิงโครไนซ์แบบ 2 สเตจ)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**2-Stage Synchronizer** คืออาวุธมาตรฐานที่ใช้แก้ปัญหา Metastable ในการส่งสัญญาณ 1 บิตข้าม Clock Domain โครงสร้างของมันคือการนำ D-Flip-Flop 2 ตัวมาต่ออนุกรมกัน (Shift Register) และป้อน Clock ของฝั่งรับ (Destination Clock) ให้ทั้ง 2 ตัว
กลไก: หาก FF ตัวแรกรับสัญญาณมาแล้วเกิดอาการ Metastable จะมีเวลาเท่ากับ 1 Clock Cycle ในการฟื้นตัวให้กลับมาเป็น 0 หรือ 1 ปกติ ก่อนที่ FF ตัวที่สองจะสุ่มอ่านค่าไปใช้ ทำให้วงจรถัดๆ ไปได้รับสัญญาณที่เสถียรแน่นอน (แต่ต้องยอมแลกกับความหน่วง / Latency 2 Clock)

## 💡 ทริคหน้างาน (OJT Tricks)
- **ระวัง Routing Delay ทรยศ:** 2-Stage Synchronizer จะทำงานได้เต็มประสิทธิภาพก็ต่อเมื่อ FF1 และ FF2 อยู่ "ใกล้กันที่สุด" ภายในเนื้อ FPGA! หากเส้นทางจาก Q1 ไปยัง D2 ยาวมาก (Routing Delay สูง) เวลาฟื้นตัวของ FF1 จะถูกตัดทอนลง (Resolution Time ลดลง) ทริคคือต้องใส่ Constraint (เช่น `ASYNC_REG = "TRUE"` ใน Xilinx) เพื่อบังคับให้ Tool วาง FF 2 ตัวนี้ติดกันใน Slice เดียวกัน
- **บางครั้ง 2 สเตจก็ไม่พอ:** หาก Clock ฝั่งรับมีความถี่สูงมากกกก (เช่นระดับ GHz) 1 Clock Cycle อาจจะสั้นเกินกว่าที่ FF1 จะฟื้นตัวทัน ในกรณีนี้อาจต้องใช้ 3-Stage หรือ 4-Stage Synchronizer!

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **2段同期化回路 (Nidan Dōkika Kairo):** 2-Stage Synchronizer (วงจรซิงค์ 2 ระดับ)
- **シフトレジスタ (Shifuto Rejisuta):** Shift Register
- **遅延 (Chien):** Delay / Latency (ความหน่วง)
- **配置制約 (Haichi Seiyaku):** Placement Constraint (ข้อบังคับการจัดวาง)
- **タイミング制約 (Taimingu Seiyaku):** Timing Constraint

**ประโยคที่ใช้บ่อย:**
> 「メタステーブル対策として、非同期入力には必ず2段同期化回路を挿入しています。」
> *(Metasutēburu taisaku toshite, hidōki nyūryoku ni wa kanarazu nidan dōkika kairo o sōnyū shite imasu.)*
> "เพื่อเป็นมาตรการรับมือกับ Metastable ในฝั่ง Input ที่เป็น Asynchronous จึงต้องแทรกวงจร 2-Stage Synchronizer เสมอครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** หากเรานำ 2-Stage Synchronizer ไปใช้รับสัญญาณปุ่มกด (Push Button) จากภายนอกที่ไม่มี Clock เข้าสู่ FPGA เราควรใส่ `ASYNC_REG` Constraint ให้กับ Flip-Flop ทั้งคู่หรือไม่? เพราะเหตุใด?
