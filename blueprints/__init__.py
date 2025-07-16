from flask import Blueprint

def init_app(app, mongo_instance):
    """Initialize blueprints with the Flask app"""
    from .news_routes import news_bp, init_mongo
    init_mongo(mongo_instance)
    app.register_blueprint(news_bp)
