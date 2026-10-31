
import logging
import os
from logging.handlers import RotatingFileHandler

import joblib
from flask import Flask, render_template, request, jsonify


# --------------------------------------------------
# Application configuration
# --------------------------------------------------

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)


# --------------------------------------------------
# Configure application logging
# --------------------------------------------------

file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    maxBytes=1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)

file_handler.setLevel(logging.INFO)

file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)


# --------------------------------------------------
# Load trained machine learning models
# --------------------------------------------------

sentiment_model = joblib.load(
    os.path.join(MODEL_DIR, "sentiment_model.pkl")
)

fake_review_model = joblib.load(
    os.path.join(MODEL_DIR, "fake_review_model.pkl")
)

app.logger.info("Machine learning models loaded successfully")


# --------------------------------------------------
# Main application route
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    sentiment = None
    authenticity = None
    sentiment_confidence = None
    fake_confidence = None
    review = ""
    error = None

    if request.method == "POST":

        review = request.form.get("review", "").strip()

        if not review:
            error = "Please enter a product review."
            app.logger.warning("Empty review submitted")

        elif len(review) > 5000:
            error = "Review must not exceed 5000 characters."
            app.logger.warning("Review exceeded maximum character limit")

        else:
            try:
                # Sentiment prediction
                sentiment_probabilities = (
                    sentiment_model.predict_proba([review])[0]
                )

                sentiment = sentiment_model.predict([review])[0]

                sentiment_confidence = round(
                    max(sentiment_probabilities) * 100, 2
                )

                # Fake review prediction
                fake_probabilities = (
                    fake_review_model.predict_proba([review])[0]
                )

                authenticity = fake_review_model.predict([review])[0]

                fake_confidence = round(
                    max(fake_probabilities) * 100, 2
                )

                app.logger.info(
                    "Prediction request processed successfully"
                )

            except Exception:
                app.logger.exception("Review prediction failed")
                error = (
                    "Unable to analyze this review. Please try again."
                )

    return render_template(
        "index.html",
        sentiment=sentiment,
        authenticity=authenticity,
        sentiment_confidence=sentiment_confidence,
        fake_confidence=fake_confidence,
        review=review,
        error=error
    )


# --------------------------------------------------
# Health monitoring endpoint
# --------------------------------------------------

@app.route("/health", methods=["GET"])
def health():

    app.logger.info("Health check requested")

    return jsonify({
        "status": "healthy",
        "application": "Product Review Analyzer"
    }), 200


# --------------------------------------------------
# Application entry point
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
