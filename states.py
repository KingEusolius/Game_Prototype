import pygame


class State_machine:
    def __init__(self, character_reference):
        self.idle = Idle(character_reference)
        self.walk = Walk(character_reference)
        self.attack = Attack(character_reference)
        self.take_hit = Take_hit(character_reference)
        self.death = Death(character_reference)
        self.dead = Dead(character_reference)

        self.current_state = self.idle
        self.character = character_reference

    def set_state(self, new_state):
        self.current_state = new_state

    def transition(self, new_state):
        self.current_state.on_exit()
        self.current_state = new_state
        self.current_state.on_entry()

    def trigger_transition(self, transition):
        if transition == "ACTION::NO_TRANSITION":
            return

        # change from string to enum
        if transition == "ACTION::TRANSITION_IDLE":
            new_state = self.idle
            self.character.state = "idle"
        elif transition == "ACTION::TRANSITION_WALK":
            new_state = self.walk
            self.character.state = "walk"
        elif transition == "ACTION::TRANSITION_ATTACK":
            new_state = self.attack
            self.character.state = "attack"
        elif transition == "ACTION::TRANSITION_HIT":
            new_state = self.take_hit
            self.character.state = "take_hit"
        elif transition == "ACTION::TRANSITION_DEATH":
            new_state = self.death
            self.character.state = "death"
        elif transition == "ACTION::TRANSITION_DEAD":
            new_state = self.dead
            self.character.state = "dead"

        self.transition(new_state)


class State:
    def __init__(self, character_reference):
        pass

    def on_entry(self):
        pass

    def on_exit(self):
        pass

    def update(self, is_finished):
        pass


class Idle(State):
    def __init__(self, character_reference):
        self.character = character_reference

    def on_entry(self):
        self.character.animation_index = 0

    def on_exit(self):
        pass

    def update(self, is_finished):
        if self.character.health > 0:
            return "ACTION::NO_TRANSITION"

        # return "ACTION::TRANSITION_DEATH"


class Walk(State):
    def __init__(self, character_reference):
        self.character = character_reference

    def on_entry(self):
        self.character.animation_index = 0

    def on_exit(self):
        # TO DO: refactor this part of the code
        if self.character.is_mob:
            self.character.actions.pop(0)
        self.character.clear_path_for_game()
        if self.character.move_range <= 0:
            self.character.can_walk = False
        if self.character.deselect_after_action:
            self.character.is_selected(False)
        # still a bug here. Character should not calculate attack path if he attacks after walking
        if not self.character.attack_after_walk:
            if self.character.can_attack and not self.character.is_mob:
                self.character.calc_attack_path(self.character)

    def update(self, is_finished):
        if len(self.character.waypoints) > 0:
            # character can walk
            self.character.move(pygame.math.Vector2(self.character.direction_x, self.character.direction_y))
            return "ACTION::NO_TRANSITION"

        # character has arrived at destination -> decision for next action
        if self.character.attack_after_walk:
            # state transition from walk to attack
            self.character.attack_after_walk = False
            return "ACTION::TRANSITION_ATTACK"

        # state transition from walk to idle
        return "ACTION::TRANSITION_IDLE"


class Attack(State):
    def __init__(self, character_reference):
        self.character = character_reference

    def on_entry(self):
        self.character.animation_index = 0
        self.character.get_direction(self.character.target.position_x, self.character.target.position_y)
        # if we are a close range unit, we want to trigger the take_hit state at the target
        if self.character.long_range == 0:
            # here we should initiate the state transition for our target
            self.character.target.state_machine.trigger_transition("ACTION::TRANSITION_HIT")
            # this part should be in the on_entry function of state take_hit OR maybe not? because of the damage dealt?
            self.character.target.take_damage(self.character.attack_power)
            self.character.target = None
        else:
            # TO DO: refactor this part of the code!
            if "lich" in self.character.class_name:
                self.character.create_projectile("death_ripple",
                                                 (self.character.target.position_x, self.character.target.position_y))
            else:
                self.character.create_projectile(self.character.position_x, self.character.position_y,
                                                 self.character.target, self.character.attack_power)

    def on_exit(self):
        if self.character.is_mob:
            self.character.actions.pop(0)
        self.character.can_attack = False

    def update(self, is_finished):
        if not is_finished:
            return "ACTION::NO_TRANSITION"

        return "ACTION::TRANSITION_IDLE"


class Take_hit(State):
    def __init__(self, character_reference):
        self.character = character_reference

    def on_entry(self):
        self.character.animation_index = 0

    def on_exit(self):
        self.character.update_status()

    def update(self, is_finished):
        if not is_finished:
            return "ACTION::NO_TRANSITION"
            # state transition from take hit to idle
        if self.character.health <= 0:
            return "ACTION::TRANSITION_DEATH"

        return "ACTION::TRANSITION_IDLE"


class Death(State):
    def __init__(self, character_reference):
        self.character = character_reference

    def on_entry(self):
        self.character.animation_index = 0

    def on_exit(self):
        self.character.alive = False

    def update(self, is_finished):
        if not is_finished:
            return "ACTION::NO_TRANSITION"
        # state transition from death to dead
        return "ACTION::TRANSITION_DEAD"


class Dead(State):
    def __init__(self, character_reference):
        self.character = character_reference

    def on_entry(self):
        self.character.animation_index = 0

    def on_exit(self):
        pass

    def update(self):
        self.character.animation_index = 0
        return "ACTION::NO_TRANSITION"
