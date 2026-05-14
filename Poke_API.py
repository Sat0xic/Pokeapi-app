from flask import Flask,render_template,request,redirect,url_for,jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import create_engine,String,Integer,Float,select
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session
import requests
import json

app = Flask(__name__)
#app.config is a dictionary that Flask uses to store settings for your app
#SECRET_KEY is a string that Flask uses to cryptographically sign session data
#A user logs in, Flask creates a cookie and stamps it with a signature derived from the SECRET_KEY
#That cookie gets sent to the user's browser
#On every future request, Flask checks the stamp
#like an automatic password your browser uses to identify and gain access to your account in the app
app.config["SECRET_KEY"] = "your-secret-key"

#Bcrypt is a password hashing library
#A scrambled, one-way version of the password
#This just initializes bcrypt and ties it to your Flask app
#example: hashed = bcrypt.generate_password_hash("mypassword123")
#stores something like: $2b$12$Kx8jZ9
bcrypt = Bcrypt(app)


#Tracks who's logged in
#Protects routes, meaning if you are not logged in you cannot access specific routes and will reroute you
login_manager = LoginManager(app)

#this tells it where to redirect them, in this case the "login" route
login_manager.login_view = "login"

engine = create_engine("sqlite:///pokemon_info.db",echo=True)

class Base(DeclarativeBase):
    pass

class Pokemon(Base):
    __tablename__ = "Pokemon_Tracker"
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    name:Mapped[str] = mapped_column(String)
    type1:Mapped[str] = mapped_column(String)
    type2:Mapped[str] = mapped_column(String,nullable=True)
    height:Mapped[float] = mapped_column(Float)
    weight:Mapped[float] = mapped_column(Float)
    ability1:Mapped[str] = mapped_column(String)
    ability2: Mapped[str] = mapped_column(String,nullable=True)
    hidden:Mapped[str] = mapped_column(String,nullable=True)
    hp:Mapped[int] = mapped_column(Integer)
    attack:Mapped[int] = mapped_column(Integer)
    defense:Mapped[int] = mapped_column(Integer)
    special_attack:Mapped[int] = mapped_column(Integer)
    special_defense:Mapped[int] = mapped_column(Integer)
    speed:Mapped[int] = mapped_column(Integer)
    sprite:Mapped[str] = mapped_column(String)
    shiny_sprite:Mapped[str] = mapped_column(String)

