# Testing Tutorial with CANoe - CAPL Test Module

## Table of Contents
1. [Overview of CANoe Testing]
2. [Test Module Structure]
### 1.1 What is CANoe Testing Feature Suite?

CANoe Testing Feature Suite is a set of tools built into CANoe that helps you:
- **Create and execute test cases** in a structured way
- **Automatically generate test reports** (test result reports)
- **Manage test cases** by group and module
- **Integrate with Test Management Systems**

### 1.2 Test System Architecture
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
<img width="406" height="286" alt="image" src="https://github.com/user-attachments/assets/ba5ecd3b-0a36-4927-901d-c98c9bdab419" />

### 2.2 Verdicts (Test Results)

Each test step and test case can have the following results:
- **PASS** ✅ - Test successful
- **FAIL** ❌ - Test failed
- **INCONCLUSIVE** ⚠️ - Result not determined
- **NONE** - No result yet
![image](https://github.com/user-attachments/assets/c5b15267-8514-4d65-91e1-60686a989ed3)

### Step 4: Write Test Case

**Purpose:** Test a specific function of the ECU

**Basic structure:**

```capl
testcase NameTestCase()
{
// 1. Name the test case
TestCaseTitle("Group", "Test name");

// 2. Prepare the environment
PreConditions();

// 3. Test steps
testStep("", "Step description");
// ... execute the test ...

// 4. Clean up
PostConditions();
}
```                           
**Detailed explanation:**

#### 4.1 Message Declaration
```capl
message GW_BCM_DoorSts_0x3D0 LockingStatus;
```
- **Action:** Create a variable to receive data from CAN message
- **This message:** Reports the door lock status from BCM (Body Control Module)

#### 4.2 TestCaseTitle()
```capl
TestCaseTitle("Locking Test", "Request to Lock");
```
- **Parameter 1:** Test group (displayed in report)
- **Parameter 2:** Specific test case name
- **Action:** Create title in test report

#### 4.3 Stimulating ECU (Stimulus)
```capl
@sysvar::testNS::LockRq = @sysvar::testNS::LockRq::RqToUnlock;
```
- **Action:** Send unlock request to ECU
- **System Variable:** Defined in CANoe database (.dbc/.ini)
