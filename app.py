import time
from flask import Flask, render_template
from config import Config
from extensions import login_manager, session
from blockchain.__init__ import get_blockchain

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    session.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    app.blockchain = get_blockchain()

    # ─── Register custom template filter ───
    @app.template_filter('ctime')
    def ctime_filter(timestamp):
        if isinstance(timestamp, (int, float)):
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        return str(timestamp)

    # Import blueprints
    from auth.routes import auth_bp
    from incident.routes import incident_bp
    from evidence.routes import evidence_bp
    from victim.routes import victim_bp
    from investigator.routes import investigator_bp
    from admin.routes import admin_bp
    from violation.routes import violation_bp
    from governance.routes import governance_bp   # <-- add this

    # Register without prefixes for most
    app.register_blueprint(auth_bp)
    app.register_blueprint(incident_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(victim_bp)
    app.register_blueprint(investigator_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(violation_bp)

    # Governance with prefix (or without, as you prefer)
    app.register_blueprint(governance_bp, url_prefix='/governance')

    @app.route('/')
    def index():
        return render_template('index.html', blocks=len(app.blockchain.chain), valid=app.blockchain.is_chain_valid())

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)