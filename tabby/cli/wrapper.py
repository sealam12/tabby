import sys
args = sys.argv[1:]


if len(args) == 0:
    print("Tabby: An open source backend for people with a passion.")
    print("Usage: tabby [command] [arguments]")
    print("Commands")
    print("  startapp       - Generates the project directory and scaffolds starting files.")
    print("  migrations     - Migration operations for within an app")
    print("  db             - Database operations for within an app")
else:
    try:
        cmd = args[0]
        module = __import__(f"tabby.cli.commands.{cmd}", fromlist=[None])
        module.ExecuteCommand(args)
    except ImportError:
        print(f"No command named {cmd}")