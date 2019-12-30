from emacontrol.emacfg import CoordsXYZ, diffr_pos_to_xyz


def test_diffr_pos_to_xyz():
    assert diffr_pos_to_xyz(0, 0, 0, 0, 0, 0) == (0.0, 0.0, 0.0)

    # @ om = 0: z along beam, x outboard (//diffh), y upward (// diffv)
    # om (assumed and defaulted to) clockwise when facing diffractometer
    samx = 4.0
    samy = 1.0
    samz = 2.0
    om = 0.0
    diffh = 3.0
    diffv = 5.0

    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, samy + diffv, samz)

    om = 90.0  # x outboard (// diffh); y // -z0; z // y0 (//diffv);
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, samz + diffv, -samy)

    om = 180.0  # x outboard (// diffh); y // -y0; z // -z0
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, -samy + diffv, -samz)

    om = 270.0  # x outboard (// diffh); y // z0; z // -y0
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, -samz + diffv, samy)

    om = 120  # z slightly down and downstream; x up and downstream
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(7.0, 6.232, -1.866)


def test_diffr_pos_to_xyz_CCW():
    # Same as test above, but now checking that the counterclockwise rotation
    # is correctly calculated.

    # @ om = 0: z along beam, x outboard (//diffh), y upward (// diffv)
    # om (assumed and defaulted to) clockwise when facing diffractometer.
    # Opposite sense of rotation used by setting the last argument,
    # rotate_sense, to -1
    samx = 4.0
    samy = 1.0
    samz = 2.0
    om = 0.0
    diffh = 3.0
    diffv = 5.0

    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, samy + diffv, samz)

    om = 90.0  # x outboard (// diffh); y // -z0; z // y0 (//diffv);
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, -samz + diffv, samy)

    om = 180.0  # x outboard (// diffh); y // -y0; z // -z0
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, -samy + diffv, -samz)

    om = 270.0  # x outboard (// diffh); y // z0; z // -y0
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, samz + diffv, -samy)

    om = 120  # z slightly down and downstream; x up and downstream
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(7.0, 2.768, -0.134)
