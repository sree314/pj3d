import math

class Rotation3D:
    def __init__(self, rotx = 0, roty = 0, rotz = 0):
        self.rotx = rotx
        self.roty = roty
        self.rotz = rotz

    def _get_matrix(self, rot_deg, axis):
        cosT = round(math.cos(rot_deg * math.pi / 180.0), 6)
        sinT = round(math.sin(rot_deg * math.pi / 180.0), 6)

        matrix = [[1,   0,  0],
                  [0, cosT, -sinT],
                  [0, sinT, cosT]]

        rot = [0, 1, 2]
        shiftamt = 3 - axis
        rot = rot[shiftamt:3] + rot[:shiftamt]

        omatrix = [matrix[rot[i]] for i in range(3)]
        for i in range(len(omatrix)):
            omatrix[i] = [omatrix[i][rot[j]] for j in range(3)]

        return omatrix

    def _mm(self, a, b):
        c = [[0.0]*3, [0.0]*3, [0.0]*3]

        for i in range(3):
            for j in range(3):
                for k in range(3):
                    c[i][j] += a[i][k] * b[k][j]

        return c

    def matrix(self):
        rotx = self._get_matrix(self.rotx, 0)
        roty = self._get_matrix(self.roty, 1)
        rotz = self._get_matrix(self.rotz, 2)

        return self._mm(rotz, self._mm(roty, rotx))


if __name__ == "__main__":
    r = Rotation3D(0, 0, 0)

    print(r._get_matrix(90, 0))
    print(r._get_matrix(90, 1))
    print(r._get_matrix(90, 2))

    print(r.matrix())
