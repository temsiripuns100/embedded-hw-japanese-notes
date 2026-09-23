# 📘 Oracle Master Bronze DBA — สรุปเนื้อหาฉบับสมบูรณ์

> **หนังสือ**: ORACLE MASTER Bronze DBA 教科書 (Textbook)
> **สอบ**: 1Z0-085-JPN — Bronze DBA Oracle Database Fundamentals
> **เวอร์ชัน**: Oracle Database 12c R1 – 19c (ข้อสอบรวมทุกเวอร์ชัน)
> **จำนวนข้อสอบ**: 70 ข้อ ใน 2 ชั่วโมง (เลือกตอบ)

---

## 📖 สารบัญ

- [[#บทที่ 1 — ภาพรวมการจัดการ Oracle Database]]
- [[#บทที่ 2 — การติดตั้ง Oracle Software และสร้าง Database]]
- [[#บทที่ 3 — EM Express และเครื่องมือ SQL]]
- [[#บทที่ 4 — การกำหนดค่า Oracle Network]]
- [[#บทที่ 5 — การจัดการ Oracle Instance]]
- [[#บทที่ 6 — โครงสร้างพื้นที่จัดเก็บข้อมูล (Storage)]]
- [[#บทที่ 7 — การจัดการ User และ Security]]
- [[#บทที่ 8 — การจัดการ Schema Objects]]
- [[#บทที่ 9 — การ Monitor และ Advisor]]
- [[#บทที่ 10 — Backup Recovery และ High Availability]]

---

## บทที่ 1 — ภาพรวมการจัดการ Oracle Database

### 1-1 พื้นฐาน Database

- **Database** = ข้อมูลที่จัดระเบียบเพื่อจุดประสงค์เฉพาะ
- **DBMS** (Database Management System) = ซอฟต์แวร์จัดการ DB → Oracle คือหนึ่งใน DBMS
- **RDBMS** = DBMS สำหรับ Relational Database โดยเฉพาะ

#### คุณสมบัติที่ DBMS ต้องมี
| คุณสมบัติ | รายละเอียด |
|---|---|
| **จัดการข้อมูลขนาดใหญ่** | รองรับปริมาณข้อมูลมหาศาล |
| **แชร์ข้อมูล** | ผู้ใช้หลายคนเข้าถึงพร้อมกัน |
| **ประสิทธิภาพสูง** | อ่าน/เขียนข้อมูลเร็ว |
| **ความพร้อมใช้งาน** | กู้คืนจากความเสียหายได้รวดเร็ว |
| **ความปลอดภัย** | ควบคุมสิทธิ์การเข้าถึง |

#### โครงสร้าง Relational Database

```mermaid
graph TD
    A["📊 Relational Database"] --> B["📋 Table (表)"]
    B --> C["📝 Column (列/カラム)<br>กำหนดชื่อ + Data Type"]
    B --> D["📄 Row (行/レコード)<br>= 1 รายการข้อมูล"]
    C --> E["Data Types<br>NUMBER, VARCHAR2, DATE ..."]
```

### 1-2 พื้นฐาน SQL

SQL คือภาษามาตรฐานสำหรับจัดการ Relational Database (มาตรฐาน ANSI/ISO)

#### การแบ่งประเภท SQL Commands

```mermaid
graph LR
    SQL["🗃️ SQL Commands"] --> Q["SELECT<br>ค้นหาข้อมูล"]
    SQL --> DML["DML<br>INSERT / UPDATE / DELETE"]
    SQL --> DDL["DDL<br>CREATE / ALTER / DROP / TRUNCATE"]
    SQL --> TC["Transaction Control<br>COMMIT / ROLLBACK"]
    SQL --> DCL["DCL<br>GRANT / REVOKE"]
    
    style Q fill:#4CAF50,color:white
    style DML fill:#2196F3,color:white
    style DDL fill:#FF9800,color:white
    style TC fill:#9C27B0,color:white
    style DCL fill:#F44336,color:white
```

> [!important] ความแตกต่างของคำสั่งลบ
> - `DELETE` (DML) → ลบ **แถว** ตามเงื่อนไข (ROLLBACK ได้)
> - `TRUNCATE` (DDL) → ลบ **ทุกแถว** แต่ตารางยังอยู่ (ROLLBACK ไม่ได้)
> - `DROP` (DDL) → ลบ **ตารางทั้งหมด** รวมโครงสร้าง (ROLLBACK ไม่ได้)

> [!warning] Implicit COMMIT (暗黙のコミット)
> เมื่อรัน DDL หรือ DCL ระหว่าง Transaction → Transaction ที่ค้างอยู่จะถูก **COMMIT อัตโนมัติ** ก่อน

### 1-3 ภาพรวม Oracle Database

Oracle ทำงานแบบ **Client / Server Architecture**

```mermaid
sequenceDiagram
    participant C as 🖥️ Client<br>(SQL*Plus etc.)
    participant L as 🔗 Listener Process<br>(Server)
    participant S as ⚙️ Server Process<br>(Server)
    participant DB as 🗄️ Oracle DB<br>(Instance + Files)
    
    C->>L: ① ส่งคำขอเชื่อมต่อ
    L->>S: ② สร้าง Server Process
    S->>C: ③ เชื่อมต่อสำเร็จ
    C->>S: ④ ส่ง SQL
    S->>DB: ⑤ ประมวลผล SQL
    DB->>S: ⑥ ผลลัพธ์
    S->>C: ⑦ ส่งผลลัพธ์กลับ
```

### 1-4 โครงสร้างภายใน Oracle Database

```mermaid
graph TB
    subgraph Oracle["🏛️ Oracle Database"]
        subgraph Instance["⚡ Instance"]
            SGA["💾 SGA<br>(System Global Area)"]
            BGP["🔄 Background Processes<br>(DBWn, LGWR, CKPT, PMON, SMON...)"]
        end
        subgraph DBFiles["📁 Database Files"]
            DF["📊 Data Files<br>ข้อมูลจริง (ตาราง, Index)"]
            RF["📝 REDO Log Files<br>บันทึกการเปลี่ยนแปลง"]
            CF["📋 Control Files<br>ข้อมูลโครงสร้าง DB"]
        end
    end
    SGA --- BGP
    Instance --> DBFiles
```

> [!tip] กระบวนการหลัก (Processes)
> - **User Process** (Client) → ส่ง SQL ไปยัง Server
> - **Listener Process** (Server) → รับคำขอเชื่อมต่อ → สร้าง Server Process
> - **Server Process** (Server) → รัน SQL → ส่งผลลัพธ์กลับ Client

---

## บทที่ 2 — การติดตั้ง Oracle Software และสร้าง Database

### 2-1 ขั้นตอนการติดตั้ง

```mermaid
graph LR
    A["1️⃣ ตรวจสอบ<br>前提条件"] --> B["2️⃣ ตั้งค่า OS<br>User/Group/Env"]
    B --> C["3️⃣ ติดตั้ง Software<br>ผ่าน OUI"]
    C --> D["4️⃣ สร้าง Database<br>ผ่าน DBCA"]
```

#### OS User & Groups ที่ต้องสร้าง
| ชื่อ | ประเภท | บทบาท |
|---|---|---|
| `oracle` | OS User | เจ้าของ Oracle Software |
| `oinstall` | OS Group | กลุ่ม Inventory (บันทึก product ที่ติดตั้ง) |
| `dba` | OS Group | กลุ่ม OSDBA (สิทธิ์ SYSDBA) |

#### Environment Variables (Linux/UNIX)
| ตัวแปร | คำอธิบาย |
|---|---|
| `ORACLE_BASE` | Top-level directory (เช่น `/u01/app/oracle`) |
| `ORACLE_HOME` | ที่ติดตั้ง Software เฉพาะรุ่น |
| `ORACLE_SID` | System Identifier (= Database Name ในกรณีปกติ) |

> [!important] ความสัมพันธ์ ORACLE_HOME กับ Database
> - 1 `ORACLE_HOME` = Software **1 เวอร์ชัน** เท่านั้น
> - 1 Server มี **หลาย** `ORACLE_HOME` ได้ (คนละเวอร์ชัน)
> - 1 `ORACLE_HOME` สร้าง **หลาย** Database ได้

### 2-2 สร้าง Database ด้วย DBCA

**DBCA** (Database Configuration Assistant) → เครื่องมือ GUI สำหรับ:
- สร้าง / ลบ Database
- เปลี่ยนค่า Config
- จัดการ Template

#### Template มี 2 ประเภท

```mermaid
graph TD
    T["📋 Database Templates"] --> S["🟢 Seed Template<br>รวม Data File ไว้แล้ว<br>สร้างเร็ว / ปรับแต่งน้อย"]
    T --> N["🔵 Non-Seed Template<br>มีแต่โครงสร้าง<br>สร้างช้าแต่ปรับแต่งได้มาก"]
```

> [!warning] DBCA ≠ DBUA
> - **DBCA** = สร้าง/ลบ Database
> - **DBUA** (Database Upgrade Assistant) = อัปเกรด Database เป็นเวอร์ชันใหม่

---

## บทที่ 3 — EM Express และเครื่องมือ SQL

### 3-1 Enterprise Manager Database Express (EM Express)

- Web-based GUI สำหรับจัดการ **DB เดียว** (ไม่ต้องติดตั้งเพิ่ม)
- URL: `https://<hostname>:5500/em`
- ตั้งค่า Port: `EXEC DBMS_XDB_CONFIG.SETHTTPSPORT(5500);`

#### สิ่งที่ทำได้ vs ทำไม่ได้

| ✅ ทำได้ | ❌ ทำไม่ได้ |
|---|---|
| แก้ไข初期化パラメータ | **เปิด/ปิด Database** |
| จัดการ Tablespace | **Backup / Recovery** |
| จัดการ User & Role | **สร้าง/แก้ไข Table** |
| ดู ADDM, AWR, SQL Tuning | **จัดการ DB หลายตัว** |

#### เปรียบเทียบ EM Express vs Cloud Control

```mermaid
graph LR
    subgraph EE["EM Express"]
        E1["จัดการ DB 1 ตัว"]
        E2["มากับ Oracle ฟรี"]
        E3["ไม่ต้อง Agent"]
        E4["❌ เปิด/ปิด DB ไม่ได้"]
    end
    subgraph CC["Cloud Control"]
        C1["จัดการ DB หลายตัว"]
        C2["ต้องติดตั้งแยก"]
        C3["ต้องมี Management Agent"]
        C4["✅ เปิด/ปิด DB ได้"]
    end
```

### 3-2 SQL*Plus

- เครื่องมือ Command-line มาตรฐาน
- รันได้: **SQL**, **PL/SQL**, **SQL*Plus Commands**

#### วิธีเชื่อมต่อ
| คำสั่ง | คำอธิบาย |
|---|---|
| `sqlplus` | ใส่ username/password แบบ interactive |
| `sqlplus user/pass` | เชื่อมต่อทันที |
| `sqlplus /nolog` | เปิด SQL*Plus โดยไม่เชื่อมต่อ → ใช้ `CONNECT` ภายหลัง |
| `sqlplus / as sysdba` | เชื่อมต่อแบบ OS Authentication (ต้อง login เป็น `oracle` user) |

> [!important] SYS User ต้องใช้ `AS SYSDBA` เสมอ

---

## บทที่ 4 — การกำหนดค่า Oracle Network

### 4-1 Oracle Net

Oracle Net = Component ที่จัดการเชื่อมต่อระหว่าง Client กับ DB Server ผ่าน Network

```mermaid
graph LR
    subgraph Client["🖥️ Client"]
        UP["User Process"]
        TN["tnsnames.ora"]
    end
    subgraph Server["🖧 DB Server"]
        LI["Listener<br>(listener.ora)"]
        SP["Server Process"]
        DB["Oracle DB"]
    end
    UP -->|"ส่ง Connection Request"| LI
    LI -->|"สร้าง Server Process"| SP
    SP -->|"ประมวลผล SQL"| DB
    UP -.->|"ใช้ tnsnames.ora"| TN
```

### 4-2 Listener

- **Listener** = Process บน Server ที่รอรับคำขอเชื่อมต่อจาก Client
- แยกจาก Instance → ต้อง start แยก
- 1 Listener ให้บริการหลาย DB ได้

#### ไฟล์ Config: `listener.ora`
- ที่อยู่: `$ORACLE_HOME/network/admin/listener.ora`
- Default: ชื่อ `LISTENER`, Port `1521`, Protocol `TCP/IP`
- ถ้าใช้ค่า Default → ไม่จำเป็นต้องมี `listener.ora`

#### คำสั่ง `lsnrctl`
| คำสั่ง | ผลลัพธ์ |
|---|---|
| `lsnrctl start` | เปิด Listener |
| `lsnrctl stop` | ปิด Listener (session ที่เชื่อมต่ออยู่ยังไม่หลุด) |
| `lsnrctl status` | ดูสถานะ Listener |
| `lsnrctl services` | ดู Service ที่ Listener รู้จัก |

### 4-3 วิธีเชื่อมต่อจาก Client

#### Local vs Remote Connection
| ประเภท | ต้องการ | ตัวอย่าง |
|---|---|---|
| **Local** | `ORACLE_SID` | `sqlplus user/pass` |
| **Remote** | 接続識別子 (Connection Identifier) | `sqlplus user/pass@identifier` |

#### Naming Methods (วิธีระบุปลายทาง)

```mermaid
graph TD
    NM["🔗 Naming Methods"] --> EC["1️⃣ Easy Connect<br>user/pass@host:port/service<br>ไม่ต้องมี config file"]
    NM --> LN["2️⃣ Local Naming<br>user/pass@net_service_name<br>ใช้ tnsnames.ora"]
    NM --> DN["3️⃣ Directory Naming<br>ใช้ LDAP Server"]
    NM --> EN["4️⃣ External Naming<br>ใช้ External Service"]
```

---

## บทที่ 5 — การจัดการ Oracle Instance

### 5-1 ส่วนประกอบของ Instance

```mermaid
graph TB
    subgraph Instance["⚡ Instance"]
        subgraph SGA["💾 SGA (System Global Area) — แชร์ระหว่าง Process"]
            DBC["🗃️ Database Buffer Cache<br>Cache ข้อมูลจาก Data File"]
            RLB["📝 REDO Log Buffer<br>บันทึกการเปลี่ยนแปลง"]
            SP["📚 Shared Pool"]
            LP["📦 Large Pool<br>RMAN, Parallel Query"]
        end
        subgraph BGP["🔄 Background Processes"]
            DBWn["DBWn<br>เขียน Dirty Block → Data File"]
            LGWR["LGWR<br>เขียน REDO → REDO Log File"]
            CKPT["CKPT<br>อัปเดต Checkpoint"]
            PMON["PMON<br>ทำความสะอาด Process ที่ตาย"]
            SMON["SMON<br>Instance Recovery"]
            ARCn["ARCn<br>Archive REDO Log"]
        end
    end
    subgraph PGA_area["💼 PGA (Process-specific)"]
        PGA["PGA<br>หน่วยความจำส่วนตัว<br>ของแต่ละ Process<br>(Sort, Session Info)"]
    end
```

#### Shared Pool ประกอบด้วย

```mermaid
graph LR
    SP["📚 Shared Pool"] --> LC["Library Cache<br>เก็บ Parsed SQL / Execution Plan"]
    SP --> DDC["Data Dictionary Cache<br>เก็บ Table/Column/Permission Info"]
```

### 5-2 การเปิด/ปิด Instance

#### Startup Phases

```mermaid
graph LR
    A["🔴 SHUTDOWN"] -->|"อ่าน SPFILE/PFILE<br>สร้าง SGA<br>เปิด BG Processes"| B["🟡 NOMOUNT"]
    B -->|"เปิด Control Files"| C["🟠 MOUNT"]
    C -->|"เปิด Data Files<br>+ REDO Log Files"| D["🟢 OPEN"]
    
    style A fill:#f44336,color:white
    style B fill:#ff9800,color:white
    style C fill:#ff5722,color:white
    style D fill:#4CAF50,color:white
```

> [!important] สิทธิ์การเชื่อมต่อ
> - **NOMOUNT / MOUNT** → เฉพาะ SYSDBA / SYSOPER
> - **OPEN** → ผู้ใช้ทั่วไปเชื่อมต่อได้

#### Shutdown Modes

| Mode | รอ Session หลุด | รอ Transaction จบ | Rollback อัตโนมัติ | สถานะ File |
|---|---|---|---|---|
| `NORMAL` | ✅ | ✅ | ❌ | สอดคล้อง |
| `TRANSACTIONAL` | ❌ | ✅ | ❌ | สอดคล้อง |
| `IMMEDIATE` ⭐ | ❌ | ❌ | ✅ | สอดคล้อง |
| `ABORT` | ❌ | ❌ | ❌ | **ไม่สอดคล้อง** (ต้อง Instance Recovery) |

### 5-2-2 Initialization Parameters

#### SPFILE vs PFILE
| รายการ | SPFILE (Server Parameter File) | PFILE (Text Parameter File) |
|---|---|---|
| รูปแบบ | Binary | Text |
| แก้ไข | `ALTER SYSTEM SET` | Text Editor |
| ลำดับความสำคัญ | **สูงกว่า** (ใช้ก่อน) | ใช้เมื่อไม่มี SPFILE |

#### Dynamic vs Static Parameters
| ประเภท | แก้ไขขณะ DB เปิด | วิธีแก้ |
|---|---|---|
| **Dynamic** | ✅ | `ALTER SYSTEM SET param=value` |
| **Static** | ❌ | `ALTER SYSTEM SET param=value SCOPE=SPFILE` → Restart |

### 5-3 การจัดการ Memory

```mermaid
graph TD
    AMM["🧠 Automatic Memory Management (AMM)<br>MEMORY_TARGET = SGA + PGA รวม"] --> ASMM["💾 Auto Shared Memory Management (ASMM)<br>SGA_TARGET = จัดการ SGA อัตโนมัติ"]
    AMM --> APGA["💼 Auto PGA Management<br>PGA_AGGREGATE_TARGET"]
    ASMM --> Manual["🔧 Manual<br>SGA_TARGET = 0<br>กำหนดแต่ละ component เอง"]
```

---

## บทที่ 6 — โครงสร้างพื้นที่จัดเก็บข้อมูล (Storage)

### 6-1 Database Files

```mermaid
graph TB
    subgraph files["📁 Database Files"]
        DF["📊 Data Files<br>เก็บข้อมูลจริง (ตาราง, Index)"]
        REDO["📝 REDO Log Files<br>บันทึกทุกการเปลี่ยนแปลง<br>ใช้ Recovery"]
        CF["📋 Control Files<br>โครงสร้าง DB<br>(ชื่อ file, timestamp ฯลฯ)<br>⚠️ ต้อง多重化!"]
    end
```

#### REDO Log File — โครงสร้าง Group / Member

```mermaid
graph LR
    subgraph G1["Group 1 (Current)"]
        M1A["Member 1a<br>/disk1/redo01a.log"]
        M1B["Member 1b<br>/disk2/redo01b.log"]
    end
    subgraph G2["Group 2"]
        M2A["Member 2a<br>/disk1/redo02a.log"]
        M2B["Member 2b<br>/disk2/redo02b.log"]
    end
    G1 -->|"Log Switch<br>(เมื่อเต็ม)"| G2
    G2 -->|"วนกลับ"| G1
```

> [!important] REDO Log
> - ต้องมีอย่างน้อย **2 Groups**
> - 多重化 (Multiplexing) = มีหลาย Member ต่อ Group (แนะนำเพื่อป้องกัน)
> - ขนาดไม่ auto-extend

### 6-2 Tablespace & Storage Hierarchy

```mermaid
graph TD
    DB["🗄️ Database"] --> TS1["📦 Tablespace 1"]
    DB --> TS2["📦 Tablespace 2"]
    TS1 --> SEG["🧱 Segment<br>(= 1 Table หรือ 1 Index)"]
    SEG --> EXT["📐 Extent<br>ชุดของ Block ที่ต่อเนื่อง<br>(ใน Data File เดียว)"]
    EXT --> BLK["🔲 Data Block<br>หน่วย I/O เล็กสุด<br>(2KB–32KB)"]
```

#### Tablespace ที่สำคัญ
| Tablespace | บทบาท | หมายเหตุ |
|---|---|---|
| **SYSTEM** | เก็บ Data Dictionary | ขาดไม่ได้ / เปลี่ยนชื่อไม่ได้ |
| **SYSAUX** | ช่วย SYSTEM (AWR ฯลฯ) | ขาดไม่ได้ / เปลี่ยนชื่อไม่ได้ |

### 6-3 การสร้าง/ขยาย/ลบ Tablespace

```sql
-- สร้าง
CREATE TABLESPACE ts1 DATAFILE '/path/file.dbf' SIZE 100M;

-- ขยาย (3 วิธี)
ALTER DATABASE DATAFILE '/path/file.dbf' RESIZE 200M;         -- Resize
ALTER TABLESPACE ts1 ADD DATAFILE '/path/file2.dbf' SIZE 100M; -- เพิ่ม File
-- เปิด AUTOEXTEND ON

-- ลบ
DROP TABLESPACE ts1 INCLUDING CONTENTS AND DATAFILES;
```

#### Smallfile vs Bigfile Tablespace
| รายการ | Smallfile (ปกติ) | Bigfile |
|---|---|---|
| จำนวน Data File | หลายไฟล์ได้ | **1 ไฟล์เท่านั้น** |
| เพิ่ม Data File | ✅ ได้ | ❌ ไม่ได้ |
| ขนาดสูงสุด | ตาม OS | สูงสุด 32 TB (8KB block) |

### 6-4 UNDO Tablespace & Temporary Tablespace

```mermaid
graph LR
    subgraph UNDO["🔄 UNDO Tablespace"]
        U1["Rollback ข้อมูล"]
        U2["読取り一貫性<br>(Read Consistency)"]
        U3["Flashback"]
    end
    subgraph TEMP["⏳ Temporary Tablespace"]
        T1["Sort (ORDER BY)"]
        T2["Hash Join"]
        T3["ใช้เมื่อ PGA ไม่พอ"]
    end
```

> [!warning] ORA-01555: Snapshot Too Old
> เกิดเมื่อ UNDO Data ถูก overwrite ก่อนที่ Query จะเสร็จ
> แก้ไข: เพิ่ม `UNDO_RETENTION` / ขยาย UNDO Tablespace

---

## บทที่ 7 — การจัดการ User และ Security

### 7-1 การสร้าง/แก้ไข/ลบ User

```sql
CREATE USER app_user
  IDENTIFIED BY password123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA 100M ON users
  PROFILE default
  PASSWORD EXPIRE       -- บังคับเปลี่ยน Password ตอน Login ครั้งแรก
  ACCOUNT UNLOCK;
```

> [!important] Quota
> ถ้าไม่กำหนด **QUOTA** บน Tablespace ใด → User จะสร้าง Object ใน Tablespace นั้นไม่ได้

#### Account Lock vs Password Expire
| สถานะ | ผลกระทบ |
|---|---|
| **Password Expire** | Login ได้ด้วย Password เก่า → แต่ต้องเปลี่ยน Password ใหม่ |
| **Account Lock** | Login **ไม่ได้เลย** → ต้อง UNLOCK ก่อน |

#### การลบ User
- User ที่กำลัง Connect → **ลบไม่ได้**
- User ที่มี Object → ต้องใช้ `DROP USER username CASCADE` (ลบ Object ทั้งหมด)

### 7-2 สิทธิ์ (Privileges) และ Role

```mermaid
graph TD
    P["🔑 Privileges"] --> SYS["System Privileges<br>CREATE SESSION, CREATE TABLE ...<br>เกี่ยวกับ DB ทั้งระบบ"]
    P --> OBJ["Object Privileges<br>SELECT, INSERT, UPDATE ...<br>เกี่ยวกับ Object เฉพาะ"]
    
    R["🎭 Role"] --> R1["กลุ่มของ Privileges<br>ช่วยจัดการง่ายขึ้น"]
    R --> R2["Predefined Roles:<br>CONNECT / RESOURCE / DBA"]
    
    SYS -.->|"WITH ADMIN OPTION<br>→ มอบต่อได้"| SYS
    OBJ -.->|"WITH GRANT OPTION<br>→ มอบต่อได้"| OBJ
```

#### Predefined Roles
| Role | สิทธิ์ |
|---|---|
| `CONNECT` | สิทธิ์พื้นฐานสำหรับเชื่อมต่อ |
| `RESOURCE` | สร้าง Object พื้นฐาน |
| `DBA` | System Privileges ทั้งหมด (แต่ เปิด/ปิด DB ไม่ได้) |

### 7-2-3 SYSDBA / SYSOPER

| สิทธิ์ | สามารถทำ | จุดเด่น |
|---|---|---|
| **SYSDBA** | สร้าง/ลบ DB, เปิด/ปิด, Incomplete Recovery, เข้าถึงข้อมูลทุก User | สิทธิ์สูงสุด |
| **SYSOPER** | เปิด/ปิด, Complete Recovery, MOUNT/OPEN | **เข้าถึงข้อมูล User ไม่ได้** |

> [!tip] การ Connect แบบ SYSDBA
> - OS Authentication: `sqlplus / as sysdba` (login เป็น `oracle` user บน OS)
> - Password File Authentication: `sqlplus sys/pass as sysdba`

---

## บทที่ 8 — การจัดการ Schema Objects

### 8-1 Schema คืออะไร

- **Schema** = พื้นที่เก็บ Object ของ User (ชื่อเดียวกับ Username)
- สร้าง User → สร้าง Schema อัตโนมัติ
- Object คนละ Schema → ชื่อซ้ำได้ → อ้างอิงด้วย `schema.object`

```mermaid
graph TD
    subgraph SO["Schema Objects<br>(สังกัด User)"]
        TBL["📋 Table"]
        IDX["🔍 Index"]
        VW["👁️ View"]
        SEQ["🔢 Sequence"]
        PROC["⚙️ Procedure"]
    end
    subgraph NSO["Non-Schema Objects<br>(สังกัด DB)"]
        USR["👤 User"]
        RLE["🎭 Role"]
        TBS["📦 Tablespace"]
        PRF["📊 Profile"]
    end
```

### 8-2 Data Types หลัก

| Data Type | คำอธิบาย |
|---|---|
| `NUMBER(n,m)` | ตัวเลข (n=ทั้งหมด, m=ทศนิยม) |
| `CHAR(n)` | ข้อความคงที่ (เติมช่องว่าง) |
| `VARCHAR2(n)` | ข้อความแปรผัน |
| `DATE` | วันที่+เวลา |
| `TIMESTAMP` | วันที่+เวลา+เศษวินาที |
| `CLOB` | ข้อความขนาดใหญ่ |
| `BLOB` | ข้อมูล Binary (รูป, เสียง) |

### 8-2-2 Constraints (ข้อจำกัด)

```mermaid
graph LR
    C["🔒 Constraints"] --> NN["NOT NULL<br>ห้ามเป็นค่าว่าง"]
    C --> UQ["UNIQUE<br>ห้ามซ้ำ (NULL ได้)"]
    C --> PK["PRIMARY KEY<br>UNIQUE + NOT NULL<br>1 ตารางมีได้ 1"]
    C --> FK["FOREIGN KEY<br>อ้างอิง PK/UNIQUE ตารางอื่น"]
    C --> CK["CHECK<br>เงื่อนไขกำหนดเอง"]
```

### 8-3 Recycle Bin & Flashback Drop

```mermaid
graph LR
    A["DROP TABLE t1"] -->|"RECYCLEBIN = ON"| B["🗑️ ย้ายไป Recycle Bin<br>(ไม่ลบจริง)"]
    B -->|"FLASHBACK TABLE t1<br>TO BEFORE DROP"| C["✅ กู้คืนสำเร็จ"]
    A -->|"PURGE"| D["❌ ลบถาวร"]
```

### 8-4 Index & View

#### Index (B-tree)
```mermaid
graph TD
    ROOT["🔝 Root Block"] --> B1["Branch Block"]
    ROOT --> B2["Branch Block"]
    B1 --> L1["🍃 Leaf Block<br>ค่า + ROWID"]
    B1 --> L2["🍃 Leaf Block<br>ค่า + ROWID"]
    B2 --> L3["🍃 Leaf Block<br>ค่า + ROWID"]
    B2 --> L4["🍃 Leaf Block<br>ค่า + ROWID"]
```

> [!warning] สร้าง Index มากเกินไป → DML (INSERT/UPDATE/DELETE) **ช้าลง** เพราะต้องอัปเดต Index ด้วย

#### View = Virtual Table
- นิยามด้วย `SELECT` statement → ไม่เก็บข้อมูลจริง
- ประโยชน์: ซ่อนความซับซ้อนของ SQL + ควบคุมสิทธิ์การเข้าถึง

### 8-5 เครื่องมือย้ายข้อมูล

| เครื่องมือ | จุดประสงค์ | ทิศทาง |
|---|---|---|
| **SQL*Loader** | โหลด CSV/Text ภายนอก → Table | นอก → ใน |
| **Data Pump** (`expdp`/`impdp`) | Export/Import ข้อมูลระหว่าง DB | DB ↔ DB |

---

## บทที่ 9 — การ Monitor และ Advisor

### 9-1 การ Monitor ด้วย EM Express

- **Database Home Page** → ดูสถานะ, Workload, SQL Monitoring
- **Performance Hub** → ดู Performance แบบ Real-time + ย้อนหลัง (ASH)

### 9-2 AWR & ADDM

```mermaid
graph LR
    MMON["🔄 MMON Process"] -->|"ทุก 60 นาที"| AWR["📊 AWR Snapshot<br>(เก็บใน SYSAUX)<br>เก็บไว้ 8 วัน"]
    AWR -->|"ทุกครั้งที่สร้าง Snapshot"| ADDM["🧠 ADDM<br>วิเคราะห์อัตโนมัติ<br>ให้คำแนะนำ"]
```

| Component | คำอธิบาย |
|---|---|
| **AWR** (Automatic Workload Repository) | เก็บสถิติ Performance อัตโนมัติ |
| **ADDM** (Automatic Database Diagnostic Monitor) | วิเคราะห์ Bottleneck จาก AWR → แนะนำวิธีแก้ |

### 9-3 Advisors

```mermaid
graph TD
    ADV["🛠️ Advisors"] --> STA["SQL Tuning Advisor<br>วิเคราะห์ SQL ตัวเดียว<br>(Top Activity, STS)"]
    ADV --> SAA["SQL Access Advisor<br>วิเคราะห์ Workload ทั้งหมด<br>แนะนำ Index/MView/Partition"]
    STA --> REC["คำแนะนำ:<br>• เก็บ Statistics<br>• สร้าง Index<br>• เขียน SQL ใหม่<br>• SQL Profile"]
```

---

## บทที่ 10 — Backup Recovery และ High Availability

### 10-1 พื้นฐาน Backup & Recovery

#### ARCHIVELOG vs NOARCHIVELOG Mode

```mermaid
graph TD
    subgraph NOARCH["🔴 NOARCHIVELOG Mode"]
        N1["REDO Log ถูก overwrite"]
        N2["❌ Recovery ถึงจุดล่าสุดไม่ได้"]
        N3["❌ Online Backup ไม่ได้"]
    end
    subgraph ARCH["🟢 ARCHIVELOG Mode"]
        A1["ARCn บันทึก REDO → Archive Log"]
        A2["✅ Recovery ถึงจุดล่าสุดได้"]
        A3["✅ Online Backup ได้"]
    end
```

> [!important] เปลี่ยน Mode
> ต้องอยู่ใน **MOUNT** state → `ALTER DATABASE ARCHIVELOG;`

#### ประเภท Backup

| ประเภท | ชื่อเรียก | เงื่อนไข | ต้อง Recovery ไหม |
|---|---|---|---|
| **Consistent** (一貫性) | Offline / Cold | DB ต้องปิดปกติ | ❌ Restore แล้วเปิดได้เลย |
| **Inconsistent** (非一貫性) | Online / Hot | DB เปิดอยู่ (ต้อง ARCHIVELOG) | ✅ ต้อง Recovery หลัง Restore |

### 10-1-4 Restore vs Recovery

```mermaid
graph LR
    BK["💾 Backup"] -->|"Restore<br>คืน File จาก Backup"| RS["📂 Restored Files<br>(ข้อมูล ณ ตอน Backup)"]
    RS -->|"Recovery<br>Apply REDO/Archive Logs"| RC["✅ Recovered DB<br>(ข้อมูลล่าสุด)"]
```

| ประเภท Recovery | คำอธิบาย |
|---|---|
| **Complete Recovery** | กู้คืนจนถึงจุดล่าสุดก่อนเกิดปัญหา |
| **Incomplete (Point-in-Time)** | กู้คืนถึงจุดที่กำหนด → ต้อง `OPEN RESETLOGS` |

#### RMAN (Recovery Manager)
```
RMAN> BACKUP DATABASE;    -- Backup ทั้ง DB
RMAN> RESTORE DATABASE;   -- คืน File
RMAN> RECOVER DATABASE;   -- Apply REDO Logs
```

### 10-1-7 ประเภทความเสียหายและการแก้ไข

```mermaid
graph TD
    F["⚠️ ประเภทความเสียหาย"] --> UF["👤 User Process Failure<br>(Session หลุด)"]
    F --> IF["⚡ Instance Failure<br>(DB Crash)"]
    F --> MF["💥 Media Failure<br>(Disk เสีย)"]
    
    UF -->|"PMON ทำ Rollback<br>อัตโนมัติ"| U_OK["✅ อัตโนมัติ"]
    IF -->|"SMON ทำ Instance Recovery<br>ตอน OPEN ครั้งถัดไป"| I_OK["✅ อัตโนมัติ"]
    MF -->|"DBA ใช้ RMAN<br>Restore + Recovery"| M_OK["⚠️ ต้องทำเอง"]
```

### 10-2 High Availability

```mermaid
graph TB
    HA["🏗️ High Availability Solutions"] --> RAC["Oracle RAC<br>หลาย Instance<br>แชร์ 1 DB<br>→ Scale Out"]
    HA --> DG["Oracle Data Guard<br>Primary → Standby<br>→ Disaster Recovery"]
    HA --> ASM["Oracle ASM<br>จัดการ Storage อัตโนมัติ<br>Striping + Mirroring"]
    HA --> CW["Oracle Clusterware<br>จัดการ Cluster<br>Failover อัตโนมัติ"]
```

| Solution | จุดประสงค์หลัก |
|---|---|
| **Oracle RAC** | หลาย Server แชร์ 1 DB → Failover + Scale-out |
| **Oracle Data Guard** | จำลอง DB ไปยังไซต์สำรอง → Disaster Recovery |
| **Oracle ASM** | จัดการ Storage อัตโนมัติ (Striping + Mirroring) |
| **Oracle Clusterware** | จัดการ Cluster → Failover อัตโนมัติ |

---

## 📊 สรุปภาพรวมทั้งเล่ม

```mermaid
graph TB
    subgraph CH1["Ch.1 ภาพรวม"]
        DB_Basics["DB/RDBMS/SQL พื้นฐาน"]
        ORA_Arch["Oracle Architecture"]
    end
    subgraph CH23["Ch.2-3 เตรียมระบบ"]
        Install["ติดตั้ง (OUI)"]
        CreateDB["สร้าง DB (DBCA)"]
        Tools["EM Express / SQL*Plus"]
    end
    subgraph CH45["Ch.4-5 Network & Instance"]
        Net["Oracle Net / Listener"]
        Inst["Instance (SGA/PGA/BG)"]
        StartStop["เปิด/ปิด Instance"]
    end
    subgraph CH67["Ch.6-7 Storage & Security"]
        Storage["Tablespace / Files"]
        UserSec["User / Privileges / Roles"]
    end
    subgraph CH89["Ch.8-9 Objects & Monitor"]
        Schema["Schema / Table / Index / View"]
        Monitor["AWR / ADDM / Advisors"]
    end
    subgraph CH10["Ch.10 Backup & HA"]
        Backup["Backup / Recovery (RMAN)"]
        HighAvail["RAC / Data Guard / ASM"]
    end
    
    CH1 --> CH23 --> CH45 --> CH67 --> CH89 --> CH10
```

---

> [!note] แหล่งข้อมูล
> สรุปจากหนังสือ: **オラクルマスター教科書 Bronze DBA**
> สำนักพิมพ์: 翔泳社 (Shoeisha)
> ผู้เขียน: 株式会社コーソル 渡部亮太
