We are creating a framework for developing software with Claude. It is modeled after Ralph. However it is not an automated loop. The user must issue a claude / command to move to the next step. Steps such as converting a high level requirement into a feature list. Allowing the user to correct and refine that with the help of claude until it is good.

The framework will be written in python and over time will be tuned for ROS2. But initially the features will be very general.

The framework will take the form of a directory with nested directories, containing standard and user supplies elements. It will be designed so that someone could use it as a starting point for a new project. It will contain code and configurations and instructions. All configurations and settings will be in the form of yaml files.

The framework will setup claude with a number of / commands. Each one will do a discrete step and call claude code once. This is different from Ralph.

There will also be an install shell script.

This directory contains the code that we are developing. Each time we reach a milestone you will copy all the files from this folder into a brand new folder so I can play with it and test it as if it was complete.
