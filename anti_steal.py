from model.decisions.use_item_decision import UseItemDecision
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
from model.tile_map import TileMap

import random

logger = Logger()
constants = Constants()

has_planted_before = False

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

    return None


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
                 MoveDecision(Position(pos.x - 5, pos.y + 15)),
                 MoveDecision(Position(pos.x, pos.y + 15)),
                 MoveDecision(pos),
                 MoveDecision(Position(pos.x + 5, pos.y + 15)),
                 MoveDecision(Position(pos.x + 10, pos.y)),
                 MoveDecision(Position(pos.x + 2, pos.y + 1)),
                 MoveDecision(pos),
                 MoveDecision(pos),
                 MoveDecision(Position(pos.x - 13, pos.y - 7)),
                 MoveDecision(Position(pos.x - 4, pos.y - 16)),
                 MoveDecision(pos),
                 MoveDecision(pos),
                 MoveDecision(pos),
                 MoveDecision(pos),
                 MoveDecision(pos),
                 move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT)))]

    return decisions[game_state.turn - 70]


def first_actions(game: Game) -> ActionDecision:
    game_state: GameState = game.get_game_state()
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position

    actions = [DoNothingDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               BuyDecision([CropType.DUCHAM_FRUIT, CropType.POTATO], [2, 3]),
               DoNothingDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               PlantDecision([CropType.POTATO], [pos]),
               PlantDecision([CropType.POTATO], [pos]),
               PlantDecision([CropType.POTATO], [pos]),
               DoNothingDecision(),
               DoNothingDecision(),
               DoNothingDecision(),
               PlantDecision([CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT], [pos, Position(pos.x, pos.y + 1)]),
               UseItemDecision(pos),
               DoNothingDecision(),
               DoNothingDecision(),
               HarvestDecision([pos, Position(pos.x, pos.y + 1)]),
               HarvestDecision([pos, Position(pos.x, pos.y + 1)]),
               HarvestDecision([pos, Position(pos.x, pos.y + 1)])]

    return actions[game_state.turn - 70]


def get_move_decision(game: Game) -> MoveDecision:
    """
    Returns a move decision for the turn given the current game state.
    This is part 1 of 2 of the turn.

    Remember, you can only sell crops once you get to a Green Grocer tile,
    and you can only harvest or plant within your harvest or plant radius.

    After moving (and submitting the move decision), you will be given a new
    game state with both players in their updated positions.

    :param: game The object that contains the game state and other related information
    :returns: MoveDecision A location for the bot to move to this turn
    """
    game_state: GameState = game.get_game_state()
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position
    logger.info(f"Currently at {my_player.position}")

    global has_planted_before

    if game_state.turn < 70 and not has_planted_before:
        has_planted_before = opponent_has_planted(pos, game_state.tile_map)

    if game_state.turn < 70:
        if get_crop_tile(pos, game_state.tile_map) is not None:
            logger.debug("Moving towards crops")
            decision = move_from_to(pos, get_crop_tile(pos, game_state.tile_map))

        else:
            target_pos = game_state.get_opponent_player().position
            decision = move_from_to(pos, target_pos)

        return decision

    elif game_state.turn < 92 and not has_planted_before and game_state.get_opponent_player().money >= my_player.money:
        return first_moves(game)

    # If we have something to sell that we harvested, then try to move towards the green grocer tiles
    if len(my_player.harvested_inventory) > 1:
        logger.debug("Moving towards green grocer")
        decision = move_from_to(pos, Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT)))
    elif get_crop_tile(pos, game_state.tile_map) is not None:
        logger.debug("Moving towards crops")
        decision = move_from_to(pos, get_crop_tile(pos, game_state.tile_map))

    else:
        target_pos = game_state.get_opponent_player().position
        decision = move_from_to(pos, target_pos)

    logger.debug(f"[Turn {game_state.turn}] Sending MoveDecision: {decision}")
    return decision


def get_action_decision(game: Game) -> ActionDecision:
    """
    Returns an action decision for the turn given the current game state.
    This is part 2 of 2 of the turn.

    There are multiple action decisions that you can return here: BuyDecision,
    HarvestDecision, PlantDecision, or UseItemDecision.

    After this action, the next turn will begin.

    :param: game The object that contains the game state and other related information
    :returns: ActionDecision A decision for the bot to make this turn
    """
    game_state: GameState = game.get_game_state()
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position

    if 70 <= game_state.turn < 92 and not has_planted_before and game_state.get_opponent_player().money >= my_player.money:
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

    # logger.debug(f"Possible harvest locations={possible_harvest_locations}")

    # If we can harvest something, try to harvest it
    if len(possible_harvest_locations) > 0:
        decision = HarvestDecision(possible_harvest_locations)
    # # If not but we have that seed, then try to plant it in a fertility band
    # elif my_player.seed_inventory[crop] > 0 and \
    #         game_state.tile_map.get_tile(pos.x, pos.y).type != TileType.GREEN_GROCER and \
    #         game_state.tile_map.get_tile(pos.x, pos.y).type.value >= TileType.F_BAND_OUTER.value:
    #     logger.debug(f"Deciding to try to plant at position {pos}")
    #     decision = PlantDecision([crop], [pos])
    # If we don't have that seed, but we have the money to buy it, then move towards the
    # green grocer to buy it
    # elif my_player.money >= crop.get_seed_price() and \
    #         game_state.tile_map.get_tile(pos.x, pos.y).type == TileType.GREEN_GROCER:
    #     logger.debug(f"Buy 1 of {crop}")
    #     decision = BuyDecision([crop], [1])
    # # If we can't do any of that, then just do nothing (move around some more)
    else:
        logger.debug(f"Couldn't find anything to do, waiting for move step")
        decision = DoNothingDecision()

    logger.debug(f"[Turn {game_state.turn}] Sending ActionDecision: {decision}")
    return decision


# 1. Check opponent crops (if we can take them take them)
# 2. Chase other guy if in lead
# 3. Create DUCHAM_FRUIT nest

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
