# PokeAPI Flask App

A full-stack web application built with Flask that allows users to search for Pokémon, view stats, browse a personal Pokédex, and explore evolution chains — all backed by a SQLite database.

## Features
- User registration and login with hashed passwords (Flask-Login + Bcrypt)
- Search any Pokémon by name via the [PokéAPI](https://pokeapi.co/)
- Displays type, height, weight, abilities, base stats, and sprites (including shiny)
- Saves searched Pokémon to a local SQLite database automatically
- Personal Pokédex page showing all previously searched Pokémon
- Evolution chain viewer with full stats for each stage

## Technologies Used
- Python / Flask
- SQLAlchemy ORM (SQLite)
- Flask-Login, Flask-Bcrypt
- [PokéAPI](https://pokeapi.co/) (free, open REST API)
- Jinja2 templating
- HTML/CSS

## How to Run
1. Clone the repository
2. Install dependencies:

pip install flask flask-bcrypt flask-login sqlalchemy requests
3. Run the app:
python Poke_API.py
4. Visit `http://127.0.0.1:5000` in your browser
5. Register an account and start searching

## What I Learned
- Building full-stack web apps with Flask and Jinja2 templating
- User authentication with hashed passwords and session management
- Persisting API data to a relational database using SQLAlchemy ORM
- Chaining multiple API calls to retrieve and display evolution chains
- Structuring a Flask app with routes, models, and templates