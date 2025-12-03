# Hướng Dẫn Testing với CANoe - CAPL Test Module

## Mục Lục
1. [Tổng Quan về CANoe Testing](#1-tổng-quan-về-canoe-testing)
2. [Cấu Trúc Test Module](#2-cấu-trúc-test-module)
3. [Hướng Dẫn Từng Bước](#3-hướng-dẫn-từng-bước)
4. [Ví Dụ Thực Tế từ Project](#4-ví-dụ-thực-tế-từ-project)
5. [Best Practices](#5-best-practices)

---

## 1. Tổng Quan về CANoe Testing

### 1.1 CANoe Test Feature Set là gì?

CANoe Test Feature Set là bộ công cụ tích hợp trong CANoe giúp bạn:
- **Tạo và thực thi test cases** một cách có cấu trúc
- **Tự động tạo test report** (báo cáo kết quả test)
- **Quản lý test cases** theo nhóm và module
- **Tích hợp với Test Management Systems**

### 1.2 Kiến Trúc Test System

```
┌─────────────────────────────────────────┐
│         CANoe Test Module               │
│  (CAPL/.NET/XML file)                   │
├─────────────────────────────────────────┤
│  • Test Module                          │
│    └── Test Groups                      │
│        └── Test Cases                   │
│            └── Test Steps               │
└─────────────────────────────────────────┘
           │
           ├──→ Bus Simulation
           ├──→ System Variables (I/O)
           ├──→ ECU Under Test (SUT)
           └──→ Test Report (XML/HTML)
```

---

## 2. Cấu Trúc Test Module

### 2.1 Các Thành Phần Chính

Trong CANoe testing, có 4 cấp độ tổ chức:

1. **Test Module** - File test chính (.can, .net, hoặc .xml)
2. **Test Group** - Nhóm các test cases liên quan (tùy chọn)
3. **Test Case** - Một test cụ thể để kiểm tra một chức năng
4. **Test Step** - Các bước nhỏ trong một test case

### 2.2 Verdicts (Kết Quả Test)

Mỗi test step và test case có thể có các kết quả:
- **PASS** ✅ - Test thành công
- **FAIL** ❌ - Test thất bại
- **INCONCLUSIVE** ⚠️ - Không xác định được kết quả
- **NONE** - Chưa có kết quả

---

## 3. Hướng Dẫn Từng Bước

### Bước 1: Chuẩn Bị Test Module

**Mục đích:** Thiết lập thông tin cơ bản cho test module

**Cần làm gì:**
1. Tạo file CAPL với extension `.can`
2. Khai báo các biến cần thiết
3. Định nghĩa hàm khởi tạo test module

**Ví dụ từ project của bạn:**

```capl
/*@!Encoding:1252*/
includes
{
  // Import các file .can khác nếu cần
}

variables
{
  // Định nghĩa timeout cho các wait commands
  const dword kWAIT_TIMEOUT = 500; // 500msecs
  int WaitResult; // Biến lưu kết quả wait
}
```

**Giải thích:**
- `kWAIT_TIMEOUT = 500`: Thời gian chờ tối đa là 500ms
- `WaitResult`: Biến lưu kết quả từ các hàm `TestWaitFor...`

---

### Bước 2: Thiết Lập Test Module Description

**Mục đích:** Thêm thông tin mô tả vào test report

**Làm TRƯỚC khi viết test cases**

**Ví dụ từ project:**

```capl
void cf_testPreparation() 
{ 
  // Mô tả test module
  TestModuleDescription("Sample test cases written in CAPL."); 
  
  // Thông tin về kỹ sư test
  TestReportAddEngineerInfo("Company", "VinFast.Ltd."); 
  TestReportAddEngineerInfo("Tester name", "Le Dinh Giang Son"); 
  
  // Thông tin về setup test
  TestReportAddSetupInfo("CANoe", "Version 15.0"); 
  TestReportAddSetupInfo("vTestStudio", "Version 5.0"); 
  
  // Thông tin về SUT (System Under Test)
  TestReportAddSUTInfo ("SUT", "Doors ECU"); 
}
```

**Giải thích từng dòng:**

1. `TestModuleDescription()`: Mô tả tổng quan về test module này
   - **Tác dụng:** Hiển thị trong test report để người đọc biết test này làm gì

2. `TestReportAddEngineerInfo()`: Thêm thông tin về người test
   - **Tác dụng:** Ghi lại ai đã viết/chạy test này
   - **Lý do:** Quan trọng để trace lại khi có vấn đề

3. `TestReportAddSetupInfo()`: Thông tin về môi trường test
   - **Tác dụng:** Ghi lại version CANoe, tool khác
   - **Lý do:** Các version khác nhau có thể cho kết quả khác nhau

4. `TestReportAddSUTInfo()`: Thông tin về ECU đang được test
   - **Tác dụng:** Xác định ECU nào đang được test
   - **Trong project:** Đang test "Doors ECU"

---

### Bước 3: Tạo PreConditions và PostConditions

**Mục đích:** Chuẩn hóa điều kiện trước và sau mỗi test case

**Làm SAU Bước 2, TRƯỚC khi viết test cases**

**Ví dụ từ project:**

```capl
testfunction PreConditions() 
{ 
  testStep("Pre-cond","Start"); 
  testStep("","Set Ignition to ON"); 
  
  // Set Ignition to ON 
  @sysvar::testNS::IgnitionStart = @sysvar::testNS::IgnitionStart::Ign_ON; 
  testWaitForTimeout(500); 
  
  testStep("Pre-cond","End"); 
}

testfunction PostConditions() 
{ 
  testStep("Post-cond","Start"); 
  testStep("","Set Ignition to OFF"); 
  
  // Set Ignition to OFF 
  @sysvar::testNS::IgnitionStart = @sysvar::testNS::IgnitionStart::Ign_OFF; 
  testWaitForTimeout(500); 
  
  testStep("Post-cond","End"); 
}
```

**Giải thích:**

1. **`testfunction`**: Không phải test case, chỉ là hàm helper
   - **Tác dụng:** Có thể gọi lại nhiều lần từ các test cases

2. **`testStep()`**: Đánh dấu một bước trong test
   - **Cú pháp:** `testStep("Nhóm", "Mô tả")`
   - **Tác dụng:** Tạo trace trong test report để theo dõi test đang ở bước nào

3. **`@sysvar::`**: Truy cập system variable
   - **Trong ví dụ:** Set Ignition ON/OFF
   - **Tác dụng:** Điều khiển các tín hiệu I/O từ CANoe

4. **`testWaitForTimeout(500)`**: Chờ 500ms
   - **Tác dụng:** Cho ECU thời gian xử lý sau khi thay đổi trạng thái

**Lý do cần PreConditions/PostConditions:**
- ✅ Đảm bảo mọi test case bắt đầu ở cùng một trạng thái
- ✅ Dọn dẹp sau test (reset về trạng thái ban đầu)
- ✅ Code gọn, không lặp lại

---

### Bước 4: Viết Test Case

**Mục đích:** Kiểm tra một chức năng cụ thể của ECU

**Cấu trúc cơ bản:**

```capl
testcase TênTestCase()
{
  // 1. Đặt tên test case
  TestCaseTitle("Nhóm", "Tên test");
  
  // 2. Chuẩn bị môi trường
  PreConditions();
  
  // 3. Các test steps
  testStep("", "Mô tả bước");
  // ... thực hiện test ...
  
  // 4. Dọn dẹp
  PostConditions();
}
```

**Ví dụ từ project - Test Case Locking:**

```capl
testcase ctc_RequestLock() 
{ 
  // Khai báo message để nhận
  message GW_BCM_DoorSts_0x3D0 LockingStatus; 
   
  // Đặt tên test case
  TestCaseTitle("Locking Test", "Request to Lock"); 
   
  // Chuẩn bị môi trường (bật Ignition)
  PreConditions(); 
   
  // BƯỚC 1: Test Unlocking
  testStep("","Set request to Lock State"); 
  @sysvar::testNS::LockRq = @sysvar::testNS::LockRq::RqToUnlock; 
   
  TestStep("Unlocking Test", "Set Locking request to RqToUnlock"); 
  @sysvar::testNS::LockRq = @sysvar::testNS::LockRq::RqToUnlock; 
   
  // Chờ ECU phản hồi
  WaitResult = TestWaitForMessage(GW_BCM_DoorSts_0x3D0, kWAIT_TIMEOUT); 
   
  // Kiểm tra kết quả
  switch(WaitResult) 
  { 
    case 0: 
      TestStepFail("Message not received"); // Timeout
      break; 
    case 1: 
      // Nhận được message
      TestGetWaitEventMsgData(LockingStatus); 
      
      // Kiểm tra trạng thái
      if(LockingStatus.STAT_DoorLockDriver == STAT_DoorLockDriver::Unlocked ) 
        TestStepPass("Test Step 1", "Door is Unlocked"); 
      else 
        TestStepFail("Test Step 1", "Still Locked"); 
      break; 
  } 
  
  // BƯỚC 2: Test Locking
  TestWaitForTimeout(kWAIT_TIMEOUT); 
   
  TestStep("Locking Test", "Set Locking request to RqToLock"); 
  @sysvar::testNS::LockRq = @sysvar::testNS::LockRq::RqToLock; 
   
  // Chờ ECU phản hồi
  WaitResult = TestWaitForMessage(GW_BCM_DoorSts_0x3D0, kWAIT_TIMEOUT); 
  
  // Kiểm tra kết quả
  switch(WaitResult) 
  { 
    case 0: 
      TestStepFail("Message not received"); 
      break; 
    case 1: 
      TestGetWaitEventMsgData(LockingStatus);
      
      if(LockingStatus.STAT_DoorLockDriver == STAT_DoorLockDriver::Locked ) 
        TestStepPass("Test Step 1", "Door is Locked"); 
      else 
        TestStepFail("Test Step 1", "Still Unlocked"); 
      break; 
  } 
  
  TestWaitForTimeout(kWAIT_TIMEOUT); 
  
  // Dọn dẹp
  PostConditions(); 
}
```

**Giải thích chi tiết:**

#### 4.1 Khai Báo Message
```capl
message GW_BCM_DoorSts_0x3D0 LockingStatus;
```
- **Tác dụng:** Tạo biến để nhận dữ liệu từ message CAN
- **Message này:** Báo cáo trạng thái khóa cửa từ BCM (Body Control Module)

#### 4.2 TestCaseTitle()
```capl
TestCaseTitle("Locking Test", "Request to Lock");
```
- **Tham số 1:** Nhóm test (hiển thị trong report)
- **Tham số 2:** Tên test case cụ thể
- **Tác dụng:** Tạo tiêu đề trong test report

#### 4.3 Kích Thích ECU (Stimulus)
```capl
@sysvar::testNS::LockRq = @sysvar::testNS::LockRq::RqToUnlock;
```
- **Tác dụng:** Gửi yêu cầu unlock đến ECU
- **System Variable:** Định nghĩa trong CANoe database (.dbc/.ini)

#### 4.4 Chờ Phản Hồi (Wait for Response)
```capl
WaitResult = TestWaitForMessage(GW_BCM_DoorSts_0x3D0, kWAIT_TIMEOUT);
```
- **Tác dụng:** Chờ ECU gửi message phản hồi
- **Giá trị trả về:**
  - `0` = Timeout (không nhận được message)
  - `1` = Nhận được message thành công

#### 4.5 Lấy Dữ Liệu Message
```capl
TestGetWaitEventMsgData(LockingStatus);
```
- **Tác dụng:** Lấy dữ liệu từ message vừa nhận được
- **Sau khi gọi:** Biến `LockingStatus` chứa dữ liệu mới nhất

#### 4.6 Kiểm Tra và Đưa Ra Verdict
```capl
if(LockingStatus.STAT_DoorLockDriver == STAT_DoorLockDriver::Unlocked ) 
  TestStepPass("Test Step 1", "Door is Unlocked"); 
else 
  TestStepFail("Test Step 1", "Still Locked");
```
- **TestStepPass()**: Đánh dấu test step thành công
- **TestStepFail()**: Đánh dấu test step thất bại
- **Tác dụng:** Ghi lại kết quả vào test report

---

### Bước 5: Sử Dụng Wait Commands

**Có 3 loại Wait Commands chính:**

#### 5.1 Wait for Timeout
```capl
testWaitForTimeout(500); // Chờ 500ms
```
- **Dùng khi:** Cần chờ một khoảng thời gian cố định
- **Ví dụ:** Sau khi set Ignition ON, chờ ECU khởi động

#### 5.2 Wait for Message
```capl
WaitResult = TestWaitForMessage(GW_BCM_DoorSts_0x3D0, kWAIT_TIMEOUT);
```
- **Dùng khi:** Chờ một message CAN cụ thể
- **Timeout:** Nếu không nhận được trong `kWAIT_TIMEOUT`, trả về 0

#### 5.3 Wait for Condition (Nâng cao)
```capl
TestWaitForSysVarValue(@sysvar::Main::Velocity, 16, 200);
```
- **Dùng khi:** Chờ một system variable đạt giá trị cụ thể
- **Ví dụ:** Chờ tốc độ xe đạt 16 km/h

**Ví dụ từ project - Test Auto Lock:**

```capl
testcase ctc_AutoLock() 
{ 
  message EngineStatus EngState; 
  message LockingState LockSysState; 
  byte ind1, ind2; 
   
  TestCaseTitle("Locking Test", "Auto Lock"); 
   
  PreConditions(); 
   
  // Unlock cửa trước
  testStep("","Set Locking request to RqToUnlock"); 
  @sysvar::Main::LockRq = @sysvar::Main::LockRq::RqToUnlock; 
   
  // Set tốc độ 15 km/h (dưới ngưỡng auto-lock)
  testStep("Set speed","15 kmph"); 
  @sysvar::Main::Velocity = 15; 
   
  // Chờ 2 message cùng lúc
  ind1 = testJoinMessageEvent(EngineStatus); 
  ind2 = testJoinMessageEvent(LockingState); 
  testWaitForAllJoinedEvents(200); 
  testGetWaitEventMsgData(ind1, EngState); 
  testGetWaitEventMsgData(ind2, LockSysState); 
   
  // Kiểm tra: Ở 15 km/h, cửa vẫn Unlocked
  if(EngState.Velocity == 15) 
  { 
    testWaitForTimeout(50); 
    if(LockSysState.LockState == VtSig_LockState::Unlocked) 
      testStepPass("Door is in Unlocked state before reaching the speed threshold"); 
    else 
      testStepFail("Door is not in Unlocked state before reaching the speed threshold"); 
  } 
   
  // Set tốc độ 16 km/h (trên ngưỡng auto-lock)
  testStep("Set speed","16 kmph"); 
  @sysvar::Main::Velocity = 16; 
   
  // Chờ lại
  ind1 = testJoinMessageEvent(EngineStatus); 
  ind2 = testJoinMessageEvent(LockingState); 
  testWaitForAllJoinedEvents(200); 
  testGetWaitEventMsgData(ind1, EngState); 
  testGetWaitEventMsgData(ind2, LockSysState); 
   
  // Kiểm tra: Ở 16 km/h, cửa phải Locked (auto-lock)
  if(EngState.Velocity == 16) 
  { 
    testWaitForMessage(LockingState, 200); 
    if(LockSysState.LockState == VtSig_LockState::Locked) 
      testStepPass("Door is in Locked state after reaching the speed threshold");
    else 
      testStepFail("Door is not in Locked state after reaching the speed threshold"); 
  }
  
  // Reset
  testStep("","Reset speed back to 0 kmph"); 
  @sysvar::Main::Velocity = 0; 
  PostConditions(); 
}
```

**Giải thích về Wait Multiple Messages:**

```capl
ind1 = testJoinMessageEvent(EngineStatus); 
ind2 = testJoinMessageEvent(LockingState); 
testWaitForAllJoinedEvents(200); 
testGetWaitEventMsgData(ind1, EngState); 
testGetWaitEventMsgData(ind2, LockSysState);
```

1. **`testJoinMessageEvent()`**: Đăng ký chờ một message
   - Trả về một identifier (ind1, ind2)

2. **`testWaitForAllJoinedEvents(200)`**: Chờ TẤT CẢ các message đã đăng ký
   - Timeout: 200ms
   - **Tác dụng:** Đợi cả 2 message cùng lúc thay vì chờ từng cái một

3. **`testGetWaitEventMsgData(ind, msg)`**: Lấy dữ liệu từ message đã chờ
   - Dùng identifier để biết lấy message nào

**Lý do dùng:** Khi cần kiểm tra 2 message cùng lúc để đảm bảo logic đúng

---

### Bước 6: MainTest() - Entry Point

**Mục đích:** Điểm bắt đầu khi test module được chạy

**Ví dụ từ project:**

```capl
void MainTest() 
{ 
  cf_testPreparation();  // Thiết lập test module
  ctc_RequestLock();     // Chạy test case
}
```

**Giải thích:**

1. **`MainTest()`**: Hàm tự động được gọi khi test module start
   - **Tác dụng:** Điểm khởi đầu của mọi thứ
   - **Lý do:** CANoe sẽ tự gọi hàm này

2. **Thứ tự thực thi:**
   - Bước 1: `cf_testPreparation()` - Thiết lập thông tin test module
   - Bước 2: `ctc_RequestLock()` - Chạy test case

**Lưu ý:** 
- Nếu muốn chạy nhiều test cases, có thể gọi nhiều lần:
```capl
void MainTest() 
{ 
  cf_testPreparation();
  ctc_RequestLock();
  ctc_AutoLock();
  // ... các test case khác
}
```

---

## 4. Ví Dụ Thực Tế từ Project

### Ví Dụ 1: Test Locking/Unlocking

**Mục tiêu:** Kiểm tra ECU có phản ứng đúng khi nhận yêu cầu lock/unlock

**Flow:**
```
1. PreConditions() → Bật Ignition
2. Gửi yêu cầu Unlock
3. Chờ message phản hồi
4. Kiểm tra cửa đã Unlock chưa
5. Gửi yêu cầu Lock
6. Chờ message phản hồi
7. Kiểm tra cửa đã Lock chưa
8. PostConditions() → Tắt Ignition
```

**Các điểm quan trọng:**
- ✅ Luôn chờ phản hồi từ ECU (không giả định)
- ✅ Kiểm tra timeout (case 0)
- ✅ Kiểm tra giá trị thực tế trong message
- ✅ Đưa ra verdict rõ ràng (Pass/Fail)

### Ví Dụ 2: Test Auto Lock

**Mục tiêu:** Kiểm tra tự động khóa cửa khi xe đạt tốc độ 16 km/h

**Flow:**
```
1. PreConditions() → Bật Ignition, Unlock cửa
2. Set tốc độ = 15 km/h
3. Kiểm tra: Cửa vẫn Unlocked
4. Set tốc độ = 16 km/h
5. Kiểm tra: Cửa tự động Locked
6. Reset tốc độ = 0
7. PostConditions() → Tắt Ignition
```

**Các điểm quan trọng:**
- ✅ Test cả 2 trường hợp: dưới ngưỡng và trên ngưỡng
- ✅ Dùng `testJoinMessageEvent()` để chờ nhiều message cùng lúc
- ✅ Kiểm tra cả tốc độ VÀ trạng thái khóa

---

## 5. Best Practices

### 5.1 Tổ Chức Code

**✅ NÊN:**
- Tách PreConditions/PostConditions thành hàm riêng
- Đặt tên test case rõ ràng (prefix: `ctc_` = CAPL test case)
- Comment giải thích logic phức tạp
- Dùng constants cho timeout và giá trị cố định

**❌ KHÔNG NÊN:**
- Viết test case quá dài (>200 dòng)
- Hard-code giá trị (dùng constants)
- Bỏ qua kiểm tra timeout
- Giả định ECU luôn phản hồi

### 5.2 Wait Commands

**✅ NÊN:**
- Luôn set timeout hợp lý (không quá ngắn, không quá dài)
- Kiểm tra kết quả wait (case 0 = timeout)
- Dùng `testWaitForTimeout()` sau khi thay đổi system variable

**❌ KHÔNG NÊN:**
- Dùng timeout = 0
- Bỏ qua kiểm tra WaitResult
- Chờ quá nhiều message cùng lúc (khó debug)

### 5.3 Test Steps

**✅ NÊN:**
- Đánh dấu testStep ở mỗi bước quan trọng
- Mô tả rõ ràng trong testStep
- Nhóm các testStep có liên quan

**❌ KHÔNG NÊN:**
- Đánh dấu testStep quá nhiều (gây rối report)
- Mô tả mơ hồ ("Do something")

### 5.4 Test Report

**✅ NÊN:**
- Điền đầy đủ thông tin trong `cf_testPreparation()`
- Đặt tên test case có ý nghĩa
- Sử dụng `TestReportAddWindowCapture()` để chụp trace (nếu cần)

### 5.5 Error Handling

**✅ NÊN:**
```capl
WaitResult = TestWaitForMessage(MyMessage, timeout);
switch(WaitResult)
{
  case 0: 
    TestStepFail("Message not received - Timeout");
    break;
  case 1:
    // Xử lý thành công
    break;
  default:
    TestStepFail("Unexpected error");
}
```

**❌ KHÔNG NÊN:**
```capl
TestWaitForMessage(MyMessage, timeout);
// Giả định luôn nhận được message
```

---

## 6. Thứ Tự Thực Hiện Khi Tạo Test Module Mới

### Checklist từng bước:

```
□ Bước 1: Tạo file .can mới
  └─ Đặt tên có ý nghĩa (ví dụ: DoorLockingTest.can)

□ Bước 2: Khai báo includes và variables
  └─ Import các file cần thiết
  └─ Định nghĩa constants (timeout, etc.)

□ Bước 3: Viết hàm cf_testPreparation()
  └─ TestModuleDescription()
  └─ TestReportAddEngineerInfo()
  └─ TestReportAddSetupInfo()
  └─ TestReportAddSUTInfo()

□ Bước 4: Viết PreConditions()
  └─ Thiết lập trạng thái ban đầu (Ignition ON, etc.)
  └─ Dùng testStep() để đánh dấu

□ Bước 5: Viết PostConditions()
  └─ Reset về trạng thái ban đầu (Ignition OFF, etc.)
  └─ Dùng testStep() để đánh dấu

□ Bước 6: Viết test cases
  └─ TestCaseTitle()
  └─ Gọi PreConditions()
  └─ Các test steps với kiểm tra kỹ lưỡng
  └─ Gọi PostConditions()

□ Bước 7: Viết MainTest()
  └─ Gọi cf_testPreparation()
  └─ Gọi các test cases

□ Bước 8: Test và Debug
  └─ Chạy từng test case một
  └─ Kiểm tra test report
  └─ Fix lỗi nếu có
```

---

## 7. So Sánh với Code Thực Tế

### Mapping từ tài liệu sang code của bạn:

| Khái niệm trong tài liệu | Trong code của bạn | Ví dụ |
|-------------------------|-------------------|-------|
| **Test Module** | File `FunctionalTest.can` | Toàn bộ file |
| **Test Case** | Hàm `testcase ctc_RequestLock()` | Dòng 133-190 |
| **Test Step** | `testStep()` | Dòng 141, 144, 167 |
| **PreConditions** | Hàm `PreConditions()` | Dòng 29-37 |
| **PostConditions** | Hàm `PostConditions()` | Dòng 39-47 |
| **Wait Command** | `TestWaitForMessage()` | Dòng 148, 171 |
| **Verdict** | `TestStepPass()` / `TestStepFail()` | Dòng 160, 162 |
| **Test Report Info** | `TestReportAdd...()` | Dòng 23-27 |

---

## 8. Tài Liệu Tham Khảo

- [CANoe Test Feature Set Documentation](https://robertscaplblog.wordpress.com/wp-content/uploads/2016/02/an-ind-1-002_testing_with_canoe.pdf)
- Vector CANoe Help System
- CAPL Programming Guide

---

## 9. Câu Hỏi Thường Gặp (FAQ)

### Q1: Khi nào dùng `testWaitForTimeout()` vs `TestWaitForMessage()`?

**A:** 
- `testWaitForTimeout()`: Khi cần chờ một khoảng thời gian cố định (ví dụ: cho ECU khởi động)
- `TestWaitForMessage()`: Khi cần chờ ECU phản hồi một message cụ thể (ví dụ: chờ status message)

### Q2: Test case của tôi fail nhưng không biết lý do?

**A:** Kiểm tra:
1. Có nhận được message không? (WaitResult == 1?)
2. Giá trị trong message đúng chưa?
3. Timeout có đủ dài không?
4. PreConditions có đúng không?

### Q3: Làm sao test nhiều test cases liên tiếp?

**A:** Trong `MainTest()`, gọi nhiều test cases:
```capl
void MainTest() 
{ 
  cf_testPreparation();
  ctc_RequestLock();
  ctc_AutoLock();
  // ... thêm các test case khác
}
```

### Q4: Test report được lưu ở đâu?

**A:** Mặc định trong thư mục của CANoe project, định dạng XML và HTML tự động được tạo sau khi test chạy xong.

---

**Tác giả:** Generated based on CANoe Testing Documentation và code analysis  
**Ngày tạo:** 2024  
**Phiên bản:** 1.0

