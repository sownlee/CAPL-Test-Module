# Testing with CANoe - Hướng dẫn chi tiết

**Tài liệu tham khảo:** [an-ind-1-002_testing_with_canoe.pdf](https://robertscaplblog.wordpress.com/wp-content/uploads/2016/02/an-ind-1-002_testing_with_canoe.pdf)

---

## 📋 MỤC LỤC

1. [Tổng quan về Testing trong CANoe](#1-tổng-quan-về-testing-trong-canoe)
2. [Hai loại Test Setup](#2-hai-loại-test-setup)
3. [Cấu trúc Test Module](#3-cấu-trúc-test-module)
4. [Các bước Setup từ đầu](#4-các-bước-setup-từ-đầu)
5. [Giải thích từng thành phần](#5-giải-thích-từng-thành-phần)
6. [Workflow thực hiện test](#6-workflow-thực-hiện-test)

---

## 1. TỔNG QUAN VỀ TESTING TRONG CANOE

### 1.1. Testing là gì?

**Testing trong CANoe** là quá trình tự động hóa việc kiểm tra chức năng của ECU (Electronic Control Unit) trên vehicle thật hoặc HIL (Hardware-in-the-Loop) setup.

### 1.2. Tại sao cần Testing với CANoe?

| **Lợi ích** | **Mô tả** |
|------------|-----------|
| **Tự động hóa** | Chạy hàng trăm test cases mà không cần can thiệp thủ công |
| **Reproducible** | Lặp lại chính xác cùng một test nhiều lần |
| **Edge Cases** | Tạo các tình huống khó test thủ công (timeout, wrong CRC, invalid data) |
| **Test Report** | Tự động generate report với pass/fail status |
| **Regression Testing** | Chạy lại toàn bộ test suite sau mỗi lần update firmware |
| **CI/CD Integration** | Tích hợp vào pipeline tự động |

### 1.3. Test Architecture trong CANoe

```
┌─────────────────────────────────────────────────┐
│              CANoe Test Environment              │
├─────────────────────────────────────────────────┤
│  Test Control (MainTest)                        │
│    ↓                                            │
│  Test Functions (PreConditions, PostConditions) │
│    ↓                                            │
│  Test Cases (TC01, TC02, ...)                  │
│    ↓                                            │
│  Test Steps (testStep, testStepPass/Fail)      │
└─────────────────────────────────────────────────┘
         ↓                    ↓
    CAN Bus Messages    System Variables
         ↓                    ↓
    Real Vehicle ECU    Simulation Nodes
```

---

## 2. HAI LOẠI TEST SETUP

### 2.1. Test Units (vTESTstudio)

**Mục đích:** Test cases được viết bằng vTESTstudio (tool riêng của Vector)

**Khi nào dùng:**
- Team có license vTESTstudio
- Cần test cases phức tạp với nhiều logic
- Muốn tách biệt test design và implementation
- Cần test management system tích hợp

**Workflow:**
```
vTESTstudio → Tạo test cases → Export → CANoe Test Units → Execute
```

### 2.2. Test Modules (CAPL)

**Mục đích:** Test cases được viết trực tiếp trong CANoe bằng CAPL

**Khi nào dùng:**
- ✅ **Dùng cho project này** - Test đơn giản, nhanh
- Không cần license vTESTstudio
- Test cases đơn giản, logic rõ ràng
- Muốn tất cả trong một môi trường CANoe

**Workflow:**
```
CAPL Browser → Viết test cases → Test Module → Execute trong CANoe
```

**→ Chúng ta sẽ dùng Test Modules (CAPL) cho project này**

---

## 3. CẤU TRÚC TEST MODULE

### 3.1. Sơ đồ cấu trúc

```
Test Module CAPL File
├── Variables Section
│   └── Khai báo biến, constants
│
├── MainTest() [Test Control]
│   └── Điều khiển thứ tự chạy test cases
│
├── Test Functions
│   ├── PreConditions() - Setup trước khi test
│   └── PostConditions() - Cleanup sau khi test
│
└── Test Cases
    ├── testcase TC01_...()
    ├── testcase TC02_...()
    └── testcase TC03_...()
```

### 3.2. So sánh với Network Node CAPL

| **Test Module CAPL** | **Network Node CAPL** |
|---------------------|----------------------|
| Có `MainTest()`, `testcase`, `testfunction` | Có `on start`, `on message`, `on timer` |
| Dùng `testStep()`, `TestWaitForMessage()` | Dùng `output()`, `on message` |
| Tự động generate test report | Không có test report |
| Chạy theo thứ tự trong `MainTest()` | Chạy theo event-driven |
| **Mục đích:** Test validation | **Mục đích:** Simulation |

---

## 4. CÁC BƯỚC SETUP TỪ ĐẦU

### **BƯỚC 1: Tạo Test Environment**

**Mục đích:** Tạo container chứa tất cả test modules

**Cách làm:**
1. Mở CANoe
2. Vào tab **Test** → Click **Test Setup** (trong nhóm Test Modules)
3. Right-click vào vùng trống → **New Test Environment**
4. Đặt tên: `te_FunctionalTests` (hoặc tên khác)
5. Right-click → **Save** → Chọn folder `Test Files` → **Save**

**Tại sao cần:**
- Tổ chức test modules theo nhóm
- Dễ quản lý nhiều test suites khác nhau
- Có thể save/load test environment

---

### **BƯỚC 2: Tạo CAPL Test Module**

**Mục đích:** Tạo file CAPL chứa test cases

**Cách làm:**
1. Right-click vào Test Environment vừa tạo
2. Chọn **Insert CAPL Test Module**
3. Right-click vào Test Module mới → **Configuration**
4. Đặt tên: `tm_FunctionalTests`
5. Click **File** → Navigate đến folder `Test Files`
6. Đặt tên file: `BCM_TestModule.can` → **Open** → **OK**

**Tại sao cần:**
- File CAPL này sẽ chứa tất cả test logic
- CANoe sẽ compile và execute file này
- Có thể edit bằng CAPL Browser

---

### **BƯỚC 3: Cấu hình Test Report**

**Mục đích:** Setup nơi lưu test report

**Cách làm:**
1. Right-click vào Test Module → **Configuration**
2. Vào tab **Test Report**
3. Trong **Test reports path**, browse đến folder `Test Reports`
4. Click **OK**

**Tại sao cần:**
- Test report sẽ được lưu tự động sau mỗi lần chạy
- Report chứa: pass/fail status, test steps, timestamps, screenshots
- Cần cho documentation và traceability

---

### **BƯỚC 4: Mở CAPL Browser để viết code**

**Mục đích:** Viết test cases vào file CAPL

**Cách làm:**
1. Right-click vào Test Module → **Edit**
2. CAPL Browser sẽ mở với file `BCM_TestModule.can`
3. Bạn sẽ thấy 3 event types mới:
   - **Test Control** (MainTest)
   - **Test Functions** (PreConditions, PostConditions)
   - **Test Cases** (testcase)

**Tại sao cần:**
- CAPL Browser có syntax highlighting cho test functions
- Auto-complete cho test APIs
- Compile và check errors trước khi run

---

### **BƯỚC 5: Viết Test Module Code**

**Mục đích:** Implement test logic

**Cấu trúc code mẫu:**

```capl
/*@!Encoding:1252*/
variables {
    // Khai báo biến ở đây
    const dword kWAIT_TIMEOUT = 500;
    int WaitResult;
}

// ========== TEST CONTROL ==========
void MainTest() {
    // Hàm này chạy đầu tiên, điều khiển thứ tự test cases
    cf_testPreparation();  // Setup test module info
    TC01_BasicLockUnlock(); // Chạy test case 1
    TC02_WindowControl();   // Chạy test case 2
    // ... các test case khác
}

// ========== TEST PREPARATION ==========
void cf_testPreparation() {
    // Thêm thông tin vào test report
    TestModuleDescription("BCM Functional Test Cases");
    TestReportAddEngineerInfo("Company", "VinFast.Ltd.");
    TestReportAddEngineerInfo("Tester name", "Your Name");
    TestReportAddSetupInfo("CANoe", "Version 15.0");
    TestReportAddSUTInfo("SUT", "BCM ECU");
}

// ========== TEST FUNCTIONS ==========
testfunction PreConditions() {
    testStep("Pre-cond", "Start");
    // Setup môi trường trước khi test
    @sysvar::testNS::IgnitionStart = @sysvar::testNS::IgnitionStart::Ign_ON;
    testWaitForTimeout(500);
    testStep("Pre-cond", "End");
}

testfunction PostConditions() {
    testStep("Post-cond", "Start");
    // Cleanup sau khi test
    @sysvar::testNS::IgnitionStart = @sysvar::testNS::IgnitionStart::Ign_OFF;
    testWaitForTimeout(500);
    testStep("Post-cond", "End");
}

// ========== TEST CASES ==========
testcase TC01_BasicLockUnlock() {
    message 0x10D msgCmd;    // Command message
    message 0x107 msgStatus; // Status message
    
    testStep("TC01", "BCM Basic Lock/Unlock Test");
    
    // Gửi lệnh Lock
    msgCmd.MHU_BCM_RemoteDoorCtrl = 1; // Lock
    output(msgCmd);
    testWaitForTimeout(1000);
    
    // Chờ và kiểm tra response
    if (TestWaitForMessage(msgStatus, 500) != 1) {
        testStepFail("Không nhận được status message");
        return;
    }
    
    // Validate kết quả
    if (msgStatus.STAT_DoorLockDriver == 1) {
        testStepPass("Door locked successfully");
    } else {
        testStepFail("Door lock failed");
    }
}
```

**Tại sao cần từng phần:**
- `MainTest()`: Điều khiển flow, dễ thêm/bớt test cases
- `PreConditions()`: Đảm bảo môi trường sẵn sàng (ignition ON, etc.)
- `PostConditions()`: Reset về trạng thái ban đầu
- `testcase`: Mỗi test case độc lập, dễ maintain

---

### **BƯỚC 6: Compile và Run Test**

**Mục đích:** Chạy test và xem kết quả

**Cách làm:**
1. Trong CAPL Browser, click **Compile** (hoặc F7)
2. Kiểm tra không có errors
3. Quay lại CANoe → Tab **Test**
4. Click **Start** để chạy test
5. Xem kết quả trong **Test Report Window**

**Tại sao cần:**
- Compile check syntax errors trước khi run
- Test Report hiển thị real-time pass/fail
- Có thể pause/resume test nếu cần

---

## 5. GIẢI THÍCH TỪNG THÀNH PHẦN

### 5.1. Test Control - `MainTest()`

**Mục đích:** Entry point, điều khiển thứ tự chạy test cases

**Cú pháp:**
```capl
void MainTest() {
    // Gọi các test cases theo thứ tự
    TC01_Test1();
    TC02_Test2();
    TC03_Test3();
}
```

**Tại sao cần:**
- ✅ **Điều khiển flow:** Quyết định test nào chạy trước, sau
- ✅ **Dễ maintain:** Thêm/bớt test cases chỉ cần sửa một chỗ
- ✅ **Conditional execution:** Có thể thêm if/switch để chọn test cases

**Ví dụ:**
```capl
void MainTest() {
    cf_testPreparation();
    
    // Chỉ chạy test cases cơ bản
    TC01_BasicLockUnlock();
    TC02_WindowControl();
    
    // Skip test cases nâng cao nếu cần
    // TC03_ComplexScenario();
}
```

---

### 5.2. Test Functions - `PreConditions()` và `PostConditions()`

**Mục đích:** Setup và cleanup môi trường test

#### **PreConditions()**

**Cú pháp:**
```capl
testfunction PreConditions() {
    testStep("Pre-cond", "Start");
    // Setup code
    @sysvar::testNS::IgnitionStart = Ign_ON;
    testWaitForTimeout(500);
    testStep("Pre-cond", "End");
}
```

**Tại sao cần:**
- ✅ **Đảm bảo môi trường sẵn sàng:** Ignition ON, vehicle speed = 0, etc.
- ✅ **Consistency:** Mọi test case bắt đầu từ cùng một trạng thái
- ✅ **Reproducible:** Test có thể chạy lại nhiều lần với kết quả giống nhau

**Ví dụ:**
```capl
testfunction PreConditions() {
    testStep("Pre-cond", "Setting up test environment");
    
    // 1. Set Ignition ON
    @sysvar::testNS::IgnitionStart = Ign_ON;
    testWaitForTimeout(500);
    
    // 2. Reset vehicle speed
    @sysvar::testNS::VehicleSpeed = 0;
    testWaitForTimeout(200);
    
    // 3. Unlock all doors
    @sysvar::testNS::LockRequest = RqToUnlock;
    testWaitForTimeout(1000);
    
    testStep("Pre-cond", "Environment ready");
}
```

#### **PostConditions()**

**Cú pháp:**
```capl
testfunction PostConditions() {
    testStep("Post-cond", "Start");
    // Cleanup code
    @sysvar::testNS::IgnitionStart = Ign_OFF;
    testWaitForTimeout(500);
    testStep("Post-cond", "End");
}
```

**Tại sao cần:**
- ✅ **Reset về trạng thái ban đầu:** Để test tiếp theo không bị ảnh hưởng
- ✅ **Safety:** Tắt các chức năng có thể gây nguy hiểm
- ✅ **Clean state:** Đảm bảo test độc lập với nhau

**Ví dụ:**
```capl
testfunction PostConditions() {
    testStep("Post-cond", "Cleaning up");
    
    // 1. Reset all requests
    @sysvar::testNS::LockRequest = No_Request;
    @sysvar::testNS::WindowRequest = No_Request;
    
    // 2. Reset vehicle speed
    @sysvar::testNS::VehicleSpeed = 0;
    
    // 3. Set Ignition OFF (optional)
    // @sysvar::testNS::IgnitionStart = Ign_OFF;
    
    testWaitForTimeout(500);
    testStep("Post-cond", "Cleanup complete");
}
```

---

### 5.3. Test Cases - `testcase TC01_...()`

**Mục đích:** Định nghĩa một test case cụ thể

**Cú pháp:**
```capl
testcase TC01_BasicLockUnlock() {
    // Test logic here
    testStep("Step 1", "Description");
    // ... actions ...
    testStepPass("Step passed");
    // hoặc
    testStepFail("Step failed");
}
```

**Tại sao cần:**
- ✅ **Modularity:** Mỗi test case độc lập, dễ maintain
- ✅ **Reusability:** Có thể gọi lại test case trong MainTest()
- ✅ **Traceability:** Mỗi test case có tên rõ ràng, dễ track trong report

**Cấu trúc test case điển hình:**

```capl
testcase TC01_BasicLockUnlock() {
    // 1. Khai báo messages (phải khai báo trong testcase)
    message 0x10D msgCmd;
    message 0x107 msgStatus;
    
    // 2. Set test case title (optional)
    TestCaseTitle("Door Control", "Basic Lock/Unlock");
    
    // 3. Gọi PreConditions (optional)
    PreConditions();
    
    // 4. Test Step 1: Lock
    testStep("Step 1", "Send Lock command");
    msgCmd.MHU_BCM_RemoteDoorCtrl = 1; // Lock
    output(msgCmd);
    testWaitForTimeout(1000);
    
    // 5. Wait và validate response
    if (TestWaitForMessage(msgStatus, 500) != 1) {
        testStepFail("No response received");
        return; // Exit test case nếu fail
    }
    
    // 6. Validate kết quả
    if (msgStatus.STAT_DoorLockDriver == 1) {
        testStepPass("Door locked successfully");
    } else {
        testStepFail("Door lock failed");
        return;
    }
    
    // 7. Test Step 2: Unlock (tương tự)
    testStep("Step 2", "Send Unlock command");
    msgCmd.MHU_BCM_RemoteDoorCtrl = 2; // Unlock
    output(msgCmd);
    testWaitForTimeout(1000);
    
    // ... validation ...
    
    // 8. Gọi PostConditions (optional)
    PostConditions();
}
```

---

### 5.4. Test Step Functions

#### **`testStep(title, description)`**

**Mục đích:** Log một bước trong test case

**Cú pháp:**
```capl
testStep("Step 1", "Send Lock command");
```

**Tại sao cần:**
- ✅ **Traceability:** Biết test đang ở bước nào
- ✅ **Debugging:** Dễ tìm lỗi khi xem test report
- ✅ **Documentation:** Test report tự động có mô tả từng bước

---

#### **`testStepPass(title, message)`**

**Mục đích:** Đánh dấu test step PASSED

**Cú pháp:**
```capl
testStepPass("Step 1", "Door locked successfully");
```

**Tại sao cần:**
- ✅ **Explicit pass:** Rõ ràng step nào đã pass
- ✅ **Report:** Hiển thị trong test report với màu xanh
- ✅ **Statistics:** Đếm số test steps passed

---

#### **`testStepFail(title, message)`**

**Mục đích:** Đánh dấu test step FAILED

**Cú pháp:**
```capl
testStepFail("Step 1", "Door lock failed - expected locked but got unlocked");
```

**Tại sao cần:**
- ✅ **Explicit fail:** Rõ ràng step nào fail và lý do
- ✅ **Report:** Hiển thị trong test report với màu đỏ
- ✅ **Debugging:** Giúp developer biết lỗi ở đâu

**Lưu ý:** Sau `testStepFail()`, nên dùng `return` để dừng test case (trừ khi muốn tiếp tục test các steps khác).

---

### 5.5. Message Waiting Functions

#### **`TestWaitForMessage(message, timeout)`**

**Mục đích:** Chờ một message cụ thể xuất hiện trên CAN bus

**Cú pháp:**
```capl
int result = TestWaitForMessage(msgStatus, 500); // timeout = 500ms
```

**Return values:**
- `1`: Message đã nhận được
- `0`: Timeout - không nhận được message trong thời gian chờ

**Tại sao cần:**
- ✅ **Synchronous testing:** Đảm bảo ECU đã phản hồi trước khi validate
- ✅ **Timeout handling:** Tránh test bị treo nếu ECU không phản hồi
- ✅ **Real-time validation:** Kiểm tra response ngay khi nhận được

**Ví dụ:**
```capl
// Gửi command
msgCmd.MHU_BCM_RemoteDoorCtrl = 1;
output(msgCmd);

// Chờ response (timeout 500ms)
int result = TestWaitForMessage(msgStatus, 500);

if (result == 1) {
    // Message received - tiếp tục validate
    TestGetWaitEventMsgData(msgStatus); // Lấy dữ liệu message
    // ... validate ...
} else {
    // Timeout - ECU không phản hồi
    testStepFail("No response from ECU within 500ms");
    return;
}
```

---

#### **`TestGetWaitEventMsgData(message)`**

**Mục đích:** Lấy dữ liệu của message vừa nhận được

**Cú pháp:**
```capl
TestGetWaitEventMsgData(msgStatus);
// Sau đó có thể đọc signals từ msgStatus
if (msgStatus.STAT_DoorLockDriver == 1) {
    // ...
}
```

**Tại sao cần:**
- ✅ **Lấy dữ liệu mới nhất:** Message có thể đã được update trên bus
- ✅ **Validate chính xác:** Đảm bảo validate đúng dữ liệu vừa nhận

**Lưu ý:** Phải gọi `TestGetWaitEventMsgData()` sau khi `TestWaitForMessage()` return 1.

---

### 5.6. Test Report Functions

#### **`TestModuleDescription(description)`**

**Mục đích:** Thêm mô tả cho test module

**Cú pháp:**
```capl
TestModuleDescription("BCM Functional Test Cases - Door Control Module");
```

**Tại sao cần:**
- ✅ **Documentation:** Người đọc report biết test module này test gì
- ✅ **Organization:** Dễ phân loại test modules

---

#### **`TestReportAddEngineerInfo(key, value)`**

**Mục đích:** Thêm thông tin engineer vào test report

**Cú pháp:**
```capl
TestReportAddEngineerInfo("Company", "VinFast.Ltd.");
TestReportAddEngineerInfo("Tester name", "Nguyen Van A");
TestReportAddEngineerInfo("Date", "2024-01-15");
```

**Tại sao cần:**
- ✅ **Traceability:** Biết ai chạy test, khi nào
- ✅ **Compliance:** Một số tiêu chuẩn yêu cầu có thông tin tester
- ✅ **Communication:** Dễ liên hệ khi có vấn đề

---

#### **`TestReportAddSetupInfo(key, value)`**

**Mục đích:** Thêm thông tin về test setup

**Cú pháp:**
```capl
TestReportAddSetupInfo("CANoe", "Version 15.0");
TestReportAddSetupInfo("Hardware", "VN1630");
TestReportAddSetupInfo("DBC Version", "V9.1.0");
```

**Tại sao cần:**
- ✅ **Reproducibility:** Biết version tools để reproduce test
- ✅ **Debugging:** Version mismatch có thể gây lỗi

---

#### **`TestReportAddSUTInfo(key, value)`**

**Mục đích:** Thêm thông tin về System Under Test (ECU được test)

**Cú pháp:**
```capl
TestReportAddSUTInfo("SUT", "BCM ECU");
TestReportAddSUTInfo("Firmware Version", "V2.3.1");
TestReportAddSUTInfo("Hardware Part Number", "BCM-2024-001");
```

**Tại sao cần:**
- ✅ **Traceability:** Biết test trên ECU nào, firmware version nào
- ✅ **Regression:** So sánh kết quả giữa các firmware versions

---

### 5.7. System Variables

**Mục đích:** Điều khiển simulation nodes và test environment

**Cú pháp:**
```capl
@sysvar::namespace::VariableName = value;
```

**Tại sao cần:**
- ✅ **Control simulation:** Điều khiển các node simulation (BCM_RX, BCM_TX)
- ✅ **Test scenarios:** Tạo các kịch bản test (ignition ON/OFF, speed, etc.)
- ✅ **Integration:** Kết nối test module với simulation nodes

**Ví dụ:**
```capl
// Set Ignition ON
@sysvar::testNS::IgnitionStart = @sysvar::testNS::IgnitionStart::Ign_ON;

// Set vehicle speed
@sysvar::testNS::VehicleSpeed = 20; // km/h

// Set lock request
@sysvar::testNS::LockRequest = @sysvar::testNS::LockRequest::RqToLock;
```

**Lưu ý:** System variables phải được định nghĩa trong CANoe Configuration (không phải trong CAPL code).

---

## 6. WORKFLOW THỰC HIỆN TEST

### 6.1. Workflow tổng quan

```
┌─────────────────────────────────────────────────┐
│ 1. Setup Test Environment trong CANoe          │
│    - Tạo Test Environment                        │
│    - Tạo CAPL Test Module                        │
│    - Cấu hình Test Report                        │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 2. Viết Test Module Code                         │
│    - MainTest()                                  │
│    - PreConditions(), PostConditions()           │
│    - Test Cases (TC01, TC02, ...)               │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 3. Compile và Check Errors                       │
│    - CAPL Browser → Compile (F7)                │
│    - Fix errors nếu có                          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 4. Setup Hardware                                │
│    - Kết nối CAN interface vào vehicle          │
│    - Load DBC files                              │
│    - Start measurement                           │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 5. Run Test                                      │
│    - Test tab → Start                           │
│    - Monitor test execution                      │
│    - Xem real-time results                       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 6. Analyze Test Report                           │
│    - Xem pass/fail status                        │
│    - Check test steps                            │
│    - Export report nếu cần                       │
└─────────────────────────────────────────────────┘
```

---

### 6.2. Checklist trước khi chạy test

- [ ] **Test Environment đã được tạo và saved**
- [ ] **CAPL Test Module đã được link đến file .can**
- [ ] **Test Report path đã được cấu hình**
- [ ] **CAPL code đã compile không có errors**
- [ ] **DBC files đã được load vào CANoe**
- [ ] **System Variables đã được định nghĩa**
- [ ] **CAN interface đã kết nối vào vehicle**
- [ ] **Measurement đã được start**
- [ ] **Simulation nodes (BCM_RX, BCM_TX) đã được enable (nếu cần)**

---

### 6.3. Thứ tự thực hiện chi tiết

#### **PHASE 1: Preparation (Chuẩn bị)**

**Step 1.1: Tạo folder structure**
```
Project Root/
├── Test Files/
│   └── BCM_TestModule.can
├── Test Reports/
│   └── (reports sẽ được lưu ở đây)
└── Node/
    └── Body/
        ├── BCM_RX.can
        └── BCM_TX.can
```

**Step 1.2: Mở CANoe và load configuration**
- Mở CANoe
- Load file configuration (.cfg) nếu có
- Hoặc tạo configuration mới

**Step 1.3: Load DBC files**
- Database → Load → Chọn DBC files
- Đảm bảo messages và signals đã được load

**Step 1.4: Setup System Variables (nếu cần)**
- Configuration → System Variables
- Tạo các variables cần thiết (IgnitionStart, VehicleSpeed, LockRequest, etc.)

---

#### **PHASE 2: Test Environment Setup**

**Step 2.1: Tạo Test Environment**
- Test tab → Test Setup → Test Modules
- Right-click → New Test Environment
- Đặt tên: `te_BCM_FunctionalTests`
- Save vào folder `Test Files`

**Step 2.2: Tạo CAPL Test Module**
- Right-click Test Environment → Insert CAPL Test Module
- Configuration → Đặt tên: `tm_BCM_Tests`
- File → Link đến `BCM_TestModule.can`
- OK

**Step 2.3: Cấu hình Test Report**
- Right-click Test Module → Configuration
- Tab Test Report → Browse đến folder `Test Reports`
- OK

**Step 2.4: Mở CAPL Browser**
- Right-click Test Module → Edit
- CAPL Browser mở với file `BCM_TestModule.can`

---

#### **PHASE 3: Code Implementation**

**Step 3.1: Viết MainTest()**
```capl
void MainTest() {
    cf_testPreparation();
    TC01_BasicLockUnlock();
    // Thêm các test cases khác
}
```

**Step 3.2: Viết Test Preparation**
```capl
void cf_testPreparation() {
    TestModuleDescription("BCM Functional Tests");
    TestReportAddEngineerInfo("Company", "VinFast");
    TestReportAddSUTInfo("SUT", "BCM ECU");
}
```

**Step 3.3: Viết PreConditions() và PostConditions()**
```capl
testfunction PreConditions() {
    // Setup code
}

testfunction PostConditions() {
    // Cleanup code
}
```

**Step 3.4: Viết Test Cases**
```capl
testcase TC01_BasicLockUnlock() {
    // Test logic
}
```

**Step 3.5: Compile**
- CAPL Browser → Compile (F7)
- Fix errors nếu có
- Đảm bảo compile thành công

---

#### **PHASE 4: Hardware Setup**

**Step 4.1: Kết nối CAN interface**
- Cắm Vector interface (VN1630, VN5610, etc.) vào PC
- Kết nối vào OBD-II connector của vehicle
- Hoặc breakout vào bus cần test (BD, PT, CH, IF)

**Step 4.2: Configure CAN channels trong CANoe**
- Hardware → Network Hardware
- Chọn interface và channel tương ứng
- Set baudrate (thường 500kbps cho CAN)

**Step 4.3: Enable Simulation Nodes (nếu cần)**
- Simulation Setup → Enable các nodes:
  - BCM_RX.can
  - BCM_TX.can

---

#### **PHASE 5: Run Test**

**Step 5.1: Start Measurement**
- Measurement → Start (F9)
- Đảm bảo CAN traffic đang được capture

**Step 5.2: Run Test**
- Test tab → Test Setup
- Chọn Test Module cần chạy
- Click **Start** (hoặc F5)
- Monitor test execution trong Test Report Window

**Step 5.3: Monitor Results**
- Xem real-time pass/fail status
- Check test steps đang chạy
- Nếu có lỗi, pause và check logs

---

#### **PHASE 6: Analyze Results**

**Step 6.1: Xem Test Report**
- Test Report Window hiển thị:
  - Tổng số test cases: passed/failed
  - Chi tiết từng test step
  - Timestamps
  - Error messages (nếu có)

**Step 6.2: Export Report (nếu cần)**
- Right-click Test Report → Export
- Chọn format (HTML, PDF, XML)
- Save vào folder `Test Reports`

**Step 6.3: Debug nếu có failures**
- Xem trace window để check CAN messages
- Check system variables values
- Review test logic trong CAPL code
- Fix và chạy lại

---

## 7. BEST PRACTICES

### 7.1. Naming Conventions

- **Test Environment:** `te_<Module>_<Type>` (ví dụ: `te_BCM_Functional`)
- **Test Module:** `tm_<Module>_<Type>` (ví dụ: `tm_BCM_Functional`)
- **Test Cases:** `TC<Number>_<Description>` (ví dụ: `TC01_BasicLockUnlock`)
- **Test Steps:** Mô tả rõ ràng, ngắn gọn

### 7.2. Code Organization

- **Mỗi test case độc lập:** Không phụ thuộc vào test case khác
- **PreConditions/PostConditions:** Luôn reset về trạng thái ban đầu
- **Timeout values:** Đặt timeout hợp lý (không quá ngắn, không quá dài)
- **Error handling:** Luôn check return values của `TestWaitForMessage()`

### 7.3. Test Report

- **Thông tin đầy đủ:** Company, tester name, SUT info, setup info
- **Mô tả rõ ràng:** Test steps có mô tả dễ hiểu
- **Screenshots:** Có thể thêm screenshots vào report nếu cần

---

## 8. TROUBLESHOOTING

### 8.1. Test không chạy

**Nguyên nhân:**
- Test Module chưa được link đến file .can
- CAPL code có compile errors
- Test Environment chưa được saved

**Giải pháp:**
- Check Configuration của Test Module
- Compile lại CAPL code và fix errors
- Save Test Environment

---

### 8.2. Không nhận được messages

**Nguyên nhân:**
- CAN interface chưa kết nối
- Measurement chưa start
- Wrong message ID hoặc bus
- ECU không phản hồi

**Giải pháp:**
- Check hardware connection
- Start measurement
- Verify message ID và bus trong DBC
- Check ECU có đang hoạt động không

---

### 8.3. Test luôn fail

**Nguyên nhân:**
- Timeout quá ngắn
- Validation logic sai
- ECU behavior khác với expected

**Giải pháp:**
- Tăng timeout
- Review validation logic
- Check ECU specification

---

## 9. TÓM TẮT

### 9.1. Các bước quan trọng nhất

1. ✅ **Tạo Test Environment** → Container cho test modules
2. ✅ **Tạo CAPL Test Module** → File chứa test logic
3. ✅ **Cấu hình Test Report** → Nơi lưu kết quả
4. ✅ **Viết code** → MainTest(), PreConditions(), PostConditions(), Test Cases
5. ✅ **Compile** → Check errors
6. ✅ **Run Test** → Execute và xem kết quả

### 9.2. Tại sao cần từng phần

| **Phần** | **Tại sao cần** |
|---------|----------------|
| **Test Environment** | Tổ chức, quản lý test modules |
| **Test Module** | Chứa test logic, compile và execute |
| **MainTest()** | Điều khiển flow, thứ tự test cases |
| **PreConditions()** | Đảm bảo môi trường sẵn sàng |
| **PostConditions()** | Reset về trạng thái ban đầu |
| **Test Cases** | Mỗi test case độc lập, dễ maintain |
| **Test Report** | Documentation, traceability |

---

## 10. TÀI LIỆU THAM KHẢO

- [Vector CANoe Documentation](https://www.vector.com/en/products/products-a-z/software/canoe/)
- [CAPL Programming Guide](https://www.vector.com/en/products/products-a-z/software/capl/)
- [Testing with CANoe PDF](https://robertscaplblog.wordpress.com/wp-content/uploads/2016/02/an-ind-1-002_testing_with_canoe.pdf)

---

**Tác giả:** Generated based on Vector CANoe Testing Guide  
**Ngày:** 2024  
**Version:** 1.0

