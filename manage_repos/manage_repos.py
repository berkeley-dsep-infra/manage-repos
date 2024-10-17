"""
General tool for mass cloning and syncing of user image repositories.

To use this tool, copy it to a directory in your PATH or run it directly from
this directory.
"""

import subprocess
import sys
import os


def _iter_repos(args):
    """
    Iterate over the repositories in the config file.

    Returns the name, path, and URL of the repository.
    """
    with open(args.config) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name = line.split("/")[-1].replace(".git", "")
            path = os.path.join(args.destination, name)
            if not os.path.exists(path):
                if args.command != "clone":
                    print(f"Skipping {name} as it doesn't exist in {args.destination}")
                    continue
            yield name, path, line


def branch(args):
    """
    Create a new feature branch in all repositories in the config file.
    """
    errors = []
    for name, path, _ in _iter_repos(args):
        print(f"Creating and switching to feature branch {args.branch} in {name}")

        try:
            subprocess.check_call(["git", "switch", "-c", args.branch], cwd=path)
        except subprocess.CalledProcessError as e:
            error = f"Error creating branch {args.branch} in {name} in {path}: {e}"
            print(error)
            errors.append(error)
            print()
            continue

        print()

    if errors is not None:
        return errors


def clone(args):
    """
    Clone all repositories in the config file to the destination directory.

    Optionally set the the user's GitHub fork as a remote, which defaults to
    'origin'.
    """
    if not os.path.exists(args.destination):
        os.makedirs(args.destination)
        print(f"Created destination directory {args.destination}")

    errors = []
    for name, path, repo in _iter_repos(args):
        if os.path.exists(path):
            print(f"Skipping {name} as it already exists.")
            next

        if args.remote and not args.github_user:
            print(
                "Remote cannot be updated, please specify a GitHub username "
                + "for the fork to continue."
            )
            sys.exit(1)

        print(f"Cloning {name} from {repo} to {path}.")
        try:
            subprocess.check_call(["git", "clone", repo, path])
        except subprocess.CalledProcessError as e:
            error = f"Error cloning {name} from {repo} to {path}: {e}"
            print(error)
            errors.append(error)
            print()
            continue

        if args.set_remote:
            print()
            print("Updating remotes and adding fork.")
            print("Renaming origin to 'upstream'.")
            try:
                subprocess.check_call(
                    ["git", "remote", "rename", "origin", "upstream"], cwd=path
                )
            except subprocess.CalledProcessError as e:
                error = f"Error renaming origin to upstream in {name} in {path}: {e}"
                print(error)
                errors.append(error)
                print()
                continue

            remote = repo.replace("berkeley-dsep-infra", args.github_user)
            print(f"Setting remote of fork to: {remote}")
            try:
                subprocess.check_call(
                    ["git", "remote", "add", args.remote, remote], cwd=path
                )
            except subprocess.CalledProcessError as e:
                error = f"Error setting remote in {name} in {path}: {e}"
                print(error)
                errors.append(error)
                print()
                continue

        subprocess.check_call(["git", "remote", "-v"], cwd=path)
        print()

    if errors is not None:
        return errors


def patch(args):
    """
    Apply a git patch to all repositories in the config file.
    """
    if not args.patch:
        print("Please specify a patch file to apply.")
        sys.exit(1)

    if not os.path.exists(args.patch):
        print(f"Patch file {args.patch} does not exist.")
        sys.exit(1)

    errors = []
    for name, path, _ in _iter_repos(args):
        print(f"Applying patch to {name} in {path}")
        try:
            subprocess.check_call(["git", "apply", args.patch], cwd=path)
        except subprocess.CalledProcessError as e:
            error = f"Error applying patch {patch} to {name} in {path}: {e}"
            print(error)
            errors.append(error)
            print()
            continue
        print()

    if errors is not None:
        return errors


def push(args):
    """
    Push all repositories in the config file to a remote.
    """
    errors = []
    if not args.branch:
        print("Please specify a branch to push with the --branch argument.")
        sys.exit(1)

    for name, path, _ in _iter_repos(args):
        print(f"Pushing {name}/{args.branch} to {args.remote}")
        try:
            subprocess.check_call(["git", "push", args.remote, args.branch], cwd=path)
        except subprocess.CalledProcessError as e:
            error = f"Error pushing {name}/{args.branch} to {args.remote}: {e}"
            print(error)
            errors.append(error)
            print()
            continue
        print()

    if errors is not None:
        return errors


def stage(args):
    """
    Stage all repositories in the config file by adding all changes and
    committing them.
    """
    errors = []
    for name, path, repo in _iter_repos(args):
        for file in args.files:
            if file == ".":
                changed_files = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                )
                print(f"Adding all changes in {name} to staging:")
                print(changed_files.stdout)
            else:
                print(f"Adding {file} to staging in {name}.")

            try:
                subprocess.check_call(["git", "add", file], cwd=path)
            except subprocess.CalledProcessError as e:
                error = f"Error adding {name} to staging: {e}"
                print(error)
                errors.append(error)
                print()
                continue

        print(f"Committing changes in {name} with message {args.message}.")
        try:
            subprocess.check_call(
                ["git", "commit", "-m", f"{args.message}", file], cwd=path
            )
        except subprocess.CalledProcessError as e:
            error = f"Error adding {name} to staging: {e}"
            print(error)
            errors.append(error)
            print()
            continue

        print()

    if errors is not None:
        return errors


def sync(args):
    """
    Sync all repositories in the config file to the destination directory using
    rebase.

    Optionally push to the user's fork.
    """
    errors = []
    for name, path, repo in _iter_repos(args):
        print(f"Syncing {name} from {repo} to {path}.")
        subprocess.check_call(["git", "switch", args.branch_default], cwd=path)
        subprocess.check_call(["git", "fetch", "--all", "--prune"], cwd=path)
        try:
            subprocess.check_call(
                ["git", "rebase", "upstream/" + args.branch_default], cwd=path
            )
        except subprocess.CalledProcessError as e:
            error = f"Error rebasing {name} to {path}: {e}"
            print(error)
            errors.append(error)
            print()
            continue

        if args.push:
            print(f"Pushing {name} to {args.remote}.")
            try:
                subprocess.check_call(
                    ["git", "push", args.remote, args.branch_default], cwd=path
                )
            except subprocess.CalledProcessError as e:
                error = (
                    f"Error pushing {name} to {args.remote}/"
                    + f"{args.branch_default}: {e}"
                )
                print(error)
                errors.append(error)
                print()
                continue

        print()

    if errors is not None:
        return errors
