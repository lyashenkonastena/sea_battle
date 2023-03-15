from random import randint

# Исключения
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

# Точки на поле, координаты  x и y
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # для сравнения точек, other - второй объект
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # вывод точек
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

# Класс корабля
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o  # ориентация корабля 0 - верт, 1 гор.
        self.lives = l

    # Метод возвращает список всех точек корабля
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    # Проверяем попали в корабль?
    def shooten(self, shot):
        return shot in self.dots

# Игровое поле
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size

        # скрывать корабли?
        self.hid = hid
        # кол-во пораженных кораблей
        self.count = 0

        # Состояние доски
        self.field = [["O"] * size for _ in range(size)]

        # Занятые точки корабля + вокруг
        self.busy = []
        # список кораблей
        self.ships = []

    # Добавление корабля на доску
    def add_ship(self, ship):

        for d in ship.dots:
            # проверка занятости точки
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Соседние точки
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    # Вывод доски
    def __str__(self):
        res = ""
        res += "   | 1 | 2 | 3 | 4 | 5 | 6 |"
        res += "\n   _________________________"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1}  | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    # Находится ли точка за пределами доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # выстрел
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        # занята ли точка
        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    # + счетчику убитых кораблей
                    self.count += 1
                    # обводим по контуру
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


# Класс игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)

            user_f = self.us.board.field
            ai_f = self.ai.board.field

            res = "    Доска пользователя:"
            res += " " * 17
            res += "Доска компьютера:"
            res += "\n    | 1 | 2 | 3 | 4 | 5 | 6 |"
            res += " " * 8
            res += "   | 1 | 2 | 3 | 4 | 5 | 6 |"
            res += "\n    _________________________"
            res += " " * 8
            res += "   _________________________\n"
            s = 1
            for f, b in zip(user_f, ai_f):
                m = str(s) + "  | "
                for x in f:
                    m += x + " | "
                m += " " * 7
                m += str(s) + "  | "

                for x in b:
                    if self.ai.board.hid:
                        x = x.replace("■", "O")
                    m += x + " | "

                s = s + 1
                res += " " + m + "\n"

            print(res)

            # print("Доска пользователя:")
            # print(self.us.board)
            # print("-" * 20)
            # print("Доска компьютера:")
            # print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

# b = Board()
# print(b)
