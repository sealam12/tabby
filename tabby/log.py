RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'
RESET = '\033[0m'

def log(*args, **kwargs):
    print(*args, **kwargs)

def error(*args, **kwargs):
    newargs = []
    for arg in args:
        if isinstance(arg, str):
            newargs.append(f"{RED}{arg}{RESET}")
        else:
            newargs.append(arg)
    
    print(*newargs, **kwargs)

def success(*args, **kwargs):
    newargs = []
    for arg in args:
        if isinstance(arg, str):
            newargs.append(f"{GREEN}{arg}{RESET}")
        else:
            newargs.append(arg)
    
    print(*newargs, **kwargs)

def info(*args, **kwargs):
    newargs = []
    for arg in args:
        if isinstance(arg, str):
            newargs.append(f"{BLUE}{arg}{RESET}")
        else:
            newargs.append(arg)
    
    print(*newargs, **kwargs)