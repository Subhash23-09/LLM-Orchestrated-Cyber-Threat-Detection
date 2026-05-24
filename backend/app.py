import os
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
import json
import asyncio

# Load environment variables
load_dotenv()

def create_app():
    print("Initializing Flask App...")
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    print("Configuring Database URI...")
    # Adapt DATABASE_URL for sync Flask/SQLAlchemy
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise RuntimeError("DATABASE_URL not found in environment. MySQL is required.")
        
    if db_url.startswith('mysql+aiomysql://'):
        db_url = db_url.replace('mysql+aiomysql://', 'mysql+pymysql://')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print("Importing models...")
    from models import db
    print("Models imported. Initializing db with app...")
    db.init_app(app)
    
    print("Creating Database Tables (if not exist)...")
    with app.app_context():
        db.create_all()
    print("Database ready.")

    # Basic Health Check
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"message": "ACD-SDI API is running", "docs": "/api/v1"}), 200

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "service": "ACD-SDI Backend"}), 200

    @app.route('/api/v1/orchestration/chat_stream', methods=['POST'])
    def chat_stream():
        """
        Server-Sent Events endpoint for multi-agent orchestration.
        """
        from services.orchestrator import OrchestratorService
        from services.memory_store import MemoryService
        
        data = request.get_json() or {}
        # Fetch signals from memory or as provided
        context = MemoryService.get_context()
        signals = context['short_term']['active_context']

        async def event_generator():
            async for evt in OrchestratorService.stream_agent_updates(signals, context):
                yield f"data: {json.dumps(evt)}\n\n"

        def run_async_gen():
            # Correctly manage loop for sync Flask route
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            gen = event_generator()
            try:
                while True:
                    try:
                        chunk = loop.run_until_complete(gen.__anext__())
                        yield chunk
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()

        return Response(stream_with_context(run_async_gen()), mimetype='text/event-stream')

    print("Registering Blueprints...")
    from api.ingestion import ingestion_bp
    from api.processing import processing_bp
    from api.memory import memory_bp
    from api.orchestration import orchestrator_bp
    from api.agents import agents_bp
    from api.decision import decision_bp
    from api.reporting import reporting_bp
    from api.learning import learning_bp
    from api.mitigation import mitigation_bp
    from api.narrative import narrative_bp
    from api.auth import auth_bp
    
    app.register_blueprint(ingestion_bp, url_prefix='/api/v1/ingestion')
    app.register_blueprint(processing_bp, url_prefix='/api/v1/processing')
    app.register_blueprint(memory_bp, url_prefix='/api/v1/memory')
    app.register_blueprint(orchestrator_bp, url_prefix='/api/v1/orchestration')
    app.register_blueprint(agents_bp, url_prefix='/api/v1/agents')
    app.register_blueprint(decision_bp, url_prefix='/api/v1/decision')
    app.register_blueprint(reporting_bp, url_prefix='/api/v1/reporting')
    app.register_blueprint(learning_bp, url_prefix='/api/v1/learning')
    app.register_blueprint(mitigation_bp, url_prefix='/api/v1/mitigation')
    app.register_blueprint(narrative_bp, url_prefix='/api/v1/narrative')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')


    print("App Creation Complete.")
    return app

if __name__ == '__main__':
    # Trigger reload
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
