from .backend.git.tree import checkout_tree_for_build
from .core import (
    Config,
    Reporter,
    run_build,
    TerminateApplication,
)
from .git import GitRevisionParseFail


def cmd_build(args, config: Config, reporter: Reporter):
    reporter.info("Selecting git repository %s" % config.git_dir)
    try:
        build = checkout_tree_for_build(
            deploy_root=config.deploy_root,
            fetch_first=args.fetch_first,
            git_ref=args.ref,
            git_dir=config.git_dir,
            reporter=reporter,
        )
        run_build(build, config, reporter)
    except GitRevisionParseFail:
        reporter.error(f"Invalid git reference: {args.ref}")
        raise TerminateApplication(1)


def register(subparsers):
    parser = subparsers.add_parser("build", help="prepare a new build from a Git ref")
    parser.add_argument(
        "ref", help="the Git ref (commit, branch, tag) that should be built"
    )
    parser.add_argument(
        "--no-fetch",
        dest="fetch_first",
        action="store_false",
        help="don't fetch from remote before running Git commands",
    )
    parser.set_defaults(func=cmd_build)
