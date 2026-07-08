import argparse
from game_env import Env
from consts import DEFAULT_ATTRIBUTE_FILE

def parse_args():
    parser = argparse.ArgumentParser(description="Run the game with custom configuration.")
    parser.add_argument('--iterations', type=int, default=1,
                        help='Number of iterations of the game to run')
    parser.add_argument('--suspect-count', type=int, default=3,
                        help='Number of suspects')
    parser.add_argument('--max-turn-count', type=int, default=11,
                        help='Maximum number of turns')
    parser.add_argument('--attribute-file', type=str, default=DEFAULT_ATTRIBUTE_FILE,
                        help='Path to attribute file')
    parser.add_argument('--include-summarizer', action='store_true', default=False,
                        help='Include summarizer (default: False)')
    parser.add_argument('--allow-internal-thought', action='store_true', default=False,
                        help='Allow agents to have internal thought (default: False)')
    parser.add_argument('--log-file', type=str, default='game_log.txt',
                        help='log whole game log at the end of the game (default: None)')
    return parser.parse_args()

def main(conf):
    iterations = conf.pop('iterations')
    with open(conf['log_file'], 'w') as f:
        f.write("")

    for i in range(iterations):
        print(f"Game {i+1}")
        game_env = Env(conf)
        game_env.game_loop()
        if conf['log_file']:
            with open(conf['log_file'], 'a') as f:
                f.write(f"Game {i+1}\n")
                f.write(game_env.full_game_log)
                f.write("\n=================\n")

if __name__ == "__main__":
    args = parse_args()
    conf = {
        "iterations": args.iterations,
        "suspect_count": args.suspect_count,
        "max_turn_count": args.max_turn_count,
        "attribute_file": args.attribute_file,
        "include_summarizer": args.include_summarizer,
        "allow_internal_thought": args.allow_internal_thought,
        "log_file": args.log_file,
    }
    main(conf)