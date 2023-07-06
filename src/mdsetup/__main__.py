"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Molecular Dynamics Setup."""


if __name__ == "__main__":
    main(prog_name="mdsetup")  # pragma: no cover
