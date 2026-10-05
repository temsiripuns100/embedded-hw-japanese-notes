# Lesson 110: FPGA Security & Bitstream Encryption (FPGAセキュリティと暗号化)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ทรัพย์สินทางปัญญา (IP) ใน FPGA อยู่ในรูปแบบของ Bitstream ซึ่งหากไม่มีการป้องกัน คู่แข่งสามารถโคลนหรือ Reverse Engineer ได้
- **Bitstream Encryption:** การใช้ AES-256 (หรือเทียบเท่า) เข้ารหัส Bitstream ตัว FPGA จะมีกุญแจถอดรหัสเก็บไว้ใน eFUSE หรือ Battery-Backed RAM (BBRAM)
- **Authentication (MAC):** การใช้ HMAC หรือ RSA/ECC เพื่อยืนยันว่า Bitstream ไม่ได้ถูกแก้ไข (Tamper) โดยผู้ไม่ประสงค์ดี
- **Physical Unclonable Functions (PUF):** เทคโนโลยีใหม่ที่ใช้ความแปรปรวนในกระบวนการผลิตซิลิคอนมาสร้างกุญแจดิจิทัลที่ไม่สามารถโคลนได้

## 2. ทริคหน้างาน OJT (OJT Field Tricks)
- **eFUSE vs BBRAM:** หน้างานจริง ถ้าอยู่ในช่วง R&D เราจะใช้ BBRAM เก็บกุญแจ เพราะลบและเขียนใหม่ได้ แต่ถ้า Mass Production ถึงจะเป่า eFUSE ซึ่งเขียนได้ครั้งเดียว (OTP)
- **Readback Attack:** อย่าลืมปิดฟีเจอร์ JTAG Readback เมื่อเข้าสู่โปรดักชัน เพื่อป้องกันไม่ให้คนอื่นเสียบสาย JTAG มาดึงข้อมูลคอนฟิกูเรชันในเครื่อง

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **暗号化 (Angōka):** Encryption
- **復号 (Fukugō):** Decryption
- **知的財産 (Chiteki zaisan):** Intellectual Property (IP)
- **認証 (Ninshō):** Authentication
- **改ざん防止 (Kaizan bōshi):** Tamper resistance / Anti-tamper

## 4. ควิซท้ายบท (Quiz)
**Q1:** ทำไมถึงต้องใช้ Battery-Backed RAM (BBRAM) ในการเก็บ Encryption Key แทนที่จะใช้ Flash ROM ธรรมดา?
**Answer:** เพราะ BBRAM เป็น Volatile memory หากมีความพยายามเจาะระบบทางกายภาพ เราสามารถออกแบบวงจร Anti-tamper ให้ตัดไฟแบตเตอรี่ กุญแจจะหายไปทันที (Zeroization) ทำให้ระบบปลอดภัย
