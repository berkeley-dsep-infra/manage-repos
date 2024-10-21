import argparse
from . import manage_repos


def main():
    argparser = argparse.ArgumentParser()
    subparsers = argparser.add_subparsers(
        dest="command",
        help="Command to execute. Additional help is available for each command.",
    )

    argparser.add_argument(
        "-c",
        "--config",
        default="repos.txt",
        help="Path to file containing list of repositories to operate on. "
        + "Defaults to repos.txt located in the current working directory.",
    )
    argparser.add_argument(
        "-d",
        "--destination",
        default=".",
        help="Location on the filesystem of the directory containing the "
        + "managed repositories. If a repo sub-directory does not exist, it "
        + "will be created. This argument is optional, and if not provided "
        + "defaults to the current working directory.",
    )

    branch_parser = subparsers.add_parser(
        "branch",
        description="Create a new feature branch in the managed repositories.",
    )
    branch_parser.add_argument(
        "-b",
        "--branch",
        help="Name of the feature branch to create.",
    )

    clone_parser = subparsers.add_parser(
        "clone",
        description="Clone repositories in the config file and "
        + "optionally set a remote for a fork.",
    )
    clone_parser.add_argument(
        "-s",
        "--set-remote",
        action="store_true",
        help="Set the user's GitHub fork as a remote.",
    )
    clone_parser.add_argument(
        "-r",
        "--remote",
        default="origin",
        help="If --set-remote is used, override the name of the remote to "
        + "set for the fork. This is optional and defaults to 'origin'.",
    )
    clone_parser.add_argument(
        "-g",
        "--github-user",
        help="The GitHub username of the fork to set in the remote.",
    )

    patch_parser = subparsers.add_parser(
        "patch",
        description="Apply a git patch to managed repositories.",
    )
    patch_parser.add_argument("-p", "--patch", help="Path to the patch file to apply.")

    push_parser = subparsers.add_parser(
        "push",
        description="Push managed repositories to a remote.",
    )
    push_parser.add_argument("-b", "--branch", help="Name of the branch to push.")
    push_parser.add_argument(
        "-r",
        "--remote",
        help="Name of the remote to push to.  This is optional and defaults "
        + "to 'origin'.",
        default="origin",
    )

    stage_parser = subparsers.add_parser(
        "stage",
        description="Stage changes in managed repositories. This performs a "
        + "git add and commit.",
    )
    stage_parser.add_argument(
        "-f",
        "--files",
        nargs="+",
        default=["."],
        help="Space-delimited list of files to stage in the repositories. "
        + "Optional, and if left blank will default to all modified files in "
        + "the directory."
    )
    stage_parser.add_argument(
        "-m",
        "--message",
        help="Commit message to use for the changes.",
    )

    sync_parser = subparsers.add_parser(
        "sync",
        description="Sync managed repositories to the latest version using "
        + "'git rebase'. Optionally push to a remote fork.",
    )
    sync_parser.add_argument(
        "-b",
        "--branch-default",
        default="main",
        help="Default remote branch to sync to. This is optional and "
        + "defaults to 'main'.",
    )
    sync_parser.add_argument(
        "-u",
        "--upstream",
        default="upstream",
        help="Name of the parent remote to sync from. This is optional and "
        + "defaults to 'upstream'.",
    )
    sync_parser.add_argument(
        "-p",
        "--push",
        action="store_true",
        help="Push the locally synced repo to a remote fork.",
    )
    sync_parser.add_argument(
        "-r",
        "--remote",
        default="origin",
        help="The name of the remote fork to push to.  This is optional and "
        + "defaults to 'origin'.",
    )

    args = argparser.parse_args()

    print(args)
    errors = []
    if args.command == "branch":
        errors.append(manage_repos.branch(args))
    elif args.command == "clone":
        errors.append(manage_repos.clone(args))
    elif args.command == "patch":
        errors.append(manage_repos.patch(args))
    elif args.command == "push":
        errors.append(manage_repos.push(args))
    elif args.command == "stage":
        errors.append(manage_repos.stage(args))
    elif args.command == "sync":
        errors.append(manage_repos.sync(args))
    else:
        argparser.print_help()

    if any(errors):
        print("The following errors occurred during execution:")
        print(errors)
        for error in errors:
            for e in error:
                print(e)


if __name__ == "__main__":
    main()
