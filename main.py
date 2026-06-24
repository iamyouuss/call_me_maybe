from src import config, Engine


def main() -> None:
    params = config()
    engine = Engine(params)
    engine.get_started()


main()
