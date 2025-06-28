from flask import Blueprint
newsOfTheWorld = Blueprint('newsOfTheWorld', __name__, template_folder='templates', static_folder='static')
from . import api_client
from .api_client import (
    fetch_random_country_news, 
    fetch_and_save_continent_news, 
    get_countries_by_continent,
    fetch_multiple_continent_news,
    fetch_and_save_multiple_continent_news,
    fetch_all_continents_news
)

__all__ = [
    'fetch_random_country_news', 
    'fetch_and_save_continent_news', 
    'get_countries_by_continent',
    'fetch_multiple_continent_news',
    'fetch_and_save_multiple_continent_news',
    'fetch_all_continents_news'
]