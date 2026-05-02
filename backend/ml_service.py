from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

TRAINING_DATA = [
    ("production issue blocking users payments failing urgent", "High"),
    ("critical bug causing downtime and outage", "High"),
    ("security vulnerability exposure requires immediate patch", "High"),
    ("high impact model drift affecting all predictions", "High"),
    ("complete dashboard UI polish and alignment", "Medium"),
    ("refactor task board performance and caching", "Medium"),
    ("implement project filtering and search", "Medium"),
    ("write integration tests for auth routes", "Medium"),
    ("update README grammar and formatting", "Low"),
    ("rename variables for consistency", "Low"),
    ("adjust button spacing and typography", "Low"),
    ("add optional tooltip for icons", "Low"),
]

X_TRAIN = [text for text, _ in TRAINING_DATA]
y_TRAIN = [label for _, label in TRAINING_DATA]

priority_model = Pipeline(
    [
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
        ("clf", LogisticRegression(max_iter=200, random_state=42)),
    ]
)

priority_model.fit(X_TRAIN, y_TRAIN)


KEYWORD_BOOST = {
    "High": {"urgent", "critical", "outage", "security", "breach", "blocking", "fail"},
    "Medium": {"refactor", "optimize", "feature", "improve", "implement", "test"},
    "Low": {"docs", "style", "rename", "minor", "clean", "format"},
}


def predict_priority(description: str) -> str:
    description_lower = description.lower()
    scores = {"High": 0, "Medium": 0, "Low": 0}

    for label, words in KEYWORD_BOOST.items():
        for word in words:
            if word in description_lower:
                scores[label] += 1

    if max(scores.values()) > 0:
        return max(scores, key=scores.get)

    return str(priority_model.predict([description])[0])
