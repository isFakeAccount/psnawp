#!/usr/bin/env python
"""Provides simple way to run formatter/linter/static analysis/tests on the project."""

import argparse
import sys
from subprocess import CalledProcessError, check_call


def do_process(args: list[str], cwd: str = ".") -> bool:
    """
    Run program provided by args.

    Returns ``True`` upon success.

    Output failed message on non-zero exit and return False.

    Exit if command is not found.

    """
    print(f"Running: {' '.join(args)}")
    try:
        check_call(args, shell=False, cwd=cwd)
    except CalledProcessError:
        print(f"\nFailed: {' '.join(args)}")
        return False
    except Exception as exc:
        print(f"{exc!s}\n", file=sys.stderr)
        raise SystemExit(1) from exc
    return True


def run_static() -> bool:
    """
    Runs the static tests.

    Returns a statuscode of 0 if everything ran correctly. Otherwise, it will return statuscode 1

    """
    success = True
    success &= do_process(["poetry", "run", "pre-commit", "run", "--all-files"])

    success &= do_process(["poetry", "run", "mypy", "src/psnawp_api/"])
    success &= do_process(["pyright", "src/psnawp_api/"])

    success &= do_process(["poetry", "run", "ruff", "format", "src/psnawp_api/"])
    success &= do_process(["poetry", "run", "ruff", "format", "tests/"])

    success &= do_process(
        ["poetry", "run", "ruff", "check", "src/psnawp_api/", "--fix"],
    )
    success &= do_process(
        ["poetry", "run", "sphinx-apidoc", "-f", "-o", "docs/", "src/psnawp_api/"],
    )
    success &= do_process(["make", "clean"], cwd="docs/")
    success &= do_process(["make", "html"], cwd="docs/")
    success &= do_process(["make", "linkcheck"], cwd="docs/")
    return success


def run_unit() -> bool:
    """
    Runs the unit-tests.

    Follows the behavior of the static tests, where any failed tests cause pre_push.py to fail.

    """
    return do_process(
        ["poetry", "run", "pytest", "--cov-config=.coveragerc", "--cov-report=html"],
    )


def main() -> int:
    """
    Runs the main function.

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
