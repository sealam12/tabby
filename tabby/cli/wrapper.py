import sys
args = sys.argv[1:]


if len(args) == 0:
    print("Tabby: An open source backend for people with a passion.")
    print("help: Open help menu")
    print("list: List all commands")
    print("version: Show tabby version")
else:
    cmd = args[0]
    module = __import__(f"tabby.cli.commands.{cmd}", fromlist=[None])
    module.ExecuteCommand(args)