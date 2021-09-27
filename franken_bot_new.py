from model.decisions.use_item_decision import UseItemDecision
from model.tile_map import TileMap
from networking.io import Logger
from game import Game
from api import game_util
from model.position import Position
from model.decisions.move_decision import MoveDecision
from model.decisions.action_decision import ActionDecision
from model.decisions.buy_decision import BuyDecision
from model.decisions.harvest_decision import HarvestDecision
from model.decisions.plant_decision import PlantDecision
from model.decisions.do_nothing_decision import DoNothingDecision
from model.tile_type import TileType
from model.item_type import ItemType
from model.crop_type import CropType
from model.upgrade_type import UpgradeType
from model.game_state import GameState
from model.player import Player
from api.constants import Constants

import random

from golden_corn_bot import get_move_decision as corn_get_move_decision
from golden_corn_bot import get_action_decision as corn_get_action_decision


logger = Logger()
constants = Constants()

do_not_do = {'the_patriots', 'venkat'}
golden_corn = {'sheldon', 'broken_windows'}

has_planted_before = False
previous_position = None


def get_crop_tile(pos: Position, tile_map: TileMap) -> Position:
    for x in range(tile_map.map_width):
        for y in range(tile_map.map_height):
            if tile_map.get_tile(x, y).crop.value > 0:
                return Position(x, y)

    return pos

def opponent_has_planted(pos: Position, tile_map: TileMap) -> bool:
    for x in range(tile_map.map_width):
        for y in range(tile_map.map_height):
            if tile_map.get_tile(x, y).crop.value > 0:
                return True

    return False


def scarecrow_pos(tile_map: TileMap):
    for x in range(tile_map.map_width):
        for y in range(tile_map.map_height):
            if tile_map.get_tile(x, y).scarecrow_effect is not None:
                return Position(x, y)

    return None

def first_moves(game: Game) -> MoveDecision:
    game_state: GameState = game.get_game_state()
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position

    decisions = [move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT))),
                 move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT))),
                 move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT))),
                 move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT))),
                 move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT))),
                 move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT))),
                 MoveDecision(Position(pos.x - 14, pos.y)),
                 MoveDecision(Position(pos.x, pos.y + 15)),
                 MoveDecision(Position(pos.x, pos.y + 15)),

                 MoveDecision(Position(pos.x + 5, pos.y + 15)),
                 MoveDecision(Position(pos.x + 5, pos.y)),
                 MoveDecision(Position(pos.x + 5, pos.y + 3)),

                 MoveDecision(Position(pos.x + 3, pos.y - 17)),
                 MoveDecision(Position(pos.x, pos.y - 17)),
                 MoveDecision(pos),
                 MoveDecision(pos),
                 MoveDecision(pos),
                 MoveDecision(pos),
                 MoveDecision(pos),
                 move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT)))]

    return decisions[game_state.turn - 45]

def first_actions(game: Game) -> ActionDecision:
    game_state: GameState = game.get_game_state()
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position

    actions = [DoNothingDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               BuyDecision([CropType.DUCHAM_FRUIT, CropType.POTATO, CropType.CORN], [2, 2, 1]),
               DoNothingDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               PlantDecision([CropType.POTATO], [pos]),
               PlantDecision([CropType.POTATO], [pos]),
               PlantDecision([CropType.CORN], [pos]),
               DoNothingDecision(),
               PlantDecision([CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT], [pos, Position(pos.x, pos.y + 1)]),
               UseItemDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               HarvestDecision([pos, Position(pos.x, pos.y + 1)]),
               HarvestDecision([pos, Position(pos.x, pos.y + 1)]),
               HarvestDecision([pos, Position(pos.x, pos.y + 1)])]

    return actions[game_state.turn - 45]


has_planted_before = False

item_map = {
    'p': [1.375, 4, 5, 0],
    'c': [2.5, 2, 5, .5],
    'g': [1.65, 10, 15, .5],
    'j': [4, 5, 20, .75],
    'q': [2.6, 15, 30, .25],
    'd': [20, 5, 100, 1],
    'g': [500, 3, 1000, 1],
    'x': [.167, 30, 5, 0]
}

