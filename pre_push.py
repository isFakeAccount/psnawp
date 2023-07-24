#!/usr/bin/env python3
"""Run static analysis on the project."""

import argparse
import sys
from subprocess import CalledProcessError, check_call


def do_process(args, shell=False, cwd="."):
    """Run program provided by args.

    Return ``True`` on success.

    Output failed message on non-zero exit and return False.

    Exit if command is not found.

    """
    print(f"Running: {' '.join(args)}")
    try:
        check_call(args, shell=shell, cwd=cwd)
    except CalledProcessError:
        print(f"\nFailed: {' '.join(args)}")
        return False
    except Exception as exc:
        sys.stderr.write(f"{str(exc)}\n")
        sys.exit(1)
    return True


def run_git_pull():
    """Runs the git pull command.

    Returns a statuscode of 0 if everything ran correctly. Otherwise, it will return
    statuscode 1

    """
    return do_process(["git", "pull"])


def run_static():
    """Runs the static tests.

    Returns a statuscode of 0 if everything ran correctly. Otherwise, it will return
    statuscode 1

    """
    success = True
    success &= do_process(["pre-commit", "run", "--all-files"])
    success &= do_process(["mypy", "src/psnawp_api/"])
    success &= do_process(["black", "src/psnawp_api/"])
    success &= do_process(["ruff", "src/psnawp_api/"])
    success &= do_process(["sphinx-apidoc", "-f", "-o", "docs/", "src/psnawp_api/"])
    success &= do_process(["make", "clean"], cwd="docs/")
    success &= do_process(["make", "html"], cwd="docs/")
    success &= do_process(["make", "linkcheck"], cwd="docs/")
    return success


def run_unit():
    """Runs the unit-tests.

    Follows the behavior of the static tests, where any failed tests cause pre_push.py
    to fail.

    """
    return do_process(["poetry", "run", "pytest", "--cov-config=.coveragerc", "--cov-report=html"])


def main():
    """Runs the main function.

    usage: pre_push.py [-h] [-n] [-u] [-a]

    Run static and/or unit-tests

    """
    parser = argparse.ArgumentParser(description="Run static and/or unit-tests")
    parser.add_argument(
        "-n",
        "--unstatic",
        action="store_true",
        help="Do not run static tests (black/flake8/pydocstyle/sphinx-build)",
        default=False,
    )
    parser.add_argument(
        "-u",
        "--unit-tests",
        "--unit",
        action="store_true",
        default=False,
        help="Run the unit tests",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        default=False,
        help="Run all the tests (static and unit). Overrides the unstatic argument.",
    )
    args = parser.parse_args()
    success = True
    try:
        # success &= run_git_pull()
        if success:
            if not args.unstatic or args.all:
                success &= run_static()
            if args.all or args.unit_tests:
                success &= run_unit()
    except KeyboardInterrupt:
        return int(not False)
    return int(not success)


if __name__ == "__main__":
    exit_code = main()
    print("\npre_push.py: Success!" if not exit_code else "\npre_push.py: Fail")
    sys.exit(exit_code)
