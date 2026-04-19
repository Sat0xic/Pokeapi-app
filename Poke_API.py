import requests
import json


#program designed to learn api request fetching data and chaining api request
def main():
    print("\nHello, this programs function is to take a pokemons name and return it's information\n")
    name = input("Enter Pokemon Name: ").lower()
    while True:
        if get_pokemon_info(name):
            break
        print("Pokemon not found")
        name = input("Enter Pokemon Name: ").lower()
    evolve = input("Would you like the evolution(s)? Y/N: ").lower()
    if evolve == "y":
        print(get_evolution(name))
    else:
        print("Goodbye")



def get_pokemon_info(pokemon_name): # function used to fetch data using api request
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}") #send api request to pokeapi
    if response.status_code == 200: # status code 200 is all good
        data = response.json() # store the response from the api request in a python dictionary using .json() in data
        bar = "*"
        #print(json.dumps(data, indent=4)) this prints the converted python dictionary and makes it readable, used for debugging and planning
        print(f"Pokemon: {data["name"]}") #data is the whole dictionary['name'] is the key --> prints the name value
        print(f"National Pokedex # {data["id"]}")
        print(f"Type: {data['types'][0]['type']['name']}")#types is a list here, index into [0],containing [type],  this a dictionary containing ['name'] and ['url']

        try:
            print(f"Type 2: {data['types'][1]['type']['name']}")
        except IndexError:
            pass

        print(f"Height: {float(data['height'])}")
        print(f"Weight: {float(data['weight'])}")
        print(f"Ability: {data['abilities'][0]['ability']['name']}")

        try:
            print(f"Hidden: {data['abilities'][1]['ability']['name']}")
        except IndexError:
            pass

        for stat in data['stats']:
            print(stat['stat']['name'] + " " + str(stat['base_stat']))
            print(stat['base_stat']//10 * bar)

        return True

    return False

def get_evolution(pokemon_name): # function used to chain api request
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name}") # not a listed url but a pattern used to lessen api request in chaining
    if response.status_code == 200:
        data = response.json()
        response2 = requests.get(data['evolution_chain']['url']) # second api url in chaining
        data2 = response2.json()
        name = data2['chain']['species']['name']


        try:
            first_evolution = data2['chain']['evolves_to'][0]['species']['name']
        except IndexError:
            return f"{name} --> no evolution"

        try:
            second_evolution = data2['chain']['evolves_to'][0]['evolves_to'][0]['species']['name']
        except IndexError:
            return f"{name} --> {first_evolution}"

        return f"{name} --> {first_evolution} --> {second_evolution}"

    return None


if __name__ == "__main__":
    main()
