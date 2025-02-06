import click


@click.group
def cli():
    pass


@click.command
def run():
    pass


cli.add_command(run)


def main() -> None:
    print("Hello from istari!")
