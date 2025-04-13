#!/usr/bin/env python3
import argparse
import subprocess
import sys
from collections import Counter


def run_git_command(args, cwd=None):
    """
    Execute a git command and return its output.

    Args:
        args (list): List of git command arguments.
        cwd (str, optional): Working directory for the command.

    Returns:
        str: The output of the git command.
    """
    result = subprocess.run(["git"] + args, cwd=cwd,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Git command error:", result.stderr)
        sys.exit(1)
    return result.stdout


def check_branch_exists(branch):
    """
    Check if the specified branch exists in the repository.

    Args:
        branch (str): Branch name to check.

    Exits the program if the branch does not exist.
    """
    # Используем rev-parse для проверки существования ветки.
    result = subprocess.run(["git", "rev-parse", "--verify", branch],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error: Branch '{branch}' does not exist.")
        sys.exit(1)


def generate_commit_overview(start_date=None, end_date=None, author=None, branch=None):
    """
    Generate a commit overview for the repository in the specified period.
    The overview displays the total commit count, commits grouped by author,
    and prints an ASCII commit graph in the terminal.

    Args:
        start_date (str, optional): Start date in dd-mm-yyyy format.
        end_date (str, optional): End date in dd-mm-yyyy format.
        author (str, optional): Filter commits by a specific author.
        branch (str, optional): Filter commits by branch.
    """

    def convert_date(date_str):
        """
        Convert date from dd-mm-yyyy to yyyy-mm-dd for git.
        """
        parts = date_str.split('-')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return date_str

    # Build git log arguments for commit report.
    overview_args = []
    if branch:
        overview_args.append(branch)
    overview_args += [
        "--pretty=format:%H|%an|%ad",
        "--date=format:%d-%m-%Y"
    ]
    if start_date:
        overview_args.append(f"--since={convert_date(start_date)}")
    if end_date:
        overview_args.append(f"--until={convert_date(end_date)}")
    if author:
        overview_args.append(f"--author={author}")

    output = run_git_command(["log"] + overview_args)
    if not output.strip():
        print("No commits found for the specified period.")
    else:
        total_commits = 0
        authors_counter = Counter()
        for line in output.strip().splitlines():
            parts = line.split("|")
            if len(parts) < 3:
                continue
            commit_author = parts[1]
            total_commits += 1
            authors_counter[commit_author] += 1

        print("\nCommit Overview")
        print("---------------")
        print(f"Total commits: {total_commits}")
        print("Commits by author:")
        for auth, count in authors_counter.items():
            print(f"  {auth}: {count}")

    # Build git log arguments for ASCII commit graph.
    graph_args = []
    if branch:
        graph_args.append(branch)
    graph_args += ["--graph", "--oneline"]
    if start_date:
        graph_args.append(f"--since={convert_date(start_date)}")
    if end_date:
        graph_args.append(f"--until={convert_date(end_date)}")
    if author:
        graph_args.append(f"--author={author}")

    print("\nCommit Graph")
    print("---------------------")
    graph_output = run_git_command(["log"] + graph_args)
    print(graph_output)


def main():
    parser = argparse.ArgumentParser(
        description="Git Tools: display commit overview and ASCII commit graph for the specified period."
    )
    parser.add_argument("-sd", "--start-date", type=str, help="Start date in dd-mm-yyyy format, e.g. 01-04-2025.")
    parser.add_argument("-ed", "--end-date", type=str, help="End date in dd-mm-yyyy format, e.g. 30-04-2025.")
    parser.add_argument("-a", "--author", type=str, help="Filter commits by a specific author, e.g. 'John Doe'.")
    parser.add_argument("-b", "--branch", type=str, help="Filter commits by branch, e.g. 'develop'.")

    args = parser.parse_args()

    # Verify that we are inside a git repository.
    try:
        run_git_command(["rev-parse", "--is-inside-work-tree"])
    except Exception:
        print("This command must be run inside a git repository.")
        sys.exit(1)

    if args.branch:
        check_branch_exists(args.branch)

    generate_commit_overview(args.start_date, args.end_date, args.author, args.branch)


if __name__ == "__main__":
    main()