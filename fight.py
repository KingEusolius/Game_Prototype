
class Fight:
    def __init__(self, mobs, img):
        self.mobs = mobs
        self.img = img
        self.celebration = False

    def is_fight_over(self, player_characters):
        victory = True
        for mob in self.mobs:
            if mob.alive:
                victory = False

        if victory and not self.celebration and 0:
            self.celebration = True
            for mob in self.mobs:
                self.spawn_item((mob.position_x, mob.position_y))

        defeat = True
        for char in player_characters:
            if char.alive:
                defeat = False

        return victory or defeat
