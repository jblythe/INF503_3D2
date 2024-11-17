from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "35.194.44.166"),
    "port": os.getenv("DB_PORT", "5432")
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/run_query", methods=["POST"])
def run_query():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        if cursor.description:
            # Fetch rows for SELECT queries
            columns = [desc[0] for desc in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            # Handle non-SELECT queries (INSERT/UPDATE/DELETE)
            connection.commit()
            rows = [{"message": f"Query executed successfully, {cursor.rowcount} row(s) affected"}]

        cursor.close()
        connection.close()
        return jsonify({"results": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)