import matplotlib.pyplot as plt
import scipy.sparse as sparse
import scipy.sparse.linalg
from math import ceil
import numpy as np


class HeatEquationSolver:
    def __init__(self, u_0_func: callable,
                 t_final=0.1,
                 a: int = 0,
                 b: int = 1,
                 t_a: float = 0,
                 t_b: float = 0,
                 n_x_points: int = 100):
        self.T_a = t_a
        self.T_b = t_b
        self.mu = 1 / 4  # By design.
        self.c = 1
        self.dx = 1 / n_x_points
        self.dt = self.dx ** 2 / (4 * self.c)

        self.n_x_points = n_x_points
        self.n_t_points = ceil(t_final / self.dt)

        self.x = np.linspace(a, b, self.n_x_points)
        self.t = np.arange(0, t_final, self.dt)
        self.u_0 = np.reshape(u_0_func(self.x), (100, 1))
        self.data = [self.u_0]
        self.result = None

    def create_main_matrix(self):
        tri_diag = np.ones((3, self.n_x_points))
        tri_diag[1] = -2 * tri_diag[1]
        # tri_diag[2, 1] = 0
        # tri_diag[1, 0] = 1/self.mu
        # tri_diag[0, -2] = 0
        # tri_diag[1, -1] = 1/self.mu
        a_matrix = sparse.spdiags(tri_diag, [-1, 0, 1], self.n_x_points, self.n_x_points) * self.mu
        # Setting the top and bottom entries to just reflect.

        i_matrix = sparse.identity(self.n_x_points)
        return a_matrix, i_matrix

    def solve(self):
        u = self.u_0

        for i in range(self.n_t_points):
            D2, I = self.create_main_matrix()
            lhs = (I - D2 / 2)
            rhs = (I + D2 / 2) * u
            # rhs[1] += self.mu / 2 * self.T_a
            # rhs[-2] += self.mu / 2 * self.T_b

            # Setting the BCs:
            u[0] = self.T_a
            u[-1] = self.T_b

            u = np.transpose(np.mat(sparse.linalg.spsolve(lhs, rhs)))

            self.data.append(np.copy(u))
            if (i % 1000) == 0:
                print(".", end="")

        self.result = np.hstack(self.data)

        return self.result

    def plot(self):
        X, Y = np.meshgrid(self.x, self.t)
        fig = plt.figure()
        ax = plt.axes(projection='3d')

        # Creating plot
        ax.plot_surface(X, Y, self.result[:, :-1].T)
        ax.set_xlabel("X [m]")
        ax.set_ylabel("T [s]")
        plt.show()


def initial_value(x):
    return 6 * np.sin(np.pi * x) + (20 + x * 10)


solver = HeatEquationSolver(u_0_func=initial_value, t_a=20, t_b=30)
res = solver.solve()
solver.plot()
