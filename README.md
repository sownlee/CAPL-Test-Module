# Testing Tutorial with CANoe - CAPL Test Module

## Table of Contents
1. [Overview of CANoe Testing]
2. [Test Module Structure]
3. [Step-by-Step Guide]
4. [Real-Life Examples from Project]
5. [Best Practices]
### 1.1 What is CANoe Testing Feature Suite?

CANoe Testing Feature Suite is a set of tools built into CANoe that helps you:
- **Create and execute test cases** in a structured way
- **Automatically generate test reports** (test result reports)
- **Manage test cases** by group and module
- **Integrate with Test Management Systems**

###1.2 Test System Architecture
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

variables {
    msTimer testTimer;
}

// Test Module
on start {
    // init test environment
    InitializeTestEnvironment();
    
    // Test Group: Safety Features
    setTestGroup("Safety_Features");
    
    // Test Cases
    DoorLockTest();
    WindowSafetyTest();
    AirbagTest();
    
    // Test Group: Comfort Features
    setTestGroup("Comfort_Features");
    
    // Test Cases
    ClimateControlTest();
    AutoLightTest();
    
    // Cleanup
    CleanupTestEnvironment();
}

testcase DoorLockTest() {
    testStep("Check basic lock function");
    @sysvar::LockRequest = LOCK;
    testWaitForTimeout(500);
    
    if (@sysvar::LockState != LOCKED) {
        testStepFail("Door lock failed");
        return;
    }
    
    testStep("Check speed-dependent auto lock");
    @sysvar::VehicleSpeed = 20;
    testWaitForTimeout(1000);
    
    if (@sysvar::LockState != LOCKED) {
        testStepFail("Auto lock at speed failed");
    }
}
*/                            
CANoe has a built-in testing feature where test cases may be implemented in CAPL language. With CAPL, test cases will be executed in the order in which they are written in the “MainTest()” test control. Also, it is important to note that the functionality of a test module CAPL program is not quite the same as that of a regular CAPL program written to simulate a network node. 

1.1.1 Configuration 
Let’s begin by setting up the test environment in CANoe. 
1) Open the Test Setup by going to the Test ribbon and selecting Test Setup in the Test Modules group. 
2) Right-click in the blank area and select New Test Environment. Enter the name as “te_FunctionalTests”. Right-click on this environment and click Save. Navigate to the sub-folder “Test 
Files” and click [Save]. 
3) Right-click on this new folder and select Insert CAPL Test Module. 
4) Right-click on this new test module and click on Configuration. Enter the name as “tm_FunctionalTests”. Click on File, navigate to the “Test Files” sub-folder and enter the name as “CANoeTests.can”. Click [Open] and click [OK]. 
5) Again right-click on the test module and click Configuration. Under the Test Report tab, add the path of the sub-folder “Test Reports” in the Test reports path. Click [OK]. 
6) Again right-click on the test module and click Edit. This will open the CAPL browser.
7) Note: The CAPL Browser is a tool that comes with the CANoe installation. Typically, this browser is used to implement a CAPL program to simulate a network node, but it is possible to use it to implement test cases for a test module.
   
1.2.2 Creating the Test Module 
The CAPL view for a test module is different than the CAPL view for a network node. There are three new event types, “Test Functions”, “Test Cases” and “Test Control”. The “Test Control” event drives which and 
when each test case should be executed. The test cases are defined in the “Test Cases” event type. We will need to create one function for setting the details of the test module, 2 testfunctions for Pre and Post conditions and 3 test cases as per the test design mentioned in the Appendix. 
2.1 Implementation in CANoe
• Output of a message to the ECU under test (Stimulus). 
• Waiting for the ECU’s response. 
• Evaluation of the response if necessary.

on key 't' {
    message SeatSensorLeftRequest msgLeftRequest;
    message SeatSensorRightRequest msgRightRequest;
    
    // TESTER ---> SUT output (stimulus)
    output(msgLeftRequest);
    output(msgRightRequest);
    
    // TESTER <--- SUT if (1 = TestWaitForMessage(SeatSensorLeftResponse, 1000))
    if (!TestWaitForMessage(SeatSensorLeftResponse, 1000)) {
        TestStepFail("Response message left not received within 1000ms");
        return;  // cancel test case
    }
    
    TestStepPass("Both responses received on time");
}
