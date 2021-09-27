# from typing_extensions import ParamSpec
# from model.crop import Crop
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

def buy_d(ct):
    return BuyDecision([CropType.DUCHAM_FRUIT], [ct])

def harv(x,y):
    return HarvestDecision([Position(i, y) for i in range(x - 1, x + 2)] + [Position(x, j) for j in range(y - 1, y +2)])

def wait(n, m=None, a=None):
    for i in range(n):
        if m is not None:
            m.append(None)
        if a is not None: 
            a.append(None)

logger = Logger()
constants = Constants()

start_x = 0
movements = [(15, 0), (15, 0), (-2, 3), (-2, 3)]
actions = [None, buy_d(3), DoNothingDecision(), DoNothingDecision()]

wait(24, movements)
wait(17, actions)

actions1 = [PlantDecision([CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT], [Position(-1, 3), Position(-2,3), Position(-3, 3)])]
wait(5, actions1)
actions1.append(harv(-2, 3))#HarvestDecision([Position(-1, 3), Position(-2,3), Position(-3, 3)]))

actions = actions + actions1

movements += [(15,0), (15, 0), (-2, 6), (-2, 6), None]
actions += [None, buy_d(4), None, None, PlantDecision([CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT], [Position(-1, 6), Position(-2,6), Position(-3, 6), Position(-2, 7)])]

wait(5, movements, actions)
actions.append(harv(-2, 6))
wait(1, movements)

movements += [(15,0), (15, 0), (-2, 10), (-2, 10), (-2, 10), None]
actions += [None, buy_d(5), None, None, None, PlantDecision([CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT], [Position(-1, 10), Position(-2,10), Position(-3, 10), Position(-2, 11), Position(-2, 9)])]

wait(5, movements, actions)
actions.append(harv(-2, 10))
wait(1, movements)

movements += [(15, 0), (15,0), (15, 0), (-2, 15), (-2, 15), (-2, 15), None, (-3, 15), (-2, 15)]
actions += [None, None, buy_d(7), None, None, None, PlantDecision([CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT], [Position(-1, 15), Position(-2,15), Position(-3, 15), Position(-2, 16), Position(-2, 14)]), PlantDecision([CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT], [Position(-3, 16), Position(-4, 15)]), None]

wait(4, movements, actions)
actions.append(harv(-2, 15))
wait(1, movements)
movements.append((-3, 15))
actions.append(harv(-3, 15))

y = 20
movements += [(15, 0), (15,0), (15, 0), (-2, y), (-2, y), (-2, y), (-2, y), None, (-3, y), (-2, y)]
actions += [None, None, buy_d(8), None, None, None, None, PlantDecision([CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT], [Position(-1, y), Position(-2,y), Position(-3, y), Position(-2, y+1), Position(-2, y-1)]), PlantDecision([CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT, CropType.DUCHAM_FRUIT], [Position(-3, y+1), Position(-4, y), Position(-3, y-1)]), None]

wait(4, movements, actions)
actions.append(harv(-2, y))
wait(1, movements)
movements.append((-3, y))
actions.append(harv(-3, y))

movements += [(15, 0), (15,0), (15, 0), (15,0)]
wait(3, actions)
actions += [BuyDecision([CropType.GOLDEN_CORN], [1])]

movements += [(-2, 25)]*4
wait(3, actions)
actions += [PlantDecision([CropType.GOLDEN_CORN], [Position(-2, 25)])]

wait(3, movements, actions)

actions += [harv(-2, 25)]
movements += [None] + [(15,0)] * 4

wait(3, actions)
# Buying second round of golden corn
actions += [BuyDecision([CropType.GOLDEN_CORN], [2])]

movements += [(-2, 30)]*5
wait(4, actions)
actions += [PlantDecision([CropType.GOLDEN_CORN, CropType.GOLDEN_CORN], [Position(-2, 30), Position(-3, 30)])]

wait(3, movements,actions)
actions += [harv(-2, 30)]
movements += [None] + [(15,0)] * 5