# UserMixin adds is_authenticated, is_active, is_anonymous, and get_id() all into one
class User(UserMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

Base.metadata.create_all(engine)

#Flask-Login — manages the cookie, extracts the user_id from it
#load_user function takes that user_id and fetches the full User object from the database
#current_user is available everywhere in your app
@login_manager.user_loader
def load_user(user_id):
    with Session(engine) as session:
        return session.get(User, int(user_id))

@app.route('/register',methods=["GET","POST"])
def register():
    with Session(engine) as session:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = User(username=username, password=hashed_password)
            session.add(new_user)
            session.commit()
            return redirect(url_for('login'))
        return render_template("register.html")

@app.route('/login',methods=["GET","POST"])
def login():
    with Session(engine) as session:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user = session.execute(select(User).where(User.username == username)).scalar_one_or_none()
            #if user exist and checks if passwords match, user.password is the stored hash password and password is hashed
            if user and bcrypt.check_password_hash(user.password, password):
                #uses UserMixin to get the id from the user object automatically and creates the session cookie to log them in
                login_user(user)
                return redirect(url_for('home'))
            return render_template("login.html",error="Invalid username or password.")
        return render_template("login.html")

@app.route('/logout')
#flask_login function that protects the route so only users that are logged in can access
@login_required
def logout():
    # is a Flask-Login function that clears the session cookie
    logout_user()
    return redirect(url_for('login'))
@app.route("/",methods=["GET","POST"])
def home():
    return  render_template("home.html")

@app.route("/search",methods=["GET"])
@login_required
def search():
    with Session(engine) as session:
        query = request.args.get("query")
        if not query:
            return render_template("home.html",error='Search failed, please try again.')
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{query}")
        if response:
            data = response.json()
            id = data["id"]
            name = data["name"]
            type1 = data["types"][0]["type"]["name"]
            type2 = data["types"][1]["type"]["name"] if len(data["types"]) > 1 else None
            height = data["height"]
            weight = data["weight"]
            not_hidden = [ability for ability in data["abilities"] if ability["is_hidden"] is False]
            is_hidden = [ability for ability in data["abilities"] if ability["is_hidden"] is True]
            if len(not_hidden) == 2 :
                ability1 = not_hidden[0]["ability"]["name"]
                ability2 = not_hidden[1]["ability"]["name"]
            else:
                ability1 = not_hidden[0]["ability"]["name"]
                ability2 = None
            if len(is_hidden) == 1:
                hidden = is_hidden[0]["ability"]["name"]
            else:
                hidden = None
            stats = {stat['stat']['name']: stat['base_stat'] for stat in data["stats"]}
            hp = stats["hp"]
            attack = stats['attack']
            defense = stats['defense']
            special_attack = stats['special-attack']
            special_defense = stats['special-defense']
            speed = stats['speed']
            sprite = data["sprites"]["front_default"]
            shiny_sprite = data["sprites"]["front_shiny"]
            exist = session.get(Pokemon,id)
            if exist:
                pokemon_data = session.get(Pokemon,id)
                return render_template("home.html", pokemon_data=pokemon_data, sprite=sprite,shiny_sprite=shiny_sprite)
            else:
                session.add(
                    Pokemon(id=id, name=name, type1=type1, type2=type2, height=height, weight=weight, ability1=ability1,
                            ability2=ability2,hidden=hidden, hp=hp, attack=attack, defense=defense,
                            special_attack=special_attack,special_defense=special_defense, speed=speed,sprite=sprite,shiny_sprite=shiny_sprite))
                session.commit()
                pokemon_data = session.get(Pokemon,id)
                return render_template("home.html",pokemon_data=pokemon_data,sprite=sprite,shiny_sprite=shiny_sprite)
        else:
            return render_template("home.html",error='Search failed, please try again.')


@app.route("/pokedex",methods=["GET"])
@login_required
def pokedex():
    with Session(engine) as session:
        pokedex = session.execute(select(Pokemon)).scalars().all()
        return render_template("pokedex.html",pokedex=pokedex)


@app.route("/evolutions/<id>",methods=["GET"])
@login_required
def evolutions(id):
    with Session(engine) as session:
        get_pokemon = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{id}")
        pokemon_data = get_pokemon.json()
        get_evolutions = requests.get(pokemon_data['evolution_chain']['url'])
        pokemon_evolution_data = get_evolutions.json()
        base_pokemon = pokemon_evolution_data['chain']['species']['name']
        evolution_list = [base_pokemon]
        stats = get_stats(base_pokemon)
        evolution_stats = [stats]
        exist = session.get(Pokemon,stats['id'])
        if not exist:
            session.add(
                Pokemon(id=stats["id"], name=stats["name"], type1=stats["type1"], type2=stats["type2"],
                        height=stats["height"], weight=stats["weight"], ability1=stats["ability1"],
                        ability2=stats["ability2"], hidden=stats["hidden"], hp=stats["hp"], attack=stats["attack"],
                        defense=stats["defense"],
                        special_attack=stats["special-attack"], special_defense=stats["special-defense"],
                        speed=stats["speed"],sprite=stats["sprite"],shiny_sprite=stats["shiny_sprite"]))
            session.commit()
        try:
            first_evolution = pokemon_evolution_data['chain']['evolves_to'][0]['species']['name']
            #for branching evolution
            if len(pokemon_evolution_data['chain']['evolves_to']) > 1:
                for i in pokemon_evolution_data["chain"]["evolves_to"]:
                    brnach_evolution = i['species']['name']
                    stats = get_stats(brnach_evolution)
                    exist = session.get(Pokemon,stats['id'])
                    if exist:
                        evolution_list.append(brnach_evolution)
                        evolution_stats.append(stats)
                    else:
                        session.add(
                            Pokemon(id=stats["id"], name=stats["name"], type1=stats["type1"], type2=stats["type2"],
                                    height=stats["height"], weight=stats["weight"], ability1=stats["ability1"],
                                    ability2=stats["ability2"], hidden=stats["hidden"], hp=stats["hp"],
                                    attack=stats["attack"], defense=stats["defense"],
                                    special_attack=stats["special-attack"], special_defense=stats["special-defense"],
                                    speed=stats["speed"], sprite=stats["sprite"], shiny_sprite=stats["shiny_sprite"]))
                        session.commit()
                        evolution_list.append(brnach_evolution)
                        evolution_stats.append(stats)

            else:
                evolution_list.append(first_evolution)
                stats = get_stats(first_evolution)
                evolution_stats.append(stats)
            exist = session.get(Pokemon,stats['id'])
            if not exist:
                session.add(
                    Pokemon(id=stats["id"], name=stats["name"], type1=stats["type1"], type2=stats["type2"], height=stats["height"], weight=stats["weight"], ability1=stats["ability1"],
                            ability2=stats["ability2"], hidden=stats["hidden"], hp=stats["hp"], attack=stats["attack"], defense=stats["defense"],
                            special_attack=stats["special-attack"], special_defense=stats["special-defense"], speed=stats["speed"],sprite=stats["sprite"],shiny_sprite=stats["shiny_sprite"]))
                session.commit()
        except IndexError:
            return render_template('home.html',evolution_list=evolution_list,evolution_stats=evolution_stats,sprite=stats["sprite"],shiny_sprite=stats["shiny_sprite"],evolve_error="Does not evolve")
        try:
            #for earlier branch evolutions
            if len(pokemon_evolution_data['chain']['evolves_to'])>1:
                for i in pokemon_evolution_data["chain"]["evolves_to"]:
                    branch_evolutions = i
                    if branch_evolutions["evolves_to"]:
                        for second_evolution in branch_evolutions["evolves_to"]:
                            second_evolution = second_evolution['species']['name']
                            stats = get_stats(second_evolution)
                            exist = session.get(Pokemon,stats['id'])
                            if exist:
                                evolution_list.append(second_evolution)
                                evolution_stats.append(stats)
                            else:
                                session.add(
                                    Pokemon(id=stats["id"], name=stats["name"], type1=stats["type1"],
                                            type2=stats["type2"], height=stats["height"], weight=stats["weight"],
                                            ability1=stats["ability1"],
                                            ability2=stats["ability2"], hidden=stats["hidden"], hp=stats["hp"],
                                            attack=stats["attack"], defense=stats["defense"],
                                            special_attack=stats["special-attack"],
                                            special_defense=stats["special-defense"], speed=stats["speed"],
                                            sprite=stats["sprite"], shiny_sprite=stats["shiny_sprite"]))
                                session.commit()
                                evolution_list.append(second_evolution)
                                evolution_stats.append(stats)
                    else:
                        continue
            else:
                second_evolution = pokemon_evolution_data['chain']['evolves_to'][0]['evolves_to'][0]['species']['name']
                stats = get_stats(second_evolution)
                evolution_list.append(second_evolution)
                evolution_stats.append(stats)
                exist = session.get(Pokemon, stats['id'])
                if not exist:
                    session.add(
                        Pokemon(id=stats["id"], name=stats["name"], type1=stats["type1"], type2=stats["type2"],
                                height=stats["height"], weight=stats["weight"], ability1=stats["ability1"],
                                ability2=stats["ability2"], hidden=stats["hidden"], hp=stats["hp"], attack=stats["attack"],
                                defense=stats["defense"],
                                special_attack=stats["special-attack"], special_defense=stats["special-defense"],
                                speed=stats["speed"],sprite=stats["sprite"],shiny_sprite=stats["shiny_sprite"]))
                    session.commit()
        except IndexError:
            return render_template('home.html', evolution_list=evolution_list,evolution_stats=evolution_stats,sprite=stats["sprite"],shiny_sprite=stats["shiny_sprite"])

        return render_template('home.html', evolution_list=evolution_list, evolution_stats=evolution_stats,sprite=stats["sprite"],shiny_sprite=stats["shiny_sprite"])

def get_stats(pokemon_name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}")
    data = response.json()
    stats = {stat['stat']['name']: stat['base_stat'] for stat in data["stats"]}
    not_hidden = [ability for ability in data["abilities"] if ability["is_hidden"] is False]
    is_hidden = [ability for ability in data["abilities"] if ability["is_hidden"] is True]
    if len(not_hidden) == 2:
        ability1 = not_hidden[0]["ability"]["name"]
        ability2 = not_hidden[1]["ability"]["name"]
    else:
        ability1 = not_hidden[0]["ability"]["name"]
        ability2 = None
    if len(is_hidden) == 1:
        hidden = is_hidden[0]["ability"]["name"]
    else:
        hidden = None
    return{
    "id" : data["id"],
    "name" : data["name"],
    "type1" : data["types"][0]["type"]["name"],
    "type2" : data["types"][1]["type"]["name"] if len(data["types"]) > 1 else None,
    "height" : data["height"],
    "weight" : data["weight"],
    "ability1" : ability1,
    "ability2" : ability2,
    "hidden" : hidden,
    "hp" : stats["hp"],
    "attack": stats["attack"],
    "defense": stats["defense"],
    "special-attack":stats["special-attack"],
    "special-defense":stats["special-defense"],
    "speed": stats["speed"],
    "sprite":data["sprites"]["front_default"],
    "shiny_sprite":data["sprites"]["front_shiny"]}


if __name__ == "__main__":
    app.run(debug=True)