my_plants = {}

value_grid = []
mask_grid = []


def harv(x, y):
    return HarvestDecision(
        [Position(i, y) for i in range(x - 1, x + 2)] + [Position(x, j) for j in range(y - 1, y + 2)])


def fertility(y, turn):
    if y < 3:
        return -1
    lowest_ok = (turn + 2) // 3 - 2

    if lowest_ok - 2 <= y <= lowest_ok:
        return 1
    elif y == lowest_ok - 3 or y == lowest_ok - 5:
        return 1.2
    elif y == lowest_ok - 4:
        return 1.5
    elif lowest_ok - 8 <= y <= lowest_ok - 6:
        return 1
    elif y > lowest_ok:
        return 0

    return -1


def get_charac(cropType):
    s = ''
    # logger.info(type(cropType))
    if cropType == 'POTATO':
        s = 'p'
    elif cropType == 'CORN':
        s = 'c'
    elif cropType == 'GRAPE':
        s = 'g'
    elif cropType == 'JOGAN_FRUIT':
        s = 'j'
    elif cropType == 'PEANUT':
        s = 'x'
    elif cropType == 'QUADROTRITICALE':
        s = 'q'
    elif cropType == 'DUCHAM_FRUIT':
        s = 'd'
    elif cropType == 'GOLDEN_CORN':
        s = 'g'

    charac = item_map[s]
    return charac


def integ_life(pos_y, cropType, startlife_turn, mine=False):
    fertility_start = fertility(pos_y, startlife_turn)
    charac = get_charac(cropType)

    value = 0 if mine else charac[2]
    for i in range(charac[1]):
        f = fertility(pos_y, startlife_turn + i)
        if f == -1 or startlife_turn + i >= 180:
            return 0
        else:
            value += charac[0] * ((f - 1) * charac[3] + 1)

    return value


def tile_value(game, position, turn):
    tile = game.tile_map.get_tile(position[0], position[1])
    if tile.crop.value > 0:
        crop_type = tile.crop.type
        charac = get_charac(crop_type)
        value = integ_life(position[1], crop_type, turn - (charac[1] - tile.crop.growth_timer),
                           position in my_plants) if tile.crop.growth_timer != 0 else tile.crop.value
        return value
    return 0


def build_value_grid(game_state):
    global value_grid
    value_grid = []
    for x in range(0, 30):
        value_col = []
        for y in range(0, 50):
            value_col.append(tile_value(game_state, (x, y), game_state.turn))
        value_grid.append(value_col)


def build_mask_grid(game_state):
    global mask_grid
    global value_grid
    build_value_grid(game_state)
    RAD = 2
    mask_grid = []
    for x in range(0, 30):
        mask_col = []
        for y in range(0, 50):
            val = 0
            for xx in range(x - RAD, x + RAD + 1):
                for yy in range(y - RAD, y + RAD + 1):
                    if xx < 0 or xx > 29 or yy < 0 or yy > 49 or distance((x, y), (xx, yy)) > RAD:
                        val += 0
                    else:
                        v = value_grid[xx][yy]
                        val += v
                        if v != 0 and distance((x, y), (xx, yy)) <= 1:
                            val += 1.5 - distance((x, y), (xx, yy))

            mask_col.append(val)
        mask_grid.append(mask_col)


def get_best_val_tile(opp_pos, game_state):
    global mask_grid
    build_mask_grid(game_state)

    best_pts = []
    best_val = 0

    for x in range(0, 30):
        for y in range(0, 50):
            if mask_grid[x][y] > best_val:
                best_val = mask_grid[x][y]
                best_pts = [(x, y)]
            elif mask_grid[x][y] == best_val and best_val != 0:
                best_pts.append((x, y))

    if (len(best_pts) == 0):
        return [opp_pos]
    return best_pts


