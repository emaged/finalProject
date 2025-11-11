from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('alchemy', __name__)


@bp.route('/alchemy')
def index():
    return render_template('index.html')