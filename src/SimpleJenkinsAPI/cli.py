"""Preprocessor for JCasC bundles."""
# Pylint inline disabling of unsubscriptable-object due to bug in 2.6.0

import argparse
import sys

from SimpleJenkinsAPI import JenkinsAPI, __metadata__


def _cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__metadata__.description)

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__metadata__.version}",
    )
    parser.add_argument("path", type=str, help="Endpoint to query.")
    parser.add_argument("--depth", default=0, nargs=1, type=int)
    parser.add_argument("--tree", default="", nargs=1, type=str)
    parser.add_argument("--pretty", action="store_true", help="Enable formatted output.")
    return parser.parse_args()


def run():
    options = _cli()
    print(
        JenkinsAPI().get(
            options.path, depth=options.depth, tree=options.tree, pretty=options.pretty
        )
    )


def main():
    """Entrypoint for console."""
    try:
        run()
    except Exception as err:  # pylint: disable=broad-except
        sys.exit(err)


if __name__ == "__main__":
    main()
