from flask import Flask

from cat_or_roll.classifier.abc import ClassifierError
from cat_or_roll.classifier.impl.classifier import CatVsBunClassifier
from cat_or_roll.service.configuration import Configuration
from cat_or_roll.service.routers.classify import bp as classify_bp


def create_app(configuration: Configuration = None):
    app = Flask(__name__)
    
    if configuration is None:
        configuration = Configuration()
    
    try:
        classifier = CatVsBunClassifier(model_location=str(configuration.classifier.location))
        app.config["classifier"] = classifier
        app.logger.info("Classifier created successfully.")
    except ClassifierError as error:
        app.logger.error(f"Failed to create classifier: {error}")
        raise error
    
    app.register_blueprint(classify_bp)
    
    app.config["HOST"] = configuration.connection.host
    app.config["PORT"] = configuration.connection.port
    app.config["DEBUG"] = configuration.connection.debug
    app.config["ALLOWED_EXTENSIONS"] = set(configuration.allowed_extensions)
    
    return app


if __name__ == "__main__":
    configuration = Configuration()
    app = create_app(configuration)
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"]
    )
