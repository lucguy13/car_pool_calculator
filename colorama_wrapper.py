from colorama import init
from colorama import Fore, Back, Style

class Colour():
    def green(self, text):
        return (Fore.GREEN + text + Style.RESET_ALL)
    def red(self, text):
        return (Fore.RED + text + Style.RESET_ALL)
    def yellow(self, text):
        return (Fore.YELLOW + text + Style.RESET_ALL)
    def blue(self, text):
        return (Fore.BLUE + text + Style.RESET_ALL)


if __name__ == "__main__":
    col = Colour()
    print(col.green('some green text'))