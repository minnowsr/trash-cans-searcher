# trash cans manip solver
# version 0.1
# author: https://github.com/minnowsr/trash-cans-searcher

DIRECTIONS = ["up", "down", "left", "right", "none"]
FRAMES_TO_GYM = 190
FRAME_WINDOW = 15

class RNG:
    def __init__(self, seed):
        self.initial_seed = seed
        self.seed = seed
        self.frame = 1

    def advance(self, n=1):
        for i in range(n):
            self.seed = ((self.seed * 0x41C64E6D) + 0x6073) % (2**32)
            self.frame += 1
        return self

    def next(self, n=1):
        seed = self.seed

        for i in range(n):
            seed = ((seed * 0x41C64E6D) + 0x6073) % (2**32)
        return RNG(seed)

    def upper16(self):
        return self.seed >> 16

    def reset(self):
        self.seed = self.initial_seed
        self.frame = 1

    def get_cycle(self):
        return [16, 32, 48, 64][self.upper16() % 4] 

    def get_direction(self):
        return [0, 1, 2, 3][self.upper16() % 4] 

    def solve_cans(self):
        can_2_directions = [
            ("R", "D"),
            ("L", "R", "D"), 
            ("L", "R", "D"), 
            ("L", "R", "D"), 
            ("L", "D"),
            ("U", "R", "D"),
            ("U", "L", "D", "R"),
            ("U", "L", "D", "R"),
            ("U", "L", "D", "R"),
            ("U", "L", "D"),
            ("U", "R"),
            ("U", "L", "R"),
            ("U", "L", "R"),
            ("U", "L", "R"),
            ("U", "L")
        ]

        can_1 = self.next().upper16() % 15

        can_2_candidates = can_2_directions[can_1]
        can_2 = can_2_candidates[self.next(2).upper16() % len(can_2_candidates)]

        return f"{can_1+1}{can_2}"

    def print(self):
        print(hex(self.seed))

class NPC:
    def __init__(self, tick, bounds, npc_type, name="", extra_tick=0):
        self.tick = tick + extra_tick

        self.max_x, self.max_y = bounds
        self.x, self.y = 1, 1

        self.npc_type = npc_type
        self.name = name

        self.direction = 4
        self.direction_history = []
        self.chose_direction = False

    def move(self, direction):

        if direction == 0: 
            self.y -= 1
        elif direction == 1: 
            self.y += 1
        elif direction == 2: 
            self.x -= 1
        elif direction == 3: 
            self.x += 1

        cond = 0 <= self.x <= self.max_x and 0 <= self.y <= self.max_y
        if cond:
            self.direction = direction
            self.direction_history.append(DIRECTIONS[direction])
        
        if self.x > self.max_x:
            self.x = self.max_x
        elif self.x < 0:
            self.x = 0

        if self.y > self.max_y:
            self.y = self.max_y
        elif self.y < 0:
            self.y = 0

        return 9 if cond else 2

    def print(self):
        print(f"{self.name}: ({self.x}, {self.y}) | tick: {self.tick} | last_direction: {DIRECTIONS[self.direction]}")
    
    def advance(self, rng, can_move=True):
        self.tick -= 1
        if can_move:
            if self.tick <= 0 and not self.chose_direction:
                direction = rng.advance().get_direction()
                self.tick = self.move(direction)
                self.chose_direction = True
            elif self.tick <= 0:
                self.tick = rng.advance().get_cycle()
                self.chose_direction = False
        else:
            self.tick = rng.advance().get_cycle()
            rng.advance()
            self.chose_direction = False

rng = RNG(0x3a73Ab23)
npcs = [NPC(rng.advance().get_cycle(), (2,2), 2, "girl", 0), NPC(rng.advance().get_cycle(), (2,2), 2, "guy", 0)]

frames = []

for frame in range(FRAMES_TO_GYM+FRAME_WINDOW):
    if frame > FRAMES_TO_GYM:
        cans = rng.solve_cans()
        frames.append((f"{hex(rng.next(2).seed)} frame {frame}: ({''.join(npcs[0].direction_history)}, {''.join(npcs[1].direction_history)})  {cans}"))

    for npc in npcs:
        npc.advance(rng)

print('\n'.join(frames))
