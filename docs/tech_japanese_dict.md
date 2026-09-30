# 🇯🇵 現場の技術日本語 (On-the-Job Technical Japanese Dictionary)

รวบรวมคำศัพท์และรูปประโยคที่ใช้ในการทำงานจริง (ประชุม, ตรวจแบบ, เขียนรายงาน)

## 1. หมวดปัญหาและการรายงาน (Troubleshooting & Reporting)
* **不具合解析 (Fuguai Kaiseki):** การวิเคราะห์ปัญหา/ข้อบกพร่อง (Failure Analysis)
* **原因究明 (Gen'in Kyūmei):** การสืบหาสาเหตุที่แท้จริง (Root Cause Investigation)
* **応急対策 (Ōkyū Taisaku):** การแก้ไขเฉพาะหน้า / ชั่วคราว (Temporary Fix / Wire-mod)
* **恒久対策 (Kōkyū Taisaku):** การแก้ไขถาวรในระดับโครงสร้าง (Permanent Countermeasure)
* **再発防止 (Saihatsu Bōshi):** การป้องกันไม่ให้เกิดซ้ำ

## 2. หมวดการตรวจแบบวงจรจ่ายไฟ (Power Supply Design Review)
* **定格電流 (Teikaku Denryū):** พิกัดกระแสสูงสุด (Rated Current)
* **磁気飽和 (Jiki Hōwa):** การอิ่มตัวทางแม่เหล็ก (Magnetic Saturation) - *ใช้เตือนเวลาเลือก Ferrite Bead ผิดเบอร์*
* **発熱 (Hatsunetsu):** การปล่อยความร้อน - *ใช้เตือนเวลาใช้ LDO ลดแรงดันไฟเยอะเกินไป*
* **リップルノイズ (Rippuru Noizu):** คลื่นรบกวนความถี่สูงจาก DCDC
* **検証項目 (Kenshō Kōmoku):** หัวข้อการทดสอบ/ตรวจสอบ (Verification Items)
* **代替品評価 (Daigae-hin Hyōka):** การประเมินชิ้นส่วนทดแทน (Alternative Part Evaluation)
* **突入電流 (Totsunyū Denryū):** กระแสกระชากตอนเปิดเครื่อง (Inrush Current)
* **立ち上がり時間 (Tachiagari Jikan):** เวลาในการไต่ระดับสัญญาณขาขึ้น (Rise Time)
* **オーバーシュート (Ōbāshūto):** แรงดันกระชากทะลุเป้าหมาย (Overshoot)
* **リセット遅延時間 (Risetto Chien Jikan):** เวลาหน่วงการรีเซ็ต (Reset Delay Time)


## 3. หมวดการตรวจลายวงจรความเร็วสูง (High-Speed PCB Design Review)
* **等長配線 (Tōchō Haisen):** การเดินสายให้ยาวเท่ากัน (Length Matching)
* **スキュー (Sukyū):** ความเหลื่อมล้ำทางเวลาของสัญญาณ (Time Skew)
* **差動インピーダンス (Sadō Inpīdansu):** ความต้านทานเชิงซ้อนคู่สายส่วนต่าง (Differential Impedance)
* **ミスマッチ (Misumatchi):** การไม่เข้าคู่กัน / ความยาวไม่เท่ากัน (Mismatch)
* **迂回する (Ukai suru):** การเดินอ้อม (Routing around an obstacle)

## 4. รูปประโยคเด็ดสำหรับ Design Review (検図)
> 「このICは最大3A流れますので、今のフェライトビーズの**定格電流**では**磁気飽和**を起こす恐れがあります。DCRがもっと低い部品に変更しましょう。」
> *(IC ตัวนี้กินกระแสสูงสุด 3A พิกัดกระแสของ Ferrite Bead ตัวนี้อาจทำให้เกิดการอิ่มตัวทางแม่เหล็กได้ เกรงว่าจะกรองคลื่นไม่ได้ครับ ควรเปลี่ยนเป็นเบอร์ที่ DCR ต่ำกว่านี้ครับ)*

> 「USB信号は**差動ペア**なので、配線長に**ミスマッチ**があると**スキュー**が発生し、ノイズの原因になります。**等長配線**（ミアンダ配線）で修正するよう指示します。」
> *(สัญญาณ USB เป็นคู่สายส่วนต่าง หากความยาวสายไม่เท่ากันจะเกิด Time Skew และเป็นสาเหตุของสัญญาณรบกวนครับ จะสั่งให้น้องแก้โดยการทำงูเลื้อยให้ยาวเท่ากันครับ)*

