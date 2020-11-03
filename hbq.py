import numpy as np
import time

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0


class AI(object):
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []
        self.list_candidate = []
        self.time_start = 0
        self.time_buffer = 0.02
        self.TIMEOUT = False
        self.directions = [[0, 1], [0, -1], [1, 0], [-1, 0], [-1, 1], [-1, -1], [1, 1], [1, -1]]
        self.valueboard = np.array([[1000, -25, 20, 10, 10, 20, -25, 1000],
                                    [-25, -50, 1, 1, 1, 1, -50, -25],
                                    [20, 1, 3, 2, 2, 3, 1, 20],
                                    [10, 1, 2, 1, 1, 2, 1, 10],
                                    [10, 1, 2, 1, 1, 2, 1, 10],
                                    [20, 1, 3, 2, 2, 3, 1, 20],
                                    [-25, -50, 1, 1, 1, 1, -50, -25],
                                    [1000, -25, 20, 10, 10, 20, -25, 1000]])

    def is_Valid(self, x, y, chessboard, color) -> bool:
        for xd, yd in self.directions:
            x1 = x
            y1 = y
            while self.on_Board(x1 + xd, y1 + yd) and chessboard[x1 + xd, y1 + yd] == -1 * color:
                x1 += xd
                y1 += yd
            if self.on_Board(x1 + xd, y1 + yd) and chessboard[x1 + xd, y1 + yd] == color and (x1 != x or y1 != y):
                return True
        return False

    def get_flip_points(self, x, y, chessboard, color) -> list:
        all_point = []
        for xd, yd in self.directions:
            flip_point = []
            x1 = x
            y1 = y

            while self.on_Board(x1 + xd, y1 + yd) and chessboard[x1 + xd, y1 + yd] == -1 * color:
                x1 += xd
                y1 += yd
                flip_point.append((x1, y1))

            if not (self.on_Board(x1 + xd, y1 + yd) and chessboard[x1 + xd, y1 + yd] == color and (x1 != x or y1 != y)):
                flip_point = []

            all_point.extend(flip_point)
        return all_point

    def on_Board(self, x, y) -> bool:
        return 0 <= x < self.chessboard_size and 0 <= y < self.chessboard_size

    def turn_color(self, point_list, board1) -> np.array:
        for point in point_list:
            board1[point[0]][point[1]] *= -1
        return board1

    def move(self, point, color, board) -> np.array:
        board = self.turn_color(self.get_flip_points(point[0], point[1], board, color), board)
        board[point[0]][point[1]] = color
        return board

    def unmove(self, board, flip_list, x, y, color) -> np.array:
        for point in flip_list:
            board[point[0]][point[1]] = color * -1
        board[x][y] = COLOR_NONE
        return board

    def min(self, search_depth, board, alpha, beta) -> int:
        if self.TIMEOUT or time.time() - self.time_start > self.time_out - self.time_buffer:
            self.TIMEOUT = True
            return beta

        if search_depth <= 0:
            return self.value(board)

        points1 = []
        points2 = []
        space_chess = np.where(board == COLOR_NONE)
        space_chess = list(zip(space_chess[0], space_chess[1]))
        for point in space_chess:
            if self.is_Valid(point[0], point[1], board, self.color * -1):
                points1.append(point)

        if not points1:
            for point in space_chess:
                if self.is_Valid(point[0], point[1], board, self.color):
                    points2.append(point)
            if not points2:
                return self.winlosevalue(board)
            return self.max(search_depth, board, alpha, beta)

        for point in points1:
            fl = self.get_flip_points(point[0], point[1], board, self.color * -1)
            board = self.turn_color(fl, board)
            board[point[0]][point[1]] = self.color * -1
            beta = min(beta, self.max(search_depth - 1, board, alpha, beta))
            board = self.unmove(board, fl, point[0], point[1], self.color * -1)

            if beta <= alpha or self.TIMEOUT:
                break

        return beta

    def max(self, search_depth, board, alpha, beta) -> int:
        if self.TIMEOUT or time.time() - self.time_start > self.time_out - self.time_buffer:
            self.TIMEOUT = True
            return alpha

        if search_depth <= 0:
            return self.value(board)

        points1 = []
        points2 = []
        space_chess = np.where(board == COLOR_NONE)
        space_chess = list(zip(space_chess[0], space_chess[1]))
        for point in space_chess:
            if self.is_Valid(point[0], point[1], board, self.color):
                points1.append(point)

        if not points1:
            for point in space_chess:
                if self.is_Valid(point[0], point[1], board, self.color * -1):
                    points2.append(point)
            if not points2:
                return self.winlosevalue(board)
            return self.min(search_depth, board, alpha, beta)

        for point in points1:
            fl = self.get_flip_points(point[0], point[1], board, self.color)
            board = self.turn_color(fl, board)
            board[point[0]][point[1]] = self.color
            alpha = max(alpha, self.min(search_depth - 1, board, alpha, beta))
            board = self.unmove(board, fl, point[0], point[1], self.color)

            if beta <= alpha or self.TIMEOUT:
                break

        return alpha

    def minmax(self, search_depth, board) -> (int, int):
        alpha = float("-inf")
        beta = float("inf")
        best_move = None
        for point in self.list_candidate:
            fl = self.get_flip_points(point[0], point[1], board, self.color)
            board = self.turn_color(fl, board)
            board[point[0]][point[1]] = self.color
            val = self.min(search_depth - 1, board, alpha, beta)
            board = self.unmove(board, fl, point[0], point[1], self.color)

            if val > alpha:
                alpha = val
                best_move = point

            if self.TIMEOUT:
                return ()
        return best_move

    def value(self, board) -> int:
        counter1 = 0
        counter2 = 0
        counter3 = 0
        sc = 0
        space_chess = np.where(board == COLOR_NONE)
        space_chess = list(zip(space_chess[0], space_chess[1]))
        chessn = 64 - len(space_chess)
        for point in space_chess:
            if self.is_Valid(point[0], point[1], board, self.color):
                counter1 += 1
            if self.is_Valid(point[0], point[1], board, self.color * -1):
                counter2 += 1

        if chessn < 25:
            mc = 300
        else:
            mc = 100

        if chessn > 20:
            for cc in [[(0, 0), (0, 1)], [(0, 0), (1, 0)], [(self.chessboard_size - 1, 0), (-1, 0)],
                       [(self.chessboard_size - 1, 0), (0, 1)], [(0, self.chessboard_size - 1), (0, -1)],
                       [(0, self.chessboard_size - 1), (1, 0)],
                       [(self.chessboard_size - 1, self.chessboard_size - 1), (-1, 0)],
                       [(self.chessboard_size - 1, self.chessboard_size - 1), (-1, -1)]]:
                corner = cc[0]
                x = corner[0]
                y = corner[1]
                dire = cc[1]
                xd = dire[0]
                yd = dire[1]
                if board[x][y] == self.color:
                    while self.on_Board(x + xd, y + yd) and board[x + xd][y + yd] == self.color:
                        counter3 += 1
                        x = x + xd
                        y = y + yd

        return sum(sum(board * self.valueboard)) * self.color + (counter1 - counter2) / (counter1 + counter2 + 2) * mc + counter3 * sc

    def winlosevalue(self, board) -> int:
        return sum(sum(board)) * self.color * 100000

    def go(self, chessboard):
        self.time_start = time.time()
        self.candidate_list.clear()
        # ==============================================================================================================
        # initialization

        space_chess = np.where(chessboard == COLOR_NONE)
        space_chess = list(zip(space_chess[0], space_chess[1]))

        for point in space_chess:
            if self.is_Valid(point[0], point[1], chessboard, self.color):
                self.candidate_list.append(point)

        self.list_candidate = self.candidate_list[:]

        # ==============================================================================================================
        # algorithm:minmax && alpha beta && iterative deepening search

        self.TIMEOUT = False
        for search_depth in [2, 3, 4, 5, 6, 8, 10, 12]:
            best_move = self.minmax(search_depth, chessboard)
            if not self.TIMEOUT and best_move:
                self.candidate_list.append(best_move)
            if self.TIMEOUT:
                break
