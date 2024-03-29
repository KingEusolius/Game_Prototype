from game_class import GameClass
import pygame, sys
from ui import *
from particle_player import *
from pathfinding import *
from projectiles import *
from item_player import *
from mouse import *
import grass
import random
import math
from observer import Observer

TILESIZE = 64
GRIDWIDTH = 16
GRIDHEIGHT = 10
DARKRED = (127, 0, 0)
LIGHTBLUE = (71, 117, 191)
DARKGRAY = (40, 40, 40)


class Particle_trigger_observer(Observer):
    def __init__(self, game_state):
        self.game_state = game_state

    def on_event(self, particle_type, position):
        print('Trigger particle')
        self.game_state.spawn_particle(particle_type, position)

class Fight(GameClass):
    def __init__(self, set_overworld):
        super().__init__(set_overworld)
        self.mobs = []
        self.player_chars = []
        self.particles = []
        self.items = []
        self.projectiles = []
        self.background_image = None
        self.celebration = False
        self.player_turn = True
        self.game_celebration = False
        self.ui = UI([None] * 4, self.spawn_particle)
        self.particle_player = Particle_Player()
        self.item_dictionary = Item_Dictionary()
        self.item_player = Item_Player(self.item_dictionary)

        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())

        self.avatar = None

        self.mob_idx = 0
        self.max_mob_idx = 0

        # set up the grass manager and enable shadows
        self.gm = grass.GrassManager('graphics/grass', tile_size=15, stiffness=900, max_unique=5, place_range=[0, 1])
        self.gm.enable_ground_shadows(shadow_radius=4, shadow_color=(0, 0, 1), shadow_shift=(1, 2))
        self.t = 0

        # fill in the base square
        if 0:
            for y in range(7, 32, 1):
                y += 5
                for x in range(10, 50, 1):
                    x += 5
                    v = random.random()
                    if v > 0.1:
                        self.gm.place_tile((x, y), int(v * 5), [0, 1, 2, 3, 4])

        # ai and pathfinding/navigation stuff. move to separate class
        self.g = SquareGrid(GRIDWIDTH, GRIDHEIGHT)
        self.path = None
        self.attack_path = None
        self.reachable_tiles = []
        self.shortest_path_tiles = []
        self.attack_tiles = []
        self.calculate_new_path = True
        self.occupied_spots_by_ai = []
        self.selected_mob = None
        self.can_ai_turn = False
        self.selected_char = None
        self.player_turn = True
        self.selected_skill = None
        self.selected_char_skill = None
        self.selected_skill_idx = -1


        # mouse
        self.mouse = Mouse()

    def set_avatar(self, avatar):
        self.avatar = avatar
        self.ui.set_inventory(self.avatar.inventory)

    def set_player_chars(self, chars):
        self.player_chars = chars
        for char in self.player_chars:
            char.position_x = 4 * 64
            char.reset_for_new_turn()
            char.get_stats(char.dictionary)

    def clear_player_chars(self):
        self.player_chars = []

    def set_mobs(self, mobs):
        self.mobs = mobs
        self.mob_idx = 0
        self.max_mob_idx = len(self.mobs)
        # self.mobs[1].set_nr_max_actions(2)
        # self.mobs[1].set_notify_fight(self.ai_turn)

    def clear_mobs(self):
        self.mobs = []

    def set_img(self, img):
        self.background_image = img

    def clear_img(self):
        self.background_image = None

    def clear_items(self):
        self.items = []

    def is_fight_over(self, player_characters):
        victory = True
        for mob in self.mobs:
            if mob.alive:
                victory = False

        # to do: correct code
        if victory and not self.celebration and 0:
            self.celebration = True
            for mob in self.mobs:
                self.spawn_item((mob.position_x, mob.position_y), mob.items)

        defeat = True
        for char in player_characters:
            if char.alive:
                defeat = False

        return victory or defeat

    def input_click_on_terrain(self):
        if self.selected_char.can_walk:
            self.selected_char.state_machine.trigger_transition("ACTION::TRANSITION_WALK")
            self.selected_char.waypoints = self.get_shortest_path()
            if self.selected_char.waypoints:
                self.selected_char.set_target_position(self.selected_char.waypoints[0][0],
                                                       self.selected_char.waypoints[0][1])
                self.selected_char.move_range -= len(self.selected_char.waypoints)

    def input_click_on_character(self):
        if self.selected_skill:
            ui_selected = True
        else:
            ui_selected = False
        if ui_selected:
            skill = self.selected_skill
            self.spawn_particle(skill.particle_type, pygame.mouse.get_pos())
            self.avatar.inventory[self.selected_skill_idx] = None
            self.ui.item_slots[self.selected_skill_idx].free_spot()

            self.selected_skill = None
            self.selected_skill_idx = -1
            return

        self.clear_path()
        self.character_selection()
        for spot in self.ui.resource_slots:
            spot.free_spot()
        if self.selected_char:
            if self.selected_char.can_walk:
                self.calculate_possible_paths_character()
            elif self.selected_char.can_attack:
                self.calculate_possible_attack_tiles(self.selected_char)
        self.calc_if_enemy_in_range()

    def input_click_on_skill(self):
        for idx, spot in enumerate(self.ui.resource_slots):
            if spot.active:
                self.selected_char_skill = spot.skill
                self.selected_skill_idx = idx

        for idx, spot in enumerate(self.ui.item_slots):
            if spot.active:
                self.selected_skill = spot.skill
                self.selected_skill_idx = idx

    def unit_transition_to_attack(self):
        char_x, char_y = self.selected_char.position_x, \
                         self.selected_char.position_y
        mob_x, mob_y = self.selected_mob.position_x, self.selected_mob.position_y
        char_x, char_y = from_screenspace_to_gridspace((char_x, char_y))
        mob_x, mob_y = from_screenspace_to_gridspace((mob_x, mob_y))
        if heuristic(vec(char_x, char_y), vec(mob_x, mob_y)) <= self.selected_char.attack_range:
            self.selected_char.target = self.selected_mob
            self.selected_mob.in_range = False
            self.selected_char.state_machine.trigger_transition("ACTION::TRANSITION_ATTACK")
            self.selected_char.deselect_after_action = True
            self.selected_char.is_selected(False)
            self.clear_path()
            self.selected_char = None

    def input_click_on_enemy(self):
        if self.selected_char_skill:
            ui_selected = True
        else:
            ui_selected = False

        if self.selected_char:
            self.selected_char.create_particle = ui_selected
            if ui_selected:
                skill = self.selected_char_skill
                self.selected_char.set_particle_create(self.spawn_particle, skill)
                self.selected_char.skills[self.selected_skill_idx] = None
                self.ui.resource_slots[self.selected_skill_idx].free_spot()
                self.selected_char_skill = None
                self.selected_skill_idx = -1

        self.mob_selection()
        # short range units
        if self.selected_char.long_range == 0:
            self.selected_char.state_machine.trigger_transition("ACTION::TRANSITION_WALK")
            self.selected_char.waypoints = self.get_shortest_path()
            if self.selected_char.waypoints:
                self.selected_char.set_target_position(self.selected_char.waypoints[0][0],
                                                       self.selected_char.waypoints[0][1])
                self.selected_char.move_range -= len(self.selected_char.waypoints)
            length_waypoints = len(self.selected_char.waypoints)
            # unit must walk up to enemy
            if length_waypoints:
                last_x, last_y = self.selected_char.waypoints[length_waypoints - 1][0], \
                                 self.selected_char.waypoints[length_waypoints - 1][1]
                mob_x, mob_y = self.selected_mob.position_x, self.selected_mob.position_y
                last_x, last_y = from_screenspace_to_gridspace((last_x, last_y))
                mob_x, mob_y = from_screenspace_to_gridspace((mob_x, mob_y))
                if heuristic(vec(last_x, last_y),
                             vec(mob_x, mob_y)) <= self.selected_char.attack_range:
                    self.selected_char.attack_after_walk = True
                    self.selected_char.target = self.selected_mob
                    self.selected_mob.in_range = False
                    self.selected_char.deselect_after_action = True
                    self.selected_char.is_selected(False)
                    self.selected_char = None
            else:
                self.unit_transition_to_attack()
        # long range unit
        else:
            self.unit_transition_to_attack()

    def input_clear_selection(self):
        self.clear_path()
        self.selected_char = None
        self.selected_mob = None
        self.selected_skill = None
        self.selected_char_skill = None
        self.selected_skill_idx = -1
        self.ui.on_mouse_click(pygame.mouse.get_pos())
        for spot in self.ui.resource_slots:
            spot.free_spot()
        #for spot in self.ui.item_slots:
        #    spot.free_spot()

        for char in self.player_chars:
            char.is_selected(False)
        for mob in self.mobs:
            mob.in_range = False

    def input_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if self.input_handling_allowed:
                mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.trigger_transition()
                if mouse_buttons[0] and self.game_celebration:
                    self.item_selection()
                if event.type == pygame.MOUSEBUTTONUP and self.game_celebration:

                    for it in self.items:
                        if it.selected:
                            it.selected = False
                            # check to assign to which character
                            mouse_position = from_screenspace_to_gridspace([it.position_x, it.position_y])
                            for char in self.avatar.chars:
                                # get char position
                                char_position = from_screenspace_to_gridspace((char.position_x, char.position_y))
                                # if positions coincide
                                if mouse_position[0] == char_position[0] and mouse_position[1] == char_position[1]:
                                    # find free skill spot of char
                                    idx = self.skills_find_free_spot(char)
                                    # if idx is smaller than number of skill slots, we have found an empty spot
                                    if idx < len(char.skills):
                                        char.skills[idx] = it
                                        self.items.remove(it)

                if event.type == pygame.MOUSEBUTTONDOWN and self.player_turn:
                    if self.game_celebration:
                        for it in self.items:
                            it.check_overlap(pygame.mouse.get_pos())
                        if mouse_buttons[2]:
                            self.item_pick_up()
                            self.input_clear_selection()
                            return

                    # this path is chosen if a character has already been selected
                    if self.selected_char and event.button == 1:
                        #if self.selected_skill:
                        #    self.handle_skill()
                        state = self.mouse_selection()
                        # click on terrain
                        if state == 0:
                            self.input_click_on_terrain()
                        # click on other character
                        elif state == 1:
                            self.input_click_on_character()
                        # click on enemy
                        elif state == 2 and self.selected_char.can_attack:
                            self.input_click_on_enemy()
                        # click on skill
                        elif state == 4:
                            self.input_click_on_skill()
                    # right click means everything is reset
                    elif event.button == 3:
                        self.input_clear_selection()
                    # character has been chosen for the first time
                    else:
                        #if self.selected_skill:
                        #    self.handle_skill()
                        state = self.mouse_selection()
                        if state == 1:
                            self.input_click_on_character()
                        elif state == 4:
                            self.input_click_on_skill()



                # keyboard input
                if event.type == pygame.KEYDOWN:
                    # ai turn in fight
                    if event.key == pygame.K_a:
                        self.player_turn = False
                        self.mob_idx = 0
                        for mob in self.mobs:
                            mob.turn_over = False
                            mob.nr_actions = 1
                        self.mob_idx = self.find_next_free_mob()
                        self.ai_turn()



    def update(self):
        current_mouse_pos = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        self.mouse.update()
        if self.mouse_position != current_mouse_pos and self.calculate_new_path:
            self.calculate_shortest_path_character()
            self.calc_if_enemy_in_range()
        self.mouse_position = current_mouse_pos
        brush_size = 2
        for char in self.player_chars:
            if char.alive:
                char.update()
                self.gm.apply_force((char.position_x + 32, char.position_y + 56), 12 * brush_size, 8 * brush_size)

        for mob in self.mobs:
            if mob.alive:
                mob.update()
                self.gm.apply_force((mob.position_x + 32, mob.position_y + 56), 12 * brush_size, 8 * brush_size)

        for part in self.particles:
            part.update()

        for it in self.items:
            it.update()
            self.gm.apply_force((it.position_x + 32, it.position_y + 56), 8 * brush_size, 8 * brush_size)

        for pr in self.projectiles:
            pr.update()
            self.gm.apply_force((pr.position_x, pr.position_y + 16), 8 * brush_size, 8 * brush_size)
            if pr.hit:
                self.projectiles.remove(pr)

        if not self.player_turn:
            # first try if this is the right place to check
            self.check_if_mob_is_finished()
            self.check_if_ai_is_finished()

        victory = True

        for mob in self.mobs:
            if mob.alive:
                victory = False

        if victory and not self.game_celebration:
            self.game_celebration = True
            new_list = [char for char in self.player_chars if char.alive]
            for char in new_list:
                char.set_particle_create(self.spawn_particle, None)
                char.check_for_level_update(len(self.mobs) * 100)
            for mob in self.mobs:
                self.spawn_item((mob.position_x, mob.position_y), mob.items)

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_reachable_tiles(screen)

        self.draw_characters(screen)

        self.draw_ui(screen)
        self.mouse.draw(screen)

        self.transition_drawing(screen)

    def draw_background(self, screen):
        screen.blit(self.background_image, (0, 0))

    def draw_characters(self, screen):
        # switch to update function, but separate update and render functionality in gm.update_render
        rot_function = lambda x, y: int(math.sin(self.t / 60 + x / 100) * 5)
        # run the update/render for the grass
        dt = 0.016
        self.gm.update_render(screen, dt, rot_function=rot_function)

        # increment master time
        self.t += dt * 100

        for char in self.player_chars:
            char.draw(screen)

        for mob in self.mobs:
            mob.draw(screen)

        for part in self.particles:
            part.draw(screen)

        for it in self.items:
            it.draw(screen)

        for pr in self.projectiles:
            pr.draw(screen)

    def draw_ui(self, screen):
        self.ui.draw(screen, self.selected_char)

    def clear_particle(self, particle):
        #cur_particle = self.particles.pop(0)
        #del cur_particle
        if particle in self.particles:
            self.particles.remove(particle)

    def spawn_particle(self, particle_type, position):
        pos = from_screenspace_to_gridspace(position)
        self.particles.append(
            Particle(self.particle_player, particle_type, pos, self.clear_particle, self.mobs, self.player_chars))

    def calc_if_enemy_in_range(self):
        if self.selected_char:
            length = len(self.shortest_path_tiles)
            if length:
                x_pos = self.shortest_path_tiles[length - 1][0]
                y_pos = self.shortest_path_tiles[length - 1][1]
                x_fig, y_fig = from_screenspace_to_gridspace((x_pos, y_pos))
            else:
                x_pos = self.selected_char.position_x
                y_pos = self.selected_char.position_y
                x_fig, y_fig = from_screenspace_to_gridspace((x_pos, y_pos))

            for mob in self.mobs:
                mob.in_range = False
                if mob.alive:
                    x_mob, y_mob = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
                    char_pos = vec(x_fig, y_fig)
                    mob_pos = vec(x_mob, y_mob)
                    mob.in_range = heuristic(char_pos, mob_pos) <= self.selected_char.attack_range

    def get_shortest_path(self):
        self.calculate_new_path = False
        return self.shortest_path_tiles

    def clear_path(self):
        self.path = None
        self.attack_path = None
        self.attack_tiles.clear()
        self.reachable_tiles.clear()
        self.shortest_path_tiles.clear()
        self.calculate_new_path = True

    def draw_reachable_tiles(self, screen):
        for tile in self.reachable_tiles:
            rect = pygame.Rect(tile[0], tile[1], TILESIZE, TILESIZE)
            pygame.draw.line(screen, DARKGRAY, rect.topleft, rect.topright, 2)
            pygame.draw.line(screen, DARKGRAY, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(screen, DARKGRAY, rect.topright, rect.bottomright, 2)
            pygame.draw.line(screen, DARKGRAY, rect.bottomleft, rect.bottomright, 2)
        for idx, tile in enumerate(self.shortest_path_tiles):
            rect = pygame.Rect(tile[0], tile[1], TILESIZE, TILESIZE)
            pygame.draw.line(screen, LIGHTBLUE, rect.topleft, rect.topright, 2)
            pygame.draw.line(screen, LIGHTBLUE, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(screen, LIGHTBLUE, rect.topright, rect.bottomright, 2)
            pygame.draw.line(screen, LIGHTBLUE, rect.bottomleft, rect.bottomright, 2)
        for tile in self.attack_tiles:
            rect = pygame.Rect(tile[0], tile[1], TILESIZE, TILESIZE)
            pygame.draw.line(screen, DARKRED, rect.topleft, rect.topright, 2)
            pygame.draw.line(screen, DARKRED, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(screen, DARKRED, rect.topright, rect.bottomright, 2)
            pygame.draw.line(screen, DARKRED, rect.bottomleft, rect.bottomright, 2)

    def ai_turn(self):
        self.occupied_spots_by_ai.clear()
        mob = self.mobs[self.mob_idx]
        mob_ready = not mob.actions
        if mob.alive and mob_ready:
            mob.ai_turn = True
            self.reachable_tiles.clear()
            self.g.walls = []
            self.g.obstacles = []
            for oc in self.occupied_spots_by_ai:
                self.g.obstacles.append(oc)
            for mobster in self.mobs:
                if mobster != mob:
                    x, y = from_screenspace_to_gridspace((mobster.position_x, mobster.position_y))
                    self.g.obstacles.append((x, y))

            self.calculate_path(mob, 18)

            nearest_char = mob.target_finder.execute([mob.position_x, mob.position_y], self.player_chars)

            if nearest_char:
                self.mob_decision(mob, nearest_char)

        self.clear_path()

    def check_if_mob_is_finished(self):
        mob = self.mobs[self.mob_idx]
        # if mobs turn is over, we can take a look for the next mob in line
        # if no next mob is found, the player can make its turn again
        if mob.turn_over:
            self.mob_idx = self.find_next_free_mob()
            # next enemy can decide what to do
            if self.mob_idx < self.max_mob_idx:
                self.ai_turn()
            else:
                # player can now fight
                self.can_ai_turn = False
                self.clear_path()
                for char in self.player_chars:
                    char.reset_for_new_turn()

    def find_next_free_mob(self):
        for idx, mob in enumerate(self.mobs):
            if not mob.turn_over and mob.alive:
                return idx
        return self.max_mob_idx

    def check_if_ai_is_finished(self):
        finished = True
        for mob in self.mobs:
            if mob.ai_turn:
                finished = False
        if finished:
            self.player_turn = True

    def create_projectile(self, start_position_x, start_position_y, target, attack_power):
        pos = (start_position_x + 32, start_position_y + 16)
        pro = Arrow(pos, target, attack_power)
        self.projectiles.append(pro)
        return pro

    def mouse_selection(self):
        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        if self.ui.on_mouse_click(pygame.mouse.get_pos()):
            return 4

        for char in self.player_chars:
            char_position = from_screenspace_to_gridspace((char.position_x, char.position_y))
            pos = pygame.mouse.get_pos()
            pos_in_mask = pos[0] - char.img.get_rect().x - char.position_x, pos[1] - char.img.get_rect().y - char.position_y
            mask = pygame.mask.from_surface(char.img)
            touching = char_position == self.mouse_position and mask.get_at(pos_in_mask)
            if touching:
                return 1
            #if char_position == self.mouse_position:
            #    return 1

        for mob in self.mobs:
            mob_position = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
            if mob_position == self.mouse_position:
                return 2

        for rect in self.ui.resource_slots:
            rect_position = from_screenspace_to_gridspace((rect.position_x, rect.position_y))
            if rect_position == self.mouse_position:
                return 3

        return 0

    def character_selection(self):
        self.selected_char = None
        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        for char in self.player_chars:
            char_position = from_screenspace_to_gridspace((char.position_x, char.position_y))
            if char_position == self.mouse_position:
                char.is_selected(True)
                self.selected_char = char
                char.deselect_after_action = False
            else:
                char.is_selected(False)

    def mob_selection(self):
        self.selected_mob = None
        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        for mob in self.mobs:
            mob_position = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
            if mob_position == self.mouse_position:
                self.selected_mob = mob

    def spawn_item(self, position, items):
        pos = from_screenspace_to_gridspace(position)
        for item in items:
            self.items.append(Item(self.item_player, item, pos, self.item_dictionary))

    def item_pick_up(self):
        for it in self.items:
            if it.check_overlap(pygame.mouse.get_pos()):
                i = self.inventory_find_free_spot()
                if i <= len(self.avatar.inventory) - 1:
                    self.avatar.inventory[i] = it
                    self.ui.set_spot_occupied(i, it)
                    self.items.remove(it)

    def item_selection(self):
        for it in self.items:
            if it.selected and not it.upgrade:
                it.position_x = pygame.mouse.get_pos()[0]
                it.position_y = pygame.mouse.get_pos()[1]

    def inventory_find_free_spot(self):
        for i in range(len(self.avatar.inventory)):
            if not self.avatar.inventory[i]:
                return i
        return len(self.avatar.inventory)

    def skills_find_free_spot(self, char):
        for i in range(len(char.skills)):
            if not char.skills[i] and char.skills_available_this_turn[i]:
                return i
        return len(len(char.skills))

    def mob_decision(self, mob, nearest_char):
        x_fig, y_fig = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
        x_end, y_end = from_screenspace_to_gridspace((nearest_char.position_x, nearest_char.position_y))
        shortest_path = breadth_first_search_with_end(self.g, vec(x_end, y_end), vec(x_fig, y_fig),
                                                      self.path)
        goal = vec(x_end, y_end)
        start = vec(x_fig, y_fig)

        self.shortest_path_tiles.clear()
        current = start + shortest_path[vec2int(start)]
        x = None
        y = None
        while current != goal and heuristic(start, current) <= mob.move_range and heuristic(current,
                                                                                            goal) >= mob.attack_range:
            x = current.x * TILESIZE
            y = current.y * TILESIZE
            self.shortest_path_tiles.append((x, y))
            # find next in path
            current = current + shortest_path[vec2int(current)]
        if x is not None and y is not None:
            last_x, last_y = x / TILESIZE, y / TILESIZE
            self.occupied_spots_by_ai.append((last_x, last_y))

        mob.waypoints = self.get_shortest_path() * 1
        # mob has to walk
        if mob.waypoints:
            mob.state_machine.trigger_transition("ACTION::TRANSITION_WALK")
            mob.actions.append('walk')
            mob.set_target_position(mob.waypoints[0][0],
                                    mob.waypoints[0][1])
            # mob can attack directly after walking
            if heuristic(vec(last_x, last_y), goal) <= mob.attack_range:
                mob.attack_after_walk = True
                mob.target = nearest_char
                mob.actions.append('attack')
            else:
                mob.attack_after_walk = False
        else:
            # mob can attack directly
            mob.target = nearest_char
            mob.state_machine.trigger_transition("ACTION::TRANSITION_ATTACK")
            mob.actions.append('attack')

    def calculate_possible_paths_character(self):
        if not self.selected_char:
            self.clear_path()
            return

        if not self.selected_char.can_walk:
            self.clear_path()
            return

        self.reachable_tiles.clear()
        self.g.walls.clear()
        self.g.obstacles.clear()

        character = self.selected_char
        for char in self.player_chars:
            if char != character:
                x, y = from_screenspace_to_gridspace((char.position_x, char.position_y))
                self.g.obstacles.append((x, y))
        for mob in self.mobs:
            x, y = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
            self.g.obstacles.append((x, y))

        self.calculate_path(character)

    def calculate_path(self, character, move_range=None):
        x_fig, y_fig = from_screenspace_to_gridspace((character.position_x, character.position_y))
        if not move_range:
            movement_range = character.move_range
        else:
            movement_range = move_range
        self.path = breadth_first_search(self.g, vec(x_fig, y_fig), movement_range)
        self.reachable_tiles.append((x_fig * TILESIZE, y_fig * TILESIZE))
        for node, dir in self.path.items():
            if dir:
                x, y = node
                x = x * TILESIZE
                y = y * TILESIZE
                self.reachable_tiles.append((x, y))

    def calculate_possible_attack_tiles(self, character):
        self.clear_path()
        self.g.walls.clear()
        self.g.obstacles.clear()
        x_fig, y_fig = from_screenspace_to_gridspace((character.position_x, character.position_y))
        self.attack_path = breadth_first_search(self.g, vec(x_fig, y_fig), character.attack_range)
        self.attack_tiles.append((x_fig * TILESIZE, y_fig * TILESIZE))
        for node, dir in self.attack_path.items():
            if dir:
                x, y = node
                x = x * TILESIZE
                y = y * TILESIZE
                self.attack_tiles.append((x, y))

    def calculate_shortest_path_character(self):
        if not self.path:
            return
        if not self.selected_char:
            self.clear_path()
            return

        character = self.selected_char
        x_fig, y_fig = from_screenspace_to_gridspace((character.position_x, character.position_y))
        x_end, y_end = from_screenspace_to_gridspace(pygame.mouse.get_pos())

        shortest_path = breadth_first_search_with_end(self.g, vec(x_end, y_end), vec(x_fig, y_fig),
                                                      self.path)
        goal = vec(x_end, y_end)
        # draw path from start to goal
        start = vec(x_fig, y_fig)
        if shortest_path:
            self.shortest_path_tiles.clear()
            current = start + shortest_path[vec2int(start)]
            while current != goal and heuristic(start, current) <= character.move_range and len(
                    self.shortest_path_tiles) < character.move_range - 1:
                x = current.x * TILESIZE
                y = current.y * TILESIZE
                self.shortest_path_tiles.append((x, y))
                # find next in path
                current = current + shortest_path[vec2int(current)]
            self.shortest_path_tiles.append((current.x * TILESIZE, current.y * TILESIZE))


def from_screenspace_to_gridspace(screen_coordinates):
    x_grid = screen_coordinates[0] // TILESIZE
    y_grid = screen_coordinates[1] // TILESIZE
    return x_grid, y_grid
