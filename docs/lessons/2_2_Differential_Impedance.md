# 2.2 差動インピーダンス（Differential Impedance）の制御 (การควบคุมอิมพีแดนซ์คู่สายส่วนต่าง เช่น 90Ω / 100Ω)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**差動インピーダンス (Differential Impedance)** คือค่าความต้านทานเชิงซ้อนที่คู่สายสัญญาณ Differential มองเห็น เช่น USB ต้องใช้ 90Ω, PCIe หรือ Ethernet ต้องใช้ 100Ω ค่านี้ขึ้นอยู่กับพารามิเตอร์ 4 อย่าง:
1. Trace Width ($W$ - ความกว้างลายทองแดง)
2. Trace Spacing ($S$ - ระยะห่างระหว่างสาย P และ N)
3. Copper Thickness ($T$ - ความหนาทองแดง)
4. Dielectric Thickness/Constant ($H, \epsilon_r$ - ความหนาและชนิดของฉนวน FR4)

หากค่าอิมพีแดนซ์ผิดเพี้ยน จะทำให้เกิดการสะท้อนกลับของคลื่น (Reflection) และทำให้คุณภาพสัญญาณแย่ลง (Eye Diagram แคบลง)

## 💡 ทริคหน้างาน (OJT Tricks)
- **คุยกับโรงงานเสมอ (Impedance Control Request):** ค่าที่คำนวณจากโปรแกรมวาดวงจร (เช่น Altium/KiCad) เป็นเพียงค่าทางทฤษฎี (Nominal) โรงงานทำบอร์ดแต่ละที่มีสเปคกาว (Prepreg) และ FR4 ที่ต่างกัน ทริคคือต้องส่ง Stack-up ไปให้โรงงานผลิตคำนวณและปรับเส้น $W$ และ $S$ ให้ได้ 90Ω/100Ω พอดีตามกระบวนการผลิตของเขา
- **Tight vs Loose Coupling:** ถ้าให้สาย P และ N อยู่ใกล้กันมาก (Tight Coupling) จะช่วยให้ลบล้าง Noise ภายนอกได้ดีมาก แต่จะทำให้อิมพีแดนซ์ไวต่อความผิดพลาดตอนกัดลายปริ้นท์ การเว้นระยะออกมานิดหน่อย (Loose Coupling) มักจะปลอดภัยกว่าในแง่ของการผลิต

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **差動インピーダンス (Sadō Inpīdansu):** Differential Impedance
- **層構成 (Sōkōsei):** Layer Stack-up (โครงสร้างชั้นทองแดง)
- **線幅 (Senhaba):** Trace Width (ความกว้างลายปริ้นท์)
- **間隔 (Kankaku):** Spacing / Clearance (ระยะห่าง)
- **指定 (Shitei):** Specify / Designation (การกำหนด/การระบุ)

**ประโยคที่ใช้บ่อย:**
> 「基板メーカーに層構成を提出し、USBの差動インピーダンスが90Ωになるよう調整を依頼しました。」
> *(Kiban mēkā ni sōkōsei o teishutsu shi, USB no sadō inpīdansu ga kyūjū-ōmu ni naru yō chōsei o irai shimashita.)*
> "ได้ส่ง Layer Stack-up ให้ทางผู้ผลิตบอร์ดแล้ว และร้องขอให้ช่วยปรับให้ Differential Impedance ของ USB ได้ 90 โอห์มพอดีครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** หากคุณวาดคู่สาย Differential บน PCB เสร็จแล้ว แต่คำนวณพบว่า Differential Impedance มีค่าสูงเกินไป (เช่น ได้ 115Ω แทนที่จะเป็น 100Ω) คุณจะสามารถปรับพารามิเตอร์ 2 อย่างใดในโปรแกรม CAD เพื่อให้ค่าอิมพีแดนซ์ลดลงมาที่ 100Ω?
