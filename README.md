# EMAControl

[![Build Status](https://travis-ci.com/mtwharmby/emacontrol.svg?branch=master)](https://travis-ci.com/mtwharmby/emacontrol)

EMAControl provides a user interface with which to control the robotic sample changer available at beameline P02.1.

Specifically it provides:

* A class which allows commands to be sent to the robot
* A series of functions which instruct the robot to perform actions (e.g. samples changes)

The functions are based on a set of calls developed by Mario Wendt and Michael Wharmby, which cover the needs of beamline users and staff to use the robot to mount a sample, measure a diffraction pattern (using other supporting libraries) an then transfer the sample back to the sample magazines. The functions work by sending string messages through a socket to the robot control server, where these messages are then interpretted and the appropriate VAL3 function called.
The following is a list of the possible string commands which may be sent through the socket to the controller:
- setAxis - (?)
- next - move to next sample
- current - (?)
- gate - go to gate position (between magazines and diffractometer)
- home - go to home position (above the magazines)
- homing - (?)
- spinner - go to spinner position
- offside - go to offside position (at diffractometer, away from spinner)
- zero - go to zero position (?)
- pick - pick sample (?)
- release - open gripper (!)
- open - open gripper (!)
- close - close gripper
- powerOn - switch motor power on
- interrupt - interrupt a motion (? does this do anything?)
- restart - restart motion after interruption (? does this do anything?)
- powerOff - switch motor power off
- setSAM - (?)
