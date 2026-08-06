def line():
    print("─" * 60)


def header():

    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              CMS FEE SCHEDULE AUTOMATION                 ║")
    print("╚════════════════════════════════════════════════════════════╝")


def step(title):

    print(f"\n▶ {title}")
    line()


def success(message):

    print(f"✓ {message}")


def summary():

    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║               AUTOMATION COMPLETED                       ║")
    print("╚════════════════════════════════════════════════════════════╝")