# 3.6 Nios II プロセッサとAvalonバス (สถาปัตยกรรม Nios II และบัส Avalon-MM)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**Nios II** เป็น Soft-Core Processor แบบ 32-bit (RISC) จากฝั่ง Altera (Intel FPGA) ที่เราสามารถจับใส่ลงไปในเนื้อ FPGA ได้ ทำให้ FPGA สามารถรันโค้ด C/C++ เหมือนไมโครคอนโทรลเลอร์ได้
**Avalon-MM (Memory Mapped)** เป็นมาตรฐาน Bus Interface ที่ใช้เชื่อมต่อระหว่าง Nios II (Master) กับ IP Cores อื่นๆ (Slaves) ภายใน FPGA โดยใช้การอ้างอิงผ่าน Address โครงสร้างของบัสจะประกอบด้วยสาย Address, Read/Write Data, และสัญญาณควบคุม (Control signals) อย่าง `waitrequest`

## 💡 ทริคหน้างาน (OJT Tricks)
- **หัวใจของ Avalon คือ `waitrequest`:** มือใหม่ที่เขียน Custom IP มาต่อบัส Avalon มักจะลืมจัดการสัญญาณ `waitrequest` หาก IP ของเรายังทำงานไม่เสร็จ (เช่น กำลังประมวลผลหรืออ่านค่าจากเซ็นเซอร์ช้าๆ) เราต้องดึง `waitrequest` ให้เป็น High เอาไว้ เพื่อหยุด Nios II ไม่ให้ส่งข้อมูลเข้ามาขัดจังหวะ!
- **Platform Designer (Qsys) คือเพื่อนแท้:** อย่าพยายามต่อสายบัส Avalon ด้วยมือ (Instantiate ใน VHDL/Verilog ทีละเส้น) เด็ดขาด ให้ใช้เครื่องมือ Platform Designer ลากเส้นต่อ Master/Slave เข้าด้วยกัน เครื่องมือจะสร้างวงจร Interconnect และจัดการเรื่อง Address Decoding ให้เองทั้งหมด (ลดบั๊กไปได้มหาศาล)

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **ソフトコアプロセッサ (Sofutokoa Purosessa):** Soft-Core Processor
- **バスインターフェース (Basu Intāfēsu):** Bus Interface
- **マスター / スレーブ (Masutā / Surēbu):** Master / Slave
- **読み出し / 書き込み (Yomidashi / Kakikomi):** Read / Write
- **アドレス空間 (Adoresu Kūkan):** Address Space

**ประโยคที่ใช้บ่อย:**
> 「自作のIPコアをNios IIと接続するため、Avalon-MMスレーブインターフェースを実装しました。」
> *(Jisaku no IP koa o Nios II to setsuzoku suru tame, Avalon-MM surēbu intāfēsu o jissō shimashita.)*
> "เพื่อเชื่อมต่อ IP Core ที่เขียนขึ้นเองเข้ากับ Nios II จึงได้ออกแบบสร้าง Interface แบบ Avalon-MM Slave ขึ้นมาครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** ในระบบบัส Avalon-MM หาก Slave (IP Core) อ่านข้อมูลช้ามาก และต้องการให้ Master (Nios II) รอจนกว่าข้อมูลจะพร้อม สัญญาณใดที่ Slave ต้องสร้างขึ้นมาควบคุม Master? (1) `readdatavalid` หรือ (2) `waitrequest`?
