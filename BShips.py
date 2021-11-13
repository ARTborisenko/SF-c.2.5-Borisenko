import copy
import time
from random import randint  # Импорт библиотеки случайных чисел


class BoardException(Exception):
    def __str__(self):
        return 'Некорректный ввод!'


class BoardOutException(BoardException):
    def __str__(self):
        return 'Ход за пределами доски!'


class BoardBusyException(BoardException):
    def __str__(self):
        return 'Допускаются ходы только в ячейки О!'


class Coord:  # Объявляем новый класс с типом данных координат
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'C ({self.x}, {self.y})'


class Ship:  # Класс корабля состоящего из длины, координаты носа и положения
    def __init__(self, coord, lenght=2, orientation='v'):
        self.coord = coord
        self.lenght = lenght
        self.orientation = orientation
        self.lives = lenght

    @property
    def ship_coords(self):  # Функция возвращающая коородинаты корабля
        s_coords = []
        if self.orientation == 'h':
            for i in range(self.lenght):
                s_coords.append(Coord(self.coord.x, self.coord.y + i))
        else:
            for i in range(self.lenght):
                s_coords.append(Coord(self.coord.x + i, self.coord.y))
        return s_coords


class Field:  # Класс инииализации игрового поля
    def __init__(self, size=6):
        self.size = size

        self.ai_hide = True
        self.shipspl = []
        self.shipsai = []
        self.s = [4, 3, 3, 3, 2, 2, 1, 1, 1, 1]
        self.ships = self.s[9 - size::]
        self.turns = [str(i + 1) for i in range(size)]
        self.plfield = [["O"] * size for _ in range(size)]
        self.aifield = [["O"] * size for _ in range(size)]
        self.aifieldhide = copy.copy(self.aifield)
        self.used = []

    def __str__(self): #Вывод поля на печать в консоль
        f = "PL|"
        for i in range(self.size):
            if i == 0:
                for j in range(1, self.size + 1):
                    f += f'P_{j}|'
                f += f' *** AI|'
                for j in range(1, self.size + 1):
                    f += f'A_{j}|'
            f += f'\n{i + 1}_|'
            for n in range(self.size):
                f += f' {self.plfield[i][n]} |'
            f += f' *** {i + 1}_|'
            for n in range(self.size):
                if self.ai_hide == True:
                    f += f' {self.aifieldhide[i][n]} |'
                else:
                    f += f' {self.aifield[i][n]} |'
        return f

    def add_ship(self, ship): #Добавление корабля на игровое поле
        counter = 0
        for i in ship.ship_coords:
            if i in self.used:
                counter += 1
            else:
                continue
        if counter > 0:
            return False
        for i in ship.ship_coords:
            if i.x < 0 or i.x > self.size or \
                    i.y < 0 or i.y > self.size:
                return False
        for i in ship.ship_coords:
            self.plfield[i.x - 1][i.y - 1] = "■"
            self.used_coord(i)
        self.shipspl.append(ship)
        return True

    def used_coord(self, coords): #Добавление использованных координат
        displacement = (
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        )
        for i, j in displacement:
            if Coord(coords.x + i, coords.y + j) not in self.used:
                self.used.append(Coord(coords.x + i, coords.y + j))

    def field_clear(self): #Полная очистка полей
        self.plfield = [["O"] * self.size for _ in range(self.size)]
        self.used = []
        self.aifield = [["O"] * self.size for _ in range(self.size)]
        self.used_ai = []
        self.shipspl = []
        self.shipsai = []


class Player:  # Класс игрока

    def __init__(self, field):
        self.playerships = field.ships


    def random_board(self, field): #Создание случайной доски, попытка с счетчиком
        playerships = copy.copy(self.playerships)
        counter = 0
        while True:
            if counter > 3000:
                field.field_clear()
                return False
            x = randint(1, field.size)
            y = randint(1, field.size)
            l = max(playerships)
            #            print(playerships)
            o = 'h' if randint(0, 1) == 1 else 'v'
            #            print(x, y, l, o)
            if field.add_ship(Ship(Coord(x, y), l, o)):
                field.add_ship(Ship(Coord(x, y), l, o))
                playerships.remove(l)
                #                print(field)
                if len(playerships) == 0:
                    return True
            else:
                counter += 1
                continue

    def player_make_random_board(self, field): #Гарантированное создание игрового поля
        while True:
            if self.random_board(field) == True:
                break
            else:
                continue


class AIPlayer:  # Класс противника ИИ
    def __init__(self):
        self.pl_board = []
        self.ai_board = []
        self.pl_ships = []
        self.ai_ships = []

    def make_ai_board(self, field, player): #ИИ забирает доску игрока и делается еще одна доска
        self.pl_board = copy.copy(field.plfield)
        self.pl_ships = copy.copy(field.shipspl)
        field.shipspl = []
        player.player_make_random_board(field)
        self.ai_board = copy.copy(field.plfield)
        self.ai_ships = copy.copy(field.shipspl)
        field.plfield = self.pl_board
        field.shipspl = self.pl_ships
        field.aifield = self.ai_board
        field.shipsai = self.ai_ships
        print(field)


