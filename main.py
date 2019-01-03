from core import Core

config = {
    "BLOCK_USERS": {"偷闲一天打个盹", },
    "DEFAULT_SONGS": [
        "煎熬",
        "烟火里的尘埃",
    ]
}


if __name__ == "__main__":
    Core(**config).run()
