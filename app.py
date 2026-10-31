
from flask import Flask, render_template, request, jsonify
import joblib
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Load trained ML models
sentiment_model = joblib.load(
    os.path.join(MODEL_DIR, "sentiment_model.pkl")
)

fake_review_model = joblib.load(
    os.path.join(MODEL_DIR, "fake_review_model.pkl")
)


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

        elif len(review) > 5000:
            error = "Review must not exceed 5000 characters."

        else:
            try:
                sentiment_probabilities = (
                    sentiment_model.predict_proba([review])[0]
                )

                fake_probabilities = (
                    fake_review_model.predict_proba([review])[0]
                )

                sentiment = sentiment_model.predict([review])[0]

                authenticity = fake_review_model.predict([review])[0]

                sentiment_confidence = round(
                    max(sentiment_probabilities) * 100, 2
                )

                fake_confidence = round(
                    max(fake_probabilities) * 100, 2
                )

            except Exception:
                app.logger.exception("Review prediction failed")
                error = "Unable to analyze this review. Please try again."

    return render_template(
        "index.html",
        sentiment=sentiment,
        authenticity=authenticity,
        sentiment_confidence=sentiment_confidence,
        fake_confidence=fake_confidence,
        review=review,
        error=error
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "Product Review Analyzer"
    }), 200


if __name__ == "__main__":
    app.run(debug=False)
