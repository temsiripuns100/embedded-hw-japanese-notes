# FPGA & VHDL Part 6: Timing Closure & Constraints

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในระดับ Senior การออกแบบระบบดิจิทัลไม่ได้จบแค่ RTL Simulation ผ่าน แต่ต้องผ่านการทำ **Timing Closure** อย่างสมบูรณ์ 
สิ่งที่ต้องเข้าใจลึกซึ้งคือ:
- **Setup Time (T_su):** เวลาที่ข้อมูลต้องนิ่งก่อนขอบขาขึ้นของคลื่นนาฬิกา การละเมิด (Setup Violation) มักเกิดจาก Critical Path ที่มี Combinational Logic มากเกินไป หรือ Routing Delay ที่ยาว
- **Hold Time (T_h):** เวลาที่ข้อมูลต้องคงที่หลังจากขอบขาขึ้นของคลื่นนาฬิกา
- **SDC (Synopsys Design Constraints):** การเขียนข้อกำหนด เช่น `create_clock`, `set_false_path`, `set_multicycle_path` เพื่อบอก Synthesis Tool ว่าต้อง Optimize อย่างไร

## ทริคหน้างาน OJT (OJT Field Tricks)
- **การแก้ Setup Violation:** ไม่ควรพึ่ง Tool ในการทำ Retiming เพียงอย่างเดียว Senior Engineer จะเข้าไปแก้ RTL โดยตรงด้วยการทำ **Pipelining** (เพิ่ม Register คั่นกลาง Logic ที่ยาว) หรือการจัดรูปสมการ (Logic Restructuring)
- **การแก้ Hold Violation:** ปกติ Tool มักจะแทรก Buffer ให้อัตโนมัติ แต่หากเกิด Hold Violation ข้าม Clock Domain แปลว่าลืมทำ CDC (Clock Domain Crossing)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **タイミング制約 (Timing seiyaku)** - Timing constraint (ข้อกำหนดทางเวลา)
- **セットアップ時間 (Settoappu jikan)** - Setup time
- **クリティカルパス (Kuritikarupasu)** - Critical path (เส้นทางวิกฤต)
- **配線遅延 (Haisen chien)** - Routing delay (ความหน่วงจากสายสัญญาณ)

## ควิซท้ายบท (Quiz)
**Q:** หากรายงาน Synthesis แจ้งเตือนว่ามี Setup Time Violation ที่ Critical Path หนึ่ง เราควรแก้ไขที่ระดับ RTL อย่างไร?
**A:** ทำการ **Pipelining** โดยเพิ่ม Register คั่นกลางระหว่าง Combinational logic เพื่อลดระดับความลึกของ Logic (Logic Depth) และทำให้ Path สั้นลง
