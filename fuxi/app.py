from flask import Flask, render_template
from string import digits, ascii_lowercase
from random import sample
from fuxi.views.authenticate import login_check, authenticate
from fuxi.views.index import index
from fuxi.views.vul_scanner import vul_scanner
from fuxi.views.asset_management import asset_management
from fuxi.views.plugin_management import plugin_management
from fuxi.views.settings import settings
from fuxi.views.dashboard import dashboard
from fuxi.views.port_scanner import port_scanner
from fuxi.views.subdomain_brute import subdomain_brute
from fuxi.views.acunetix_scanner import acunetix_scanner
from fuxi.views.auth_tester import auth_tester


app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join(sample(digits + ascii_lowercase, 10))

app.register_blueprint(authenticate)
app.register_blueprint(index)
app.register_blueprint(vul_scanner)
app.register_blueprint(asset_management)
app.register_blueprint(plugin_management)
app.register_blueprint(settings)
app.register_blueprint(dashboard)
app.register_blueprint(port_scanner)
app.register_blueprint(subdomain_brute)
app.register_blueprint(acunetix_scanner)
app.register_blueprint(auth_tester)


@app.errorhandler(404)
@login_check
def page_not_fount(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
@login_check
def internal_server_error(e):
    return render_template('500.html'), 500
