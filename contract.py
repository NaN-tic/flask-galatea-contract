from flask import Blueprint, render_template, current_app, abort, g, \
    url_for, request, session
from galatea.tryton import tryton
from galatea.helpers import customer_required
from flask_babel import gettext as _, lazy_gettext
from flask_paginate import Pagination
from flask_login import login_required

contract = Blueprint('contract', __name__, template_folder='templates')

DISPLAY_MSG = lazy_gettext('Displaying <b>{start} - {end}</b> of <b>{total}</b>')

LIMIT = current_app.config.get('TRYTON_PAGINATION_CONTRACT_LIMIT', 20)
STATE_EXCLUDE = current_app.config.get('TRYTON_CONTRACT_STATE_EXCLUDE', ['draft'])

Contract = tryton.pool.get('contract')

@contract.route("/<int:id>", endpoint="contract")
@login_required
@customer_required
@tryton.transaction()
def contract_detail(lang, id):
    '''Contract Detail'''

    contracts = Contract.search([
        ('id', '=', id),
        ('party', '=', session['customer']),
        ('state', 'not in', STATE_EXCLUDE),
        ], limit=1)
    if not contracts:
        abort(404)

    contract, = Contract.browse(contracts)

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('my-account', lang=g.language),
        'name': _('My Account'),
        }, {
        'slug': url_for('.contracts', lang=g.language),
        'name': _('Contracts'),
        }, {
        'slug': url_for('.contract', lang=g.language, id=contract.id),
        'name': contract.number or _('Not number'),
        }]

    return render_template('contract.html',
            breadcrumbs=breadcrumbs,
            contract=contract,
            )

@contract.route("/", endpoint="contracts")
@login_required
@customer_required
@tryton.transaction()
def contract_list(lang):
    '''Contracts'''

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    domain = [
        ('party', '=', session['customer']),
        ('state', 'not in', STATE_EXCLUDE),
        ]
    total = Contract.search_count(domain)
    offset = (page-1)*LIMIT

    order = [
        ('start_period_date', 'DESC'),
        ('id', 'DESC'),
        ]
    contracts = Contract.search(domain, offset, LIMIT, order)

    pagination = Pagination(
        page=page, total=total, per_page=LIMIT, display_msg=DISPLAY_MSG, bs_version='3')

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('my-account', lang=g.language),
        'name': _('My Account'),
        }, {
        'slug': url_for('.contracts', lang=g.language),
        'name': _('Contracts'),
        }]

    return render_template('contracts.html',
            breadcrumbs=breadcrumbs,
            pagination=pagination,
            contracts=contracts,
            )
