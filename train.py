"""
Script for training Stock Trading Bot.

Usage:
  train.py <train-stock> [--val-stock=<val-stock>] [--strategy=<strategy>]
    [--window-size=<window-size>] [--batch-size=<batch-size>]
    [--episode-count=<episode-count>] [--model-name=<model-name>]
    [--recipient=<recipient>] [--max-position=<max-position>]
    [--save-thresh=<save-thresh>]
    [--pretrained] [--debug]

Options:
  --val-stock=<val-stock>           Used to be proprietary. Can be used to send validation data to the script.
                                    For ease of use, send in all data through <train-stock> and it will be separated
                                    for you for training.
  --strategy=<strategy>             Q-learning strategy to use for training the network. Options:
                                      `dqn` i.e. Vanilla DQN,
                                      `t-dqn` i.e. DQN with fixed target distribution,
                                      `double-dqn` i.e. DQN with separate network for value estimation. [default: t-dqn]
  --window-size=<window-size>       Size of the n-day window stock data representation
                                    used as the feature vector. [default: 10]
  --batch-size=<batch-size>         Number of samples to train on in one mini-batch
                                    during training. [default: 32]
  --episode-count=<episode-count>   Number of trading episodes to use for training. [default: 50]
  --model-name=<model-name>         Name of the pretrained model to use. [default: model_debug]
  --pretrained                      Specifies whether to continue training a previously
                                    trained model (reads `model-name`).
  --recipient=<recipient>           Recipient for email notifications on training
  --max-position=<max-position>     Maximum number of shares that the model can hold at a time (we don't all have unlimited money)
  --save-thresh=<save-thresh>       Number of episodes to save after. [default: 10]
  --debug                           Specifies whether to use verbose logs during eval operation.
"""

import math
import logging
import coloredlogs
import numpy as np
import notification as nf

from docopt import docopt
from datetime import datetime

from trading_bot.agent import Agent
from trading_bot.methods import train_model, evaluate_model
from trading_bot.utils import (
    get_stock_data,
    format_currency,
    format_position,
    show_train_result,
    switch_k_backend_device
)

logging.basicConfig(filename=f"logs/train_{datetime.today().strftime('%Y-%m-%d')}.log", level=logging.DEBUG,
                    format='[%(asctime)s] %(name)s %(levelname)s - %(message)s')


def main(train_stock, val_stock, window_size, batch_size, ep_count, max_position, save_thresh,
         strategy="t-dqn", model_name="model_debug", pretrained=False,
         debug=False):
    """ Trains the stock trading bot using Deep Q-Learning.
    Please see https://arxiv.org/abs/1312.5602 for more details.

    Args: [python train.py --help]
    """
    logging.info(f"Training model {model_name} with {ep_count} episode(s) and a max position of {max_position} with {train_stock} as the training data and {val_stock} as validation.")

    agent = Agent(window_size, strategy=strategy, pretrained=pretrained, model_name=model_name)
    
    train_data = get_stock_data(train_stock)
    val_data = get_stock_data(val_stock)

    initial_offset = val_data[1] - val_data[0]

    for episode in range(1, ep_count + 1):
        train_result = train_model(agent, episode, train_data, debug, save_thresh=save_thresh, ep_count=ep_count,
                                   max_position=max_position, batch_size=batch_size, window_size=window_size)
        val_result, _ = evaluate_model(agent, val_data, window_size, debug, max_position)
        show_train_result(train_result, val_result, initial_offset)

    # Send success email
    nf.send_training_notification(recipient, model_name)


def single_data(stock_data, window_size, batch_size, ep_count, max_position, save_thresh,
         strategy="t-dqn", model_name="model_debug", pretrained=False,
         debug=False, recipient='null@null.com'):
    """ Trains the stock trading bot using Deep Q-Learning.
    This method uses a single CSV and separates it 80/20 for training and validation
    Please see https://arxiv.org/abs/1312.5602 for more details.

    Args: [python train.py --help]
    """
    logging.info(f"Training model {model_name} with {ep_count} episode(s) and a max position of {max_position} with {stock_data} as the training and validation data")

    agent = Agent(window_size, strategy=strategy, pretrained=pretrained, model_name=model_name)

    # Separate the data passed
    all_data = get_stock_data(stock_data)
    train_data, val_data = np.split(all_data, [int(0.8*len(all_data))])

    # convert back to list
    train_data = train_data.tolist()
    val_data = val_data.tolist()

    # Calculate offset
    initial_offset = val_data[1] - val_data[0]

    for episode in range(1, ep_count + 1):
        train_result = train_model(agent, episode, train_data, debug, save_thresh=save_thresh, ep_count=ep_count,
                                   max_position=max_position, batch_size=batch_size, window_size=window_size)
        val_result, _ = evaluate_model(agent, val_data, window_size, debug, max_position)
        show_train_result(train_result, val_result, initial_offset)

    # Send success email
    nf.send_training_notification(recipient, model_name)


if __name__ == "__main__":
    args = docopt(__doc__)

    train_stock = args["<train-stock>"]
    val_stock = args["--val-stock"]
    strategy = args["--strategy"]
    window_size = int(args["--window-size"])
    batch_size = int(args["--batch-size"])
    ep_count = int(args["--episode-count"])
    model_name = args["--model-name"]
    pretrained = args["--pretrained"]
    debug = args["--debug"]
    recipient = args["--recipient"]
    save_thresh = int(args["--save-thresh"])

    try:
        max_position = int(args["--max-position"])
    except TypeError:
        max_position = math.inf

    coloredlogs.install(level="DEBUG")
    switch_k_backend_device()

    try:
        if val_stock is None:
            single_data(train_stock, window_size, batch_size, ep_count, max_position, save_thresh=save_thresh,
                        strategy=strategy, model_name=model_name,
                        pretrained=pretrained, debug=debug)
        else:
            main(train_stock, val_stock, window_size, batch_size, ep_count, max_position, save_thresh=save_thresh,
                 strategy=strategy, model_name=model_name,
                 pretrained=pretrained, debug=debug)
    except KeyboardInterrupt:
        print("Aborted!")
    except Exception as e:
        print(e)
        nf.send_error_notification(recipient, model_name, e)