def move_from_to(start: Position, end: Position):
    moves_left = 20
    x = start.x
    y = start.y
    if abs(end.x - start.x) <= moves_left:
        x = end.x
        moves_left -= abs(end.x - start.x)
    else:
        if end.x > start.x:
            x = start.x + moves_left
            moves_left = 0
        else:
            x = start.x - moves_left
            moves_left = 0

    if moves_left > 0:
        if abs(end.y - start.y) <= moves_left:
            y = end.y
            moves_left -= abs(end.y - start.y)
        else:
            if end.y > start.y:
                y = start.y + moves_left
                moves_left = 0
            else:
                y = start.y - moves_left
                moves_left = 0

    return MoveDecision(Position(x, y))

def distance(p1, p2):
    return abs(p2[1] - p1[1]) + abs(p2[0] - p1[0])

def get_move_decision(game: Game) -> MoveDecision:
    game_state: GameState = game.get_game_state()
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position
    logger.info(f"Currently at {my_player.position}")

    if game_state.get_opponent_player().name in golden_corn:
        return corn_get_move_decision(game)

    global has_planted_before

    if game_state.turn < 45 and not has_planted_before:
        has_planted_before = opponent_has_planted(pos, game_state.tile_map)
    elif 45 <= game_state.turn < 65 and not has_planted_before and game_state.get_opponent_player().money >= my_player.money and game_state.get_opponent_player().name not in do_not_do:
        return first_moves(game)

    # If we have items, go sell them
    if len(my_player.harvested_inventory) > 5:
        decision = move_from_to(pos, Position(constants.BOARD_WIDTH // 2, 0))
    else:
        # Go towards nearest crop
        opppos = game_state.get_opponent_player().position
        next_pos = get_best_val_tile((opppos.x, opppos.y), game_state)
        logger.info(str(next_pos))

        closest = 1000000000
        closest_p = next_pos[0]
        for p in next_pos:
            d = distance(p, (pos.x, pos.y))
            if d < closest:
                closest = d
                closest_p = p

        next_pos = Position(closest_p[0], closest_p[1])
        # logger.info(str(mask_grid))

        decision = move_from_to(pos, next_pos)

    if game_state.turn >= 175:
        decision = move_from_to(pos, Position(constants.BOARD_WIDTH // 2, 0))

    logger.debug(f"[Turn {game_state.turn}] Sending MoveDecision: {decision}")
    return decision



def get_action_decision(game: Game) -> ActionDecision:
    game_state: GameState = game.get_game_state()
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    if game_state.get_opponent_player().name in golden_corn:
        return corn_get_action_decision(game)

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position

    if 45 <= game_state.turn < 65 and not has_planted_before and game_state.get_opponent_player().money >= my_player.money and game_state.get_opponent_player().name not in do_not_do:
        return first_actions(game)

    # Let the crop of focus be the one we have a seed for, if not just choose a random crop
    crop = max(my_player.seed_inventory, key=my_player.seed_inventory.get) \
        if sum(my_player.seed_inventory.values()) > 0 else random.choice(list(CropType))

    # Get a list of possible harvest locations for our harvest radius
    possible_harvest_locations = []
    harvest_radius = my_player.harvest_radius
    for harvest_pos in game_util.within_harvest_range(game_state, my_player.name):
        if game_state.tile_map.get_tile(harvest_pos.x, harvest_pos.y).crop.value > 0:
            possible_harvest_locations.append(harvest_pos)

    logger.debug(f"Possible harvest locations={possible_harvest_locations}")

    # If we can harvest something, try to harvest it
    if len(possible_harvest_locations) > 0:
        decision = HarvestDecision(possible_harvest_locations)
    else:
        logger.debug(f"Couldn't find anything to do, waiting for move step")
        decision = DoNothingDecision()

    logger.debug(f"[Turn {game_state.turn}] Sending ActionDecision: {decision}")
    return decision


def main():
    """
    Competitor TODO: choose an item and upgrade for your bot
    """
    game = Game(ItemType.RAIN_TOTEM, UpgradeType.LONGER_LEGS)

    while (True):
        try:
            game.update_game()
        except IOError:
            exit(-1)
        game.send_move_decision(get_move_decision(game))

        try:
            game.update_game()
        except IOError:
            exit(-1)
        game.send_action_decision(get_action_decision(game))


if __name__ == "__main__":
    main()
