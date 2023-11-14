import argparse

from kazandb.server import RedisServer


def main(args):
    server = RedisServer(
        host=args.host,
        port=args.port,
        parser=args.parser,
        verbose=args.verbose,
    )
    server.start()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=6379)
    parser.add_argument("--parser", type=str, default="resp2")
    parser.add_argument("--verbose", type=bool, default=False)
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
