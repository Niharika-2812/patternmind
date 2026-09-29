from flask import Flask, render_template, request, jsonify
from collections import Counter
from datetime import datetime
import re

app = Flask(__name__)

experiences = [
    {
        "id": 1,
        "title": "Payment API Incident",
        "description": "After a deployment, database connections increased and the payment API became slow.",
        "tags": ["deployment", "database", "api", "latency"],
        "date": "2026-09-02"
    },
    {
        "id": 2,
        "title": "Checkout Failure",
        "description": "A production deployment caused connection pool pressure and payment failures.",
        "tags": ["deployment", "database", "payments"],
        "date": "2026-09-08"
    },
    {
        "id": 3,
        "title": "API Degradation",
        "description": "Following a release, database latency increased and API errors went up.",
        "tags": ["deployment", "database", "api", "latency"],
        "date": "2026-09-15"
    },
    {
        "id": 4,
        "title": "Maintenance Window",
        "description": "Routine maintenance completed without major API degradation.",
        "tags": ["maintenance", "database"],
        "date": "2026-09-20"
    }
]


def extract_keywords(text):
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

    stop_words = {
        "this", "that", "with", "from", "after", "before",
        "into", "were", "there", "their", "about", "following",
        "became", "caused", "major", "without"
    }

    return [
        word for word in words
        if word not in stop_words
    ]


def discover_patterns(items):
    tag_counter = Counter()

    for item in items:
        for tag in item.get("tags", []):
            tag_counter[tag] += 1

    patterns = []

    for tag, count in tag_counter.most_common():
        if count >= 2:
            supporting = [
                item["title"]
                for item in items
                if tag in item.get("tags", [])
            ]

            patterns.append({
                "pattern": f"{tag.title()} appears repeatedly across historical experiences",
                "frequency": count,
                "evidence": supporting
            })

    # Special relationship discovered from our demo data
    deployment_items = [
        item for item in items
        if "deployment" in item.get("tags", [])
    ]

    database_items = [
        item for item in deployment_items
        if "database" in item.get("tags", [])
    ]

    if len(deployment_items) >= 2 and len(database_items) >= 2:
        patterns.insert(0, {
            "pattern": "Deployment-related incidents repeatedly coincide with database problems",
            "frequency": len(database_items),
            "evidence": [item["title"] for item in database_items],
            "strength": "High"
        })

    return patterns


@app.route("/")
def home():
    return render_template(
        "index.html",
        experiences=experiences,
        patterns=discover_patterns(experiences)
    )


@app.route("/add", methods=["POST"])
def add_experience():
    data = request.get_json()

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    tags = data.get("tags", [])

    if not title or not description:
        return jsonify({
            "success": False,
            "message": "Title and description are required."
        }), 400

    new_experience = {
        "id": len(experiences) + 1,
        "title": title,
        "description": description,
        "tags": tags,
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    experiences.append(new_experience)

    return jsonify({
        "success": True,
        "experience": new_experience,
        "patterns": discover_patterns(experiences)
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "success": False,
            "message": "Enter an experience to analyze."
        })

    query_words = set(extract_keywords(query))

    matches = []

    for item in experiences:
        item_words = set(
            extract_keywords(
                item["title"] + " " +
                item["description"] + " " +
                " ".join(item["tags"])
            )
        )

        overlap = query_words.intersection(item_words)

        if overlap:
            matches.append({
                "experience": item,
                "matched_terms": list(overlap)
            })

    patterns = discover_patterns(
        [match["experience"] for match in matches]
        if matches else experiences
    )

    insight = (
        "PatternMind found historical experiences with overlapping signals. "
        "The repeated relationship should be investigated using the supporting evidence."
    )

    if any("Deployment-related" in p["pattern"] for p in patterns):
        insight = (
            "PatternMind detected a recurring relationship between deployments "
            "and database-related problems in historical incidents. "
            "Consider monitoring database connections and latency during future deployments."
        )

    return jsonify({
        "success": True,
        "matches": matches,
        "patterns": patterns,
        "insight": insight
    })


if __name__ == "__main__":
    app.run(debug=True)