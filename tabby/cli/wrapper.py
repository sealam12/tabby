import sys
args = sys.argv[1:]

cmd = args[0]
module = __import__(f"tabby.cli.commands.{cmd}", fromlist=[None])
module.ExecuteCommand(args)