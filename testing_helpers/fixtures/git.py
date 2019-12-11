import configparser
import os
import pathlib
import subprocess
import textwrap

from behave import fixture

from testing_helpers.dirs import DirectoryContext

SOURCE_DIR = "source"
TARGET_DIR = "target"


class GitRepo:
    def __init__(self, dirname: pathlib.Path):
        self.dirname = dirname

    def create(self):
        os.makedirs(self.dirname, exist_ok=True)
        subprocess.run(
            ["git", "init", "."], cwd=self.dirname, check=True, capture_output=True
        )

    def run(self, args, **kwargs):
        return subprocess.run(args, cwd=self.dirname, check=True, capture_output=True)


@fixture(name="fixture.root_dir")
def root_dir(context, *args, **kwargs):
    context.root_dir = DirectoryContext()
    with context.root_dir:
        yield context.root_dir


@fixture(name="fixture.default_git_repo")
def default_git_repo(context, *args, **kwargs):
    target_dir = context.root_dir.path / TARGET_DIR
    source_dir = context.root_dir.path / SOURCE_DIR

    os.makedirs(target_dir, exist_ok=True)

    repo = GitRepo(source_dir)
    repo.create()

    with open(source_dir / "hello.txt", "w") as stream:
        stream.write("hello world\n")

    with open(source_dir / "deploy.ini", "w") as stream:
        stream.write(
            textwrap.dedent(
                f"""\
                [dirs]
                deploy = {target_dir}
                [build]
                run = true
                """
            )
        )

    repo.run(["git", "add", "."])
    repo.run(["git", "commit", "-m", "First commit"])

    yield


def update_config_file(context, action):
    source_dir = context.root_dir.path / SOURCE_DIR

    config = configparser.ConfigParser()
    filename = source_dir / "deploy.ini"

    with open(filename, "r+") as stream:
        config.read_file(stream, str(filename))

        action(config)

        stream.seek(0, 0)
        stream.truncate()
        config.write(stream)


def set_build_command(context, command: str):
    def update(config: configparser.ConfigParser):
        config.set("build", "run", command)

    update_config_file(context, update)


def set_post_deploy_command(context, command: str):
    def update(config: configparser.ConfigParser):
        if not config.has_section("post_deploy"):
            config.add_section("post_deploy")
        config.set("post_deploy", "run", command)

    update_config_file(context, update)