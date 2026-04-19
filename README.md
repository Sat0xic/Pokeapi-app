# PokeAPI App

A command-line Python app that retrieves data on any Pokemon by name using the [PokéAPI](https://pokeapi.co/).

## Features
- Displays National Pokédex number, type, height, weight, and abilities
- Shows base stats with a visual bar representation
- Optional evolution chain lookup

- ## Example Output

  
- Enter Pokemon Name: pikachu
Pokemon: pikachu
National Pokedex # 25
Type: electric
Height: 4.0
Weight: 60.0
Ability: static
Hidden: lightning-rod
hp 35
***
attack 55
*****
defense 40
****
special-attack 50
*****
special-defense 50
*****
speed 90
*********
Would you like the evolution(s)? Y/N: y
pichu --> pikachu --> raichu


## Technologies Used
- Python
- [requests](https://pypi.org/project/requests/) library
- [PokéAPI](https://pokeapi.co/) (free, open REST API)

## How to Run
1. Install dependencies:
2. pip install requests

## What I Learned
- Making HTTP requests to a REST API using `requests`
- Parsing and navigating nested JSON responses
- Chaining multiple API calls to retrieve evolution data
