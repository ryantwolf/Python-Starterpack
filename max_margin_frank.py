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


logger = Logger()
constants = Constants()

has_planted_before = False

ties_list = ["venkat", "the_patriots"]

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
            moves_left -= (end.y - start.y)
        else:
            if end.y > start.y:
                y = start.y + moves_left
                moves_left = 0
            else:
                y = start.y - moves_left
                moves_left = 0

    return MoveDecision(Position(x, y))


def get_crop_tile(pos: Position, tile_map: TileMap) -> Position:
    for x in range(tile_map.map_width):
        for y in range(tile_map.map_height):
            if tile_map.get_tile(x, y).crop.value > 0 and tile_map.get_tile(x, y).scarecrow_effect is not None:
                return Position(x, y)

    return pos

def opponent_has_planted(pos: Position, tile_map: TileMap) -> bool:
    for x in range(tile_map.map_width):
        for y in range(tile_map.map_height):
            if tile_map.get_tile(x, y).crop.value > 0:
                return True

    return False

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

def get_move_decision(game: Game) -> MoveDecision:
    game_state: GameState = game.get_game_state()
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    opponent: Player = game_state.get_opponent_player()
    pos: Position = my_player.position
    logger.info(f"Currently at {my_player.position}")

    global has_planted_before

    if game_state.turn < 45 and not has_planted_before:
        has_planted_before = opponent_has_planted(pos, game_state.tile_map)
    elif 45 <= game_state.turn < 65 and not has_planted_before and opponent.money >= my_player.money and opponent.name not in ties_list:
        return first_moves(game)

    # If we have items, go sell them
    if len(my_player.harvested_inventory) > 5:
        decision = MoveDecision(Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT)))
    else:
        # Go towards nearest crop
        target_pos = get_crop_tile(pos, game_state.tile_map)
        if target_pos.x == pos.x and target_pos.y == pos.y:
            target_pos = game_state.get_opponent_player().position
        decision = move_from_to(pos, target_pos)

    if game_state.turn >= 175:
        return move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT)))

    logger.debug(f"[Turn {game_state.turn}] Sending MoveDecision: {decision}")
    return decision



def get_action_decision(game: Game) -> ActionDecision:
    game_state: GameState = game.get_game_state()
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position
    opponent: Player = game_state.get_opponent_player()

    if 45 <= game_state.turn < 65 and not has_planted_before and opponent.money >= my_player.money and opponent.name not in ties_list:
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