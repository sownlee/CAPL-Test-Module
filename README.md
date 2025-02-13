1.1 Test Units and Test Modules 
There are two types of Test Setups in CANoe. The Test Units Test Setup is used for executing the test cases created using vTESTstudio and the Test Modules Test Setup is used for executing the test cases 
created in CANoe environment. 

1.2 Testing in CANoe 
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
