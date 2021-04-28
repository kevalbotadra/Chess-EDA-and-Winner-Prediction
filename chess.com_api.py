from chessdotcom import get_player_stats
import pprint


printer = pprint.PrettyPrinter()

def get_player_ratings(username):
    data = get_player_stats(username).json
    printer.pprint(data)
    categories = ["chess_blitz", "chess_rapid", "chess_bullet"]
    for category in categories:
        print("Category:", category)
        try:
            print(f'Current: {data["stats"][category]["last"]["rating"]}')
        except:
            print("No Current Value Available")
        try:
            print(f'Best: {data["stats"][category]["best"]["rating"]}')
        except:
            print("No Best Value Available")

get_player_ratings("<insert player name>")



