from src import config, Engine


def main() -> None:
    params = config()
    engine = Engine(params)
    engine.get_started()


if __name__ == "__main__":
    main()