class Battle: #Класс в котором прописан бой

    def __init__(self, field):
        self.coords_busy_ai = []
        self.coords_busy_pl = []
        self.ships_live_pl = len(field.shipspl)
        self.ships_live_ai = len(field.shipsai)

    def error(self, d, field):
        if len(d) == 2:
            if d[0] in field.turns and d[1] in field.turns:
                return d
        print("Некорректный ввод!")
        return False

    def pl_shot(self, field): #Выстрел игрока, возвращает False при промахе
        displacement = (
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        )
        s = input("Выстел игрока:")
        if self.error(s, field):
            shot_coord = Coord(int(s[0]), int(s[1]))

            if shot_coord not in self.coords_busy_ai:
                self.coords_busy_ai.append(shot_coord)
                shot_x = shot_coord.x - 1
                shot_y = shot_coord.y - 1
            else:
                print('Стрелять можно только в ячейки c О!')
                return False
        else:
            return False

        for ship in field.shipsai:
            if shot_coord in ship.ship_coords:
                field.aifieldhide[shot_x][shot_y] = 'X'
                ship.lives -= 1
                if ship.lives == 0:
                    for i in ship.ship_coords:
                        for j, k in displacement:
                            if 0 < i.x + j <= field.size and \
                                    0 < i.y + k <= field.size:
                                if field.aifieldhide[i.x - 1 + j][i.y - 1 + k] != 'X':
                                    field.aifieldhide[i.x - 1 + j][i.y - 1 + k] = '.'
                                    if Coord(i.x + j, i.y + k) not in self.coords_busy_ai:
                                        self.coords_busy_ai.append(Coord(i.x + j, i.y + k))
                    time.sleep(1)
                    self.ships_live_ai -= 1
                    print(f'Корабль противника потоплен. Осталось: {self.ships_live_ai}')
                    time.sleep(1)
                    print(field)
                    return False
                else:
                    time.sleep(1)
                    print('Попал!')
                    time.sleep(1)
                    print(field)
                    return False
        field.aifieldhide[shot_x][shot_y] = '.'
        time.sleep(1)
        print("Мимо!")
        time.sleep(1)
        print(field)
        return True

    def ai_shot(self, field): #Аналогично игроку стреляет ИИ
        displacement = (
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        )
        shot_coord = Coord(randint(1, field.size), randint(1, field.size))

        if shot_coord not in self.coords_busy_pl:
            self.coords_busy_pl.append(shot_coord)
            shot_x = shot_coord.x - 1
            shot_y = shot_coord.y - 1
        else:
            return True

        time.sleep(1)
        for ship in field.shipspl:
            if shot_coord in ship.ship_coords:
                print('Стреляет AI===>')
                field.plfield[shot_x][shot_y] = 'X'
                ship.lives -= 1
                if ship.lives == 0:
                    for i in ship.ship_coords:
                        for j, k in displacement:
                            if 0 < i.x + j <= field.size and \
                                    0 < i.y + k <= field.size:
                                if field.plfield[i.x - 1 + j][i.y - 1 + k] != 'X':
                                    field.plfield[i.x - 1 + j][i.y - 1 + k] = '.'
                                    if Coord(i.x + j, i.y + k) not in self.coords_busy_pl:
                                        self.coords_busy_pl.append(Coord(i.x + j, i.y + k))
                    time.sleep(randint(1, 3))
                    self.ships_live_pl -= 1
                    print(f'AI уничтожил наш корабль. Осталось: {self.ships_live_pl}')
                    time.sleep(1)
                    print(field)
                    return True
                else:
                    time.sleep(randint(1, 3))
                    print(f'AI подбил наш корабль в точке {shot_coord.x}{shot_coord.y}!')
                    time.sleep(1)
                    print(field)
                    return True
        print('Стреляет AI===>')
        time.sleep(randint(1, 3))
        field.plfield[shot_x][shot_y] = '.'
        print(F"AI выстрелил в {shot_coord.x}{shot_coord.y} и промахнулся...")
        time.sleep(1)
        print(field)
        return False


class Game:  # Класс для запуска игры
    def __init__(self, battle):
        self.battle = battle

    def winner(self): #Проверка на победителя
        if self.battle.ships_live_ai == 0:
            print('Победил игрок!')
            return False
        if self.battle.ships_live_pl == 0:
            print('В этот раз AI оказался сильней...')
            print('Все наши корабли на дне(')
            return False
        return True

    def start(self, field):
        winner = 0
        while winner == 0:
            while True:
                if self.winner():
                    if self.battle.pl_shot(field):
                        break
                    else:
                        continue
                else:
                    winner = 1
                    break

            while True:
                if winner == 0:
                    if self.winner():
                        if self.battle.ai_shot(field):
                            continue
                        else:
                            break
                    else:
                        winner = 1
                        break
                else:
                    break


s_values = ['5', '6', '7', '8', '9'] #Перечень возможных размеров поля

print("""
Правила игры:
При старте запрашивается размер поля. 
Размеры поля могут быть от 5/5 до 9/9 включительно.
Требуется ввести цифру и нажать Enter. 
После создания двух полей, когда в консоли запрашивается
Ход игрока: 
Требуется ввести номер строки затем номер столбца без 
пробелов, например: 12 - первая строка, второй столбец
Стрелять допускается только в ячейки в состоянии О
При попадании ячейка сменится на Х
При промахе ячейска сменится на .
Вокруг потопленного корабля . проставятся сами. Все
ради комфортного геймплея!
Веселой игры!        
""")

while True: #Запуск игры, обрабатывается исключением при некорректном вводе
    s = input('Введите желаемый размер поля от 5 до 9: ')
    try:
        if s not in s_values:
            raise BoardException()
    except BoardException as i:
        print('Некорректный ввод!!!!!')
        continue
    else:
        s_int = int(s)
        f = Field(size=s_int)
        p = Player(f)
        p.player_make_random_board(f)
        ai = AIPlayer()
        ai.make_ai_board(f, p)
        b = Battle(f)
        g = Game(b)
        g.start(f)
        break
