## Stored variables:
### Positions 
- **currentSpinPosJ**
- **homePosition**
- **spinHomePos**

## Calls available:
### Sample
- `getSamPosOffset;`<br />
  Return the current x, y offset applied to the **homePosition** required to align the gripper over the selected sample number. x & y are 0-based integers defining the column and row indices of the sample board grid.
- `setSamPosOffset:#x[num]#y[num];`<br />
  Change the offset x, y offset applied to the **homePosition** required to align the gripper over the selected sample number. Only two dimensions are required as the sample holder is two dimensional with a constant height (z).

### Positions
- `getCurrentPosition;`<br />
  Return the current position of the gripper: the x, y, z, rx, ry, rz equivalent of the joint configuration of the arm at the time of this call.
- `getNearestPosition;`<br />
  Using the current position of the robot, determine the nearest stored position (e.g. **homePosition**, **gatePosition**, etc.) and the displacement of the arm at this moment from that position.
- `getSpinHomePosition;`<br />
  Return the x, y, z, rx, ry, rz equivalent of **spinnerHomePos**, the joint configuration of the arm at the 'spinner home' position (equivalent of the **homePosition** above the sample board).
- `getSpinPosition;`<br />
  Return the x, y, z, rx, ry, rz equivalent of **currentSpinPosJ**, the joint configuration of the arm at the currently defined spinner position.
- `getSpinPosOffset;`<br />
  Return the x, y, z, rx, ry, rz offset applied to **spinHomePos** required to reach **currentSpinPosJ**.
- `setSpinPosOffset:#x[num]#y[num]#z[num]`;<br />
  Apply a new x, y, z offset to the **spinHomePos** position. It is not necessary (or possible) to apply a rotational offset as the orientation of the spinner does not change with time.

