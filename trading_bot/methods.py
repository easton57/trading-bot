import os
import math
import logging
import numpy as np

from tqdm import tqdm
from datetime import datetime

from .utils import (
    format_currency,
    format_position
)
from .ops import (
    get_state
)


def train_model(agent, episode, data, debug, save_thresh=10, ep_count=100, batch_size=32, window_size=10, max_position=math.inf):
    logging.basicConfig(filename=f"logs/train_{datetime.today().strftime('%Y-%m-%d')}.log", level=logging.DEBUG, force=True,
                        format='[%(asctime)s] %(name)s %(levelname)s - %(message)s')
    logging.info('* * * * * * * * * * * * * * * * * * * * * * *')
    logging.info(f'* * * Starting Training on Episode {episode} * * *')
    logging.info('* * * * * * * * * * * * * * * * * * * * * * *')

    total_profit = 0
    data_length = len(data) - 1

    agent.inventory = []
    avg_loss = []

    state = get_state(data, 0, window_size + 1)

    for t in tqdm(range(data_length), total=data_length, leave=True, desc='Episode {}/{}'.format(episode, ep_count)):
        reward = 0
        next_state = get_state(data, t + 1, window_size + 1)

        # select an action
        action = agent.act(state)

        # BUY
        if action == 1 and len(agent.inventory) < max_position:
            agent.inventory.append(data[t])

            if debug:
                logging.debug("Buy at: {}".format(format_currency(data[t])))
                logging.debug("Position size is now: {}".format(len(agent.inventory)))

        # SELL
        elif action == 2 and len(agent.inventory) > 0:
            bought_price = agent.inventory.pop(0)
            delta = data[t] - bought_price
            reward = delta  # max(delta, 0)
            total_profit += delta

            if debug:
                logging.debug("Sell at: {} | Position: {}".format(
                    format_currency(data[t]), format_position(data[t] - bought_price)))
                logging.debug("Position size is now: {}".format(len(agent.inventory)))

        # HOLD
        else:
            pass

        done = (t == data_length - 1)
        agent.remember(state, action, reward, next_state, done)

        if len(agent.memory) > batch_size:
            loss = agent.train_experience_replay(batch_size)
            avg_loss.append(loss)

        state = next_state

    if episode % save_thresh == 0:
        agent.save(episode)

    return episode, ep_count, total_profit, np.mean(np.array(avg_loss))


def evaluate_model(agent, data, window_size, debug, max_position=math.inf):
    logging.basicConfig(filename=f"logs/eval_{datetime.today().strftime('%Y-%m-%d')}.log", level=logging.DEBUG, force=True,
                        format='[%(asctime)s] %(name)s %(levelname)s - %(message)s')
    logging.info('* * * * * * * * * * * * * * * * * * * * * * *')
    logging.info('* * * * * *  Starting Evaluation  * * * * * *')
    logging.info('* * * * * * * * * * * * * * * * * * * * * * *')

    total_profit = 0
    data_length = len(data) - 1

    history = []
    agent.inventory = []
    
    state = get_state(data, 0, window_size + 1)

    for t in range(data_length):        
        reward = 0
        next_state = get_state(data, t + 1, window_size + 1)
        
        # select an action
        action = agent.act(state, is_eval=True)

        # BUY
        if action == 1 and len(agent.inventory) < max_position:
            agent.inventory.append(data[t])

            history.append((data[t], "BUY"))

            if debug:
                logging.debug("Buy at: {}".format(format_currency(data[t])))
                logging.debug("Position size is now: {}".format(len(agent.inventory)))
        
        # SELL
        elif action == 2 and len(agent.inventory) > 0:
            bought_price = agent.inventory.pop(0)
            delta = data[t] - bought_price
            reward = delta  # max(delta, 0)
            total_profit += delta

            history.append((data[t], "SELL"))

            if debug:
                logging.debug("Sell at: {} | Position: {}".format(
                    format_currency(data[t]), format_position(data[t] - bought_price)))
                logging.debug("Position size is now: {}".format(len(agent.inventory)))
        # HOLD
        else:
            history.append((data[t], "HOLD"))

        done = (t == data_length - 1)
        agent.memory.append((state, action, reward, next_state, done))

        state = next_state
        if done:
            logging.info('* * * * * * * * * * * * * * * * * * * * * * *')
            logging.info('* * * * * *  Evaluation Complete  * * * * * *')
            logging.info('* * * * * * * * * * * * * * * * * * * * * * *')

            return total_profit, history
