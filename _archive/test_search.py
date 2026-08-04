from core.search import search_games


results = search_games(
    "007 First Light"
)


for game in results:

    print(game)