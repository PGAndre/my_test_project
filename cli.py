from pathlib import Path

from alembic import command
from alembic.config import Config
import typer as typer
import uvicorn as uvicorn


app = typer.Typer()


@app.command()
def migrate(rev_id: str = "head"):
    alembic_cfg = Config(
        Path(__file__).parent.joinpath("alembic.ini").absolute().as_posix()
    )
    command.upgrade(alembic_cfg, rev_id)


@app.command()
def api(port: int = 7001, host: str = "127.0.0.1", workers: int = 1):
    uvicorn.run("app.main:app", port=port, host=host, workers=workers, app_dir="app")


@app.command()
def rollback():
    alembic_cfg = Config(
        Path(__file__).parent.joinpath("alembic.ini").absolute().as_posix()
    )
    command.downgrade(alembic_cfg, revision="-1")


if __name__ == "__main__":
    app()
