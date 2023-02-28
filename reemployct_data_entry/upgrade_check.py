import colorama
import requests
from packaging import version

from reemployct_data_entry.__init__ import __version__


def main() -> None:
    '''
    Check for the latest version of the installed package on PyPI.
    Prompt upgrade if package is out of date.
    '''
    latest_version = get_package_latest_version("reemployct-data-entry")

    if(version.parse(latest_version) > version.parse(__version__)):
        print(colorama.Fore.BLUE)
        print("A newer version of ReEmployCT-Data-Entry is available.")
        print(f"Latest: {latest_version}")
        print(f"Installed: {__version__}")
        print(f"Run this command in your terminal to upgrade:{colorama.Style.RESET_ALL} pip install reemployct-data-entry -U")
    

def get_package_latest_version(package: str) -> str:
    response = requests.get(f'https://pypi.org/pypi/{package}/json')
    latest_version = response.json()['info']['version']
    return latest_version


if(__name__ == "__main__"):
    main()
