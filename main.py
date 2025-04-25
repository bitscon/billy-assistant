from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

@app.route("/about", methods=["GET"])
def about():
    info = {
        "name": "Billy",
        "version": "v1.0",
        "description": "Private AI assistant for Chad",
        "status": "ready",
        "github": "https://github.com/bitscon/billy-assistant"
    }
    log_event({"type": "meta", "event": "about_check", "timestamp": time.time()})
    return jsonify(info)
