    def set_sample_mounted(self, state):
        # TODO Docstring
        if state is True:
            self.send('sampleMounted;', wait_for='sampleMounted:done;')
        else:
            self.send('sampleUnmounted;', wait_for='sampleUnmounted:done;')

    def get_spin_position_offset(self):
        """
        Reads and returns the offset (trsf.{x,y,z} in VAL3) which has been
        applied to the SpinHomePosition to set the current currentSpinPosJ of
        the robot.

        Returns
        -------
        coords : tuple
        x, y, z offset in mm.
        """
        spin_offset = self.send('getSpinPosOffset;')
        return Robot._parse_state(spin_offset, ['X', 'Y', 'Z'])

    def set_spin_position_offset(self, spin_x, spin_y, spin_z, verbose=False):
        """
        Sends new x, y and z offsets to be applied to the SpinHomePosition of
        the robot to yield the new currentSpinPosJ. These values should be
        calculated from the goniometer head encoder positions.

        Parameters
        ----------
        spin_x, spin_y, spin_z : float
        New offsets in three dimensions for the spinner in mm
        """
        if verbose:
            print('Spinner coords: ({}, {}, {})'.format(spin_x, spin_y,
                                                        spin_z))
        self.send(('setSpinPosOffset:'
                   + '#X{0:.3f}#Y{1:.3f}#Z{2:.3f};'.format(spin_x, spin_y,
                                                           spin_z)),
                  wait_for='setSpinPosOffset:done;')
                  
def get_spin_home_position(self):
        """
        Reads the SpinHomePosition, i.e. the position where the robot was last
        calibrated against the goniometer head. This is the position which
        offsets are applied to.

        Returns
        -------
        spin_home_pos : dict
        A six-member dictionary containing the translations (3x in mm) and
        rotations (3x in degrees) of the spinner home position.
        """
        spin_home = self.send('getSpinHomePosition;')
        return Robot._parse_state(spin_home, ['X', 'Y', 'Z', 'RX', 'RY', 'RZ'])

def get_spin_position(self):
        """
        Reads the current spinner position (i.e. SpinHomePosition + offset =
        currentSpinPosJ in VAL3). The returned values are absolute in the
        robot reference frame.

        Returns
        -------
        current_spin_pos : dict
        A six-member dictionary containing the translations (3x in mm) and
        rotations (3x in degrees) of the spinner position.
        """
        spin_pos = self.send('getSpinPosition;')
        return Robot._parse_state(spin_pos, ['X', 'Y', 'Z', 'RX', 'RY', 'RZ'])

    def get_diffr_origin_calib(self):
        # TODO docstring
        diffr_origin = self.send('getDiffOrigin;')
        return Robot._parse_state(diffr_origin, None, to_coordsxyz=True)

    def get_diffr_pos_calib(self):
        # TODO docstring
        diffr_pos_calib = self.send('getDiffRel;')
        return Robot._parse_state(diffr_pos_calib, None, to_coordsxyz=True)

    def get_gripper_coords(self):
        """
        Gets the current location of the gripper and returns the x, y, z
        coordinates.

        Returns
        -------
        coords : tuple
        x, y, z coordinates of the gripper in mm.
        """
        # FIXME If we can just return the gripper coords rather than the
        # spinner, we don't actually have to store the position of the gripper
        # as the "spinner position". We just have to move the gripper to the
        # right place.
        return self.get_spinner_coords()



    @staticmethod  # FIXME Rather than to_coords, create a separate method
    def _parse_state(response, keys, to_coordsxyz=False):  # TODO Rename
        """
        Extracts only the requested keys from the state inside the given
        Response object. These are returned as a dictionary of lowercase keys
        and their values.

        Parameters
        ----------
        response : Response
        Object containing state to be extracted.

        keys : list
        String names of items to be returned

        to_coordsxyz : bool (default: False)
        Returns a CoordsXYZ object. In this case the value of keys is ignored.

        Returns
        -------
        selected_keys : dict
        Dictionary with specified lowercase key names and their associated
        values.
        """
        if to_coordsxyz:
            state = Robot._parse_state(response, ['X', 'Y', 'Z'])
            return CoordsXYZ(x=state['x'], y=state['y'], z=state['z'])
        return {key.lower(): response.state[key] for key in keys}