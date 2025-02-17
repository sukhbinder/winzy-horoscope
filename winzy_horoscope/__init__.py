import winzy
import requests
from colorama import Fore, Style, init
from functools import lru_cache
from datetime import datetime, timedelta

# Initialize colorama
init(autoreset=True)

# Cache expiration time
CACHE_EXPIRATION = timedelta(minutes=60)

# Dictionary to track cache timestamps
cache_timestamps = {}


@lru_cache(maxsize=32)
def get_daily_horoscope_cached(sign: str, day: str) -> dict:
    """
    Cached version of the get_daily_horoscope function.
    """
    # Store the timestamp of the cache entry
    cache_timestamps[(sign, day)] = datetime.now()

    # Fetch the horoscope
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}
    response = requests.get(url, params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"status": "error", "message": "Failed to fetch data"}


def get_daily_horoscope(sign: str, day: str) -> dict:
    """
    Wrapper to handle LRU cache expiration.
    """
    cache_key = (sign, day)

    # Check if the cache has expired
    if cache_key in cache_timestamps:
        cached_time = cache_timestamps[cache_key]
        if datetime.now() - cached_time > CACHE_EXPIRATION:
            # Clear expired entry
            get_daily_horoscope_cached.cache_clear()
            cache_timestamps.pop(cache_key, None)

    # Call the cached function
    return get_daily_horoscope_cached(sign, day)


def display_horoscope(data: dict):
    """
    Display horoscope data in a nicely formatted way with colors.
    """
    if data.get("success", False):
        horoscope_data = data["data"]
        print(f"{Fore.GREEN}{Style.BRIGHT}Horoscope for {horoscope_data['date']}:\n")
        print(f"{Fore.CYAN}{horoscope_data['horoscope_data']}\n")
    else:
        print(f"{Fore.RED}Error: {data.get('message', 'Unknown error occurred')}")


def create_parser(subparser):
    valid_signs = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]
    parser = subparser.add_parser(
        "horoscope",
        description="Get daily Horoscope using https://horoscope-app-api.vercel.app by Ashutosh Krishna",
    )
    # Add subprser arguments here.
    parser.add_argument(
        "sign",
        type=str,
        choices=valid_signs,
        help="Zodiac sign (e.g., Aries, Taurus, Gemini, etc.). Choose from the available options.",
    )
    parser.add_argument(
        "--day",
        type=str,
        default="TODAY",
        help='Date in format (YYYY-MM-DD) OR "TODAY" OR "TOMORROW" OR "YESTERDAY". Default is "TODAY".',
    )
    return parser


class WinzyPlugin:
    """ Get daily Horoscope using https://horoscope-app-api.vercel.app by Ashutosh Krishna """

    __name__ = "horoscope"

    @winzy.hookimpl
    def register_commands(self, subparser):
        parser = create_parser(subparser)
        parser.set_defaults(func=self.run)

    def run(self, args):
        sign = args.sign
        day = (
            args.day.upper()
            if args.day.upper() in {"TODAY", "TOMORROW", "YESTERDAY"}
            else args.day
        )

        data = get_daily_horoscope(sign, day)
        if data.get("status") == 200:
            display_horoscope(data)
        else:
            print(
                f"{Fore.RED}Error fetching data: {data.get('message', 'Unknown error occurred')}"
            )

    def hello(self, args):
        # this routine will be called when "winzy horoscope is called."
        print("Hello! This is an example ``winzy`` plugin.")


horoscope_plugin = WinzyPlugin()