def move_from_to(start: Position, end: Position):
    moves_left = constants.MAX_MOVEMENT
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
    # logger.debug(str(x) + ' ' + str(y) + str(moves_left))
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
    global start_x
    game_state: GameState = game.get_game_state()
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")
    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position
    logger.info(f"Currently at {my_player.position}")

    if game_state.turn == 1:
        start_x = my_player.position.x
        logger.debug(str(start_x))

    turn = game_state.turn -1
    if turn >= len(movements):
        return MoveDecision(Position(pos.x, pos.y))
    else:
        if (movements[turn] is None):
            return MoveDecision(Position(pos.x, pos.y))
        goal_pos = Position(movements[turn][0], movements[turn][1])
        if goal_pos.x <= -1:
            if start_x == 0:
                goal_pos.x = - goal_pos.x 
            else:
                goal_pos.x = 30 + goal_pos.x
        logger.debug(str(goal_pos))
        decision = move_from_to(my_player.position, goal_pos)
        
    # If we have something to sell that we harvested, then try to move towards the green grocer tiles
    # if random.random() < 0.5 and \
            # (sum(my_player.seed_inventory.values()) == 0 or
             # len(my_player.harvested_inventory)):
        # logger.debug("Moving towards green grocer")
        # decision = MoveDecision(Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT)))
    # # If not, then move randomly within the range of locations we can move to
    # else:
        # pos = random.choice(game_util.within_move_range(game_state, my_player.name))
        # logger.debug("Moving randomly")
    #     decision = MoveDecision(pos)

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
    # Let the crop of focus be the one we have a seed for, if not just choose a random crop
    crop = max(my_player.seed_inventory, key=my_player.seed_inventory.get) \
        if sum(my_player.seed_inventory.values()) > 0 else random.choice(list(CropType))

    turn = game_state.turn - 1
    if turn >= len(actions):
        return DoNothingDecision();
    else:
        if actions[turn] is None:
            return DoNothingDecision()

        decision = actions[turn]
        if type(decision) == PlantDecision or type(decision) == HarvestDecision:
            pos_list = decision.coords if type(decision) == PlantDecision else decision.positions
            for i in range(len(pos_list)):
                goal_pos = pos_list[i] 
                if goal_pos.x <= -1:
                    if start_x == 0:
                        goal_pos.x = - goal_pos.x
                    else:
                        goal_pos.x = 30 + goal_pos.x       
        
    # Get a list of possible harvest locations for our harvest radius
    # possible_harvest_locations = []
    # harvest_radius = my_player.harvest_radius
    # for harvest_pos in game_util.within_harvest_range(game_state, my_player.name):
        # if game_state.tile_map.get_tile(harvest_pos.x, harvest_pos.y).crop.value > 0:
            # possible_harvest_locations.append(harvest_pos)

    # logger.debug(f"Possible harvest locations={possible_harvest_locations}")

    # # If we can harvest something, try to harvest it
    # if len(possible_harvest_locations) > 0:
        # decision = HarvestDecision(possible_harvest_locations)
    # # If not but we have that seed, then try to plant it in a fertility band
    # elif my_player.seed_inventory[crop] > 0 and \
            # game_state.tile_map.get_tile(pos.x, pos.y).type != TileType.GREEN_GROCER and \
            # game_state.tile_map.get_tile(pos.x, pos.y).type.value >= TileType.F_BAND_OUTER.value:
        # logger.debug(f"Deciding to try to plant at position {pos}")
        # decision = PlantDecision([crop], [pos])
    # # If we don't have that seed, but we have the money to buy it, then move towards the
    # # green grocer to buy it
    # elif my_player.money >= crop.get_seed_price() and \
        # game_state.tile_map.get_tile(pos.x, pos.y).type == TileType.GREEN_GROCER:
        # logger.debug(f"Buy 1 of {crop}")
        # decision = BuyDecision([crop], [1])
    # # If we can't do any of that, then just do nothing (move around some more)
    # else:
        # logger.debug(f"Couldn't find anything to do, waiting for move step")
    #     decision = DoNothingDecision()

    logger.debug(f"[Turn {game_state.turn}] Sending ActionDecision: {decision}")
    return decision


def main():
    """
    Competitor TODO: choose an item and upgrade for your bot
    """
    game = Game(ItemType.COFFEE_THERMOS, UpgradeType.SPYGLASS)

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
