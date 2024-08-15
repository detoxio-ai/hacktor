    
from colorama import Fore, Style, init
from progress.bar import Bar

# Initialize colorama
init(autoreset=True)


class DummyProgressBar:
    
    def __init__(self, title:str, max:int):
        pass
    
    def next(self, max:int=None):
        pass
class BasePrinter:
    def __init__(self, silent: bool = True, verbose: bool = False):
        self.silent=silent
        self.verbose = verbose
        
    def trace(self, message):
        pass

    def info(self, message):
        pass  # Override to do nothing

    def warn(self, message):
        pass  # Override to do nothing

    def critical(self, message):
        pass  # Override to do nothing

    def heading(self, message):
        pass  # Override to do nothing

    def subheading(self, message):
        pass  # Override to do nothing

    def progress_bar(self, title, max) -> DummyProgressBar:
        return DummyProgressBar(title=title, max=max)

class ProgressBar:
    
    def __init__(self, title:str, max:int):
        self.bar = Bar(title, max=max, suffix='%(index)d / %(max)d')
    
    def next(self, max:int=None):
        if max:
            self.bar.max = max
        self.bar.next()

class Printer(BasePrinter):
    # ANSI color codes
    MID_GREY = '\033[90m'  # Mid-grey color (ANSI)
    BLUE = '\033[94m'  # Blue color
    DARK_ORANGE = '\033[38;5;208m'  # Dark orange color
    RED = Fore.RED  # Red color from colorama
    BOLD_BLUE = '\033[1;34m'  # Bold blue color
    BOLD_PURPLE = '\033[1;35m'  # Bold purple color
    
    def __init__(self, silent:bool=False, verbose:bool=False):
        super().__init__(silent=silent, verbose=verbose)

    def trace(self, message):
        if self.verbose and not self.silent:
            print(f"{self.MID_GREY} {message}{Style.RESET_ALL}")

    def info(self, message):
        if not self.silent:
            print(f"{self.MID_GREY} {message}{Style.RESET_ALL}")

    def warn(self, message):
        if not self.silent:
            print(f"{self.DARK_ORANGE} {message}{Style.RESET_ALL}")

    def critical(self, message):
        if not self.silent:
            print(f"{self.RED} {message}{Style.RESET_ALL}")

    def heading(self, message):
        if not self.silent:
            print(f"{self.BOLD_BLUE}{message}{Style.RESET_ALL}")

    def subheading(self, message):
        if not self.silent:
            print(f"{self.BOLD_PURPLE}{message}{Style.RESET_ALL}")
    
    def progress_bar(self, title, max):
        return ProgressBar(title=title, max=max)