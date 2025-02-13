Overview
This repository hosts the "CANoe Test Feature Set Tutorial," a comprehensive guide designed to demonstrate the setup, simulation, and testing of Electronic Control Units (ECUs) using CANoe and vTESTstudio. The tutorial specifically focuses on simulating the Doors ECU as the System Under Test (SUT) within a CAN network environment.
Purpose
The tutorial aims to equip automotive engineers and testers with the necessary skills to:
Develop and manage a CAN database.
Simulate ECUs and their interactions within a CAN network.
Create, manage, and execute test cases using both CAPL and C# in vTESTstudio.
Analyze test results effectively using CANoe's testing and simulation tools.
Tutorial Content
The tutorial is structured into several key sections, each designed to build upon the previous to provide a thorough understanding of CANoe's and vTESTstudio's capabilities:
1. Introduction to the Tutorial:
An overview of the tutorial's goals and the simulated network setup.
Details on the ECUs involved: Engine, Console, and Doors ECUs.
Setup Instructions:
Steps to create a new directory structure for managing the tutorial files.
Instructions on setting up CANoe configurations and creating a new CAN database.
ECU Simulation:
Guidance on simulating the Doors ECU and the remaining bus required for the simulation.
Configuration of messages and signals within the CAN database.
4. Creating and Managing Test Cases:
Detailed instructions on using vTESTstudio to create test cases in CAPL, C#, Test Table, and Test Sequence Diagram.
Steps to configure and execute tests within CANoe.
5. Testing and Results Analysis:
Explanation of how to execute tests and monitor them in real-time using CANoe.
Guidelines on generating and interpreting test reports.
6. Appendices:
Additional technical details on network setup, ECU design, and specific CAN requirements.
Getting Started
To begin with this tutorial:
1. Clone this repository to your local environment.
2. Install CANoe and vTESTstudio, ideally version 15.0 for CANoe and version 5.0 for vTESTstudio, as used in this tutorial.
3. Navigate to the docs directory and sequentially follow the tutorials starting from the setup instructions.
Resources
This repository includes:
docs/: Detailed documentation and step-by-step guides for each section of the tutorial.
examples/: Example configuration files and scripts that can be directly used or modified for testing.
scripts/: Sample scripts in CAPL and C# demonstrating how to write effective test cases.
