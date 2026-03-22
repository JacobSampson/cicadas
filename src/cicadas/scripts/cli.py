# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

"""
Cicadas CLI - Main entry point for the cicadas command.

This module provides the main CLI interface that dispatches to individual
script commands. Each script can also be invoked directly via its own
entry point (e.g., cicadas-init, cicadas-status).
"""

import argparse
import sys
from pathlib import Path

# Add scripts directory to path for relative imports used by scripts
_scripts_dir = Path(__file__).parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))


def main():
    """Main entry point for the cicadas CLI."""
    parser = argparse.ArgumentParser(
        prog="cicadas",
        description="Cicadas: Sustainable, Spec-Driven Development (SDD) for human-AI teams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  init              Initialize Cicadas in the current project
  status            Show current initiatives, branches, and signals
  check             Check for conflicts and updates
  kickoff           Promote drafts to active and create initiative branch
  branch            Register a feature branch
  signal            Broadcast a change to peer branches
  archive           Archive completed initiative or branch specs
  prune             Rollback and restore specs to drafts
  abort             Context-aware escape from current branch
  history           Generate HTML timeline from archive and index
  open-pr           Open a pull request from the current branch
  review            Check review.md verdict
  validate-skill    Validate an Agent Skill against the spec
  publish-skill     Publish a skill to its destination

Examples:
  cicadas init
  cicadas status
  cicadas kickoff my-feature --intent "Add user authentication"
  cicadas branch feat/auth --intent "Auth module" --modules "auth,users"
""",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Command to run",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments for the command",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    command_map = {
        "init": _run_init,
        "status": _run_status,
        "check": _run_check,
        "kickoff": _run_kickoff,
        "branch": _run_branch,
        "signal": _run_signal,
        "archive": _run_archive,
        "prune": _run_prune,
        "abort": _run_abort,
        "history": _run_history,
        "open-pr": _run_open_pr,
        "review": _run_review,
        "validate-skill": _run_validate_skill,
        "publish-skill": _run_publish_skill,
        "lifecycle": _run_lifecycle,
        "update-index": _run_update_index,
    }

    if args.command not in command_map:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        print(f"Available commands: {', '.join(sorted(command_map.keys()))}", file=sys.stderr)
        return 1

    return command_map[args.command](args.args)


def _get_version():
    """Get the package version."""
    try:
        from cicadas import __version__
        return __version__
    except ImportError:
        return "unknown"


def _run_init(args):
    """Run the init command."""
    from init import init_cicadas
    from utils import get_project_root
    init_cicadas(get_project_root())
    return 0


def _run_status(args):
    """Run the status command."""
    from status import show_status
    show_status()
    return 0


def _run_check(args):
    """Run the check command."""
    import argparse

    from check import check_conflicts

    parser = argparse.ArgumentParser(prog="cicadas check")
    parser.add_argument("--initiative", help="Check specific initiative")
    parsed = parser.parse_args(args)

    check_conflicts(initiative_name=parsed.initiative)
    return 0


def _run_kickoff(args):
    """Run the kickoff command."""
    import argparse

    from kickoff import kickoff

    parser = argparse.ArgumentParser(prog="cicadas kickoff")
    parser.add_argument("name", help="Initiative name")
    parser.add_argument("--intent", required=True, help="Initiative intent/description")
    parsed = parser.parse_args(args)

    kickoff(parsed.name, parsed.intent)
    return 0


def _run_branch(args):
    """Run the branch command."""
    import argparse

    from branch import create_branch

    parser = argparse.ArgumentParser(prog="cicadas branch")
    parser.add_argument("name", help="Branch name")
    parser.add_argument("--intent", required=True, help="Branch intent/description")
    parser.add_argument("--modules", default="", help="Comma-separated module list")
    parser.add_argument("--initiative", help="Parent initiative name")
    parser.add_argument("--from", dest="from_branch", help="Parent branch to fork from")
    parser.add_argument("--worktree-dir", dest="worktree_dir", help="Override worktree directory")
    parser.add_argument("--no-worktree", action="store_true", help="Force plain branch")
    parsed = parser.parse_args(args)

    create_branch(
        parsed.name,
        parsed.intent,
        parsed.modules,
        initiative=parsed.initiative,
        from_branch=parsed.from_branch,
        worktree_dir_override=parsed.worktree_dir,
        no_worktree=parsed.no_worktree,
    )
    return 0


def _run_signal(args):
    """Run the signal command."""
    import argparse

    from signalboard import send_signal

    parser = argparse.ArgumentParser(prog="cicadas signal")
    parser.add_argument("message", help="Signal message")
    parser.add_argument("--initiative", help="Target initiative")
    parsed = parser.parse_args(args)

    send_signal(parsed.message, parsed.initiative)
    return 0


def _run_archive(args):
    """Run the archive command."""
    import argparse

    from archive import archive

    parser = argparse.ArgumentParser(prog="cicadas archive")
    parser.add_argument("name", help="Name to archive")
    parser.add_argument("--type", choices=["branch", "initiative"], default="initiative")
    parsed = parser.parse_args(args)

    archive(parsed.name, parsed.type)
    return 0


def _run_prune(args):
    """Run the prune command."""
    import argparse

    from prune import prune

    parser = argparse.ArgumentParser(prog="cicadas prune")
    parser.add_argument("name", help="Name to prune")
    parser.add_argument("--type", choices=["branch", "initiative"], default="branch")
    parsed = parser.parse_args(args)

    prune(parsed.name, parsed.type)
    return 0


def _run_abort(args):
    """Run the abort command."""
    from abort import main as abort_main
    abort_main()
    return 0


def _run_history(args):
    """Run the history command."""
    import argparse
    from pathlib import Path

    from history import generate

    parser = argparse.ArgumentParser(prog="cicadas history")
    parser.add_argument("--output", help="Output path for HTML file")
    parsed = parser.parse_args(args)

    output_path = Path(parsed.output) if parsed.output else None
    out = generate(output_path)
    print(f"Generated: {out}")
    return 0


def _run_open_pr(args):
    """Run the open-pr command."""
    import argparse

    from open_pr import open_pr

    parser = argparse.ArgumentParser(prog="cicadas open-pr")
    parser.add_argument("--base", help="Base branch for PR")
    parsed = parser.parse_args(args)

    open_pr(base_branch=parsed.base)
    return 0


def _run_review(args):
    """Run the review command."""
    import argparse

    from review import check_review

    parser = argparse.ArgumentParser(prog="cicadas review")
    parser.add_argument("--initiative", help="Initiative name")
    parsed = parser.parse_args(args)

    result = check_review(initiative=parsed.initiative)
    return result


def _run_validate_skill(args):
    """Run the validate-skill command."""
    # Reconstruct sys.argv for the script's argparse
    import sys

    from validate_skill import main as validate_main
    old_argv = sys.argv
    sys.argv = ["cicadas validate-skill"] + args
    try:
        validate_main()
        return 0
    except SystemExit as e:
        return e.code if e.code else 0
    finally:
        sys.argv = old_argv


def _run_publish_skill(args):
    """Run the publish-skill command."""
    # Reconstruct sys.argv for the script's argparse
    import sys

    from skill_publish import main as publish_main
    old_argv = sys.argv
    sys.argv = ["cicadas publish-skill"] + args
    try:
        publish_main()
        return 0
    except SystemExit as e:
        return e.code if e.code else 0
    finally:
        sys.argv = old_argv


def _run_lifecycle(args):
    """Run the lifecycle command."""
    import argparse

    from create_lifecycle import create_lifecycle

    parser = argparse.ArgumentParser(prog="cicadas lifecycle")
    parser.add_argument("name", help="Initiative name")
    parser.add_argument("--pr-specs", action="store_true")
    parser.add_argument("--pr-initiatives", action="store_true")
    parser.add_argument("--pr-features", action="store_true")
    parser.add_argument("--pr-tasks", action="store_true")
    parser.add_argument("--no-pr-specs", action="store_true")
    parser.add_argument("--no-pr-initiatives", action="store_true")
    parser.add_argument("--no-pr-features", action="store_true")
    parser.add_argument("--no-pr-tasks", action="store_true")
    parsed = parser.parse_args(args)

    create_lifecycle(
        parsed.name,
        pr_specs=parsed.pr_specs,
        pr_initiatives=parsed.pr_initiatives,
        pr_features=parsed.pr_features,
        pr_tasks=parsed.pr_tasks,
        no_pr_specs=parsed.no_pr_specs,
        no_pr_initiatives=parsed.no_pr_initiatives,
        no_pr_features=parsed.no_pr_features,
        no_pr_tasks=parsed.no_pr_tasks,
    )
    return 0


def _run_update_index(args):
    """Run the update-index command."""
    import argparse

    from update_index import update_index

    parser = argparse.ArgumentParser(prog="cicadas update-index")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--summary", required=True, help="Summary of changes")
    parsed = parser.parse_args(args)

    update_index(parsed.branch, parsed.summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
