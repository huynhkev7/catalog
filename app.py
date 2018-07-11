import datetime
import httplib2
import json
import random
import requests
import string
from functools import wraps
from setup_database import Base, User, Category, Item
from flask import session as login_session, make_response,\
    Flask, render_template, request, redirect, jsonify, url_for,\
    make_response, flash, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets

APP_NAME = 'App Catalog'
ITEM_COUNT = 10
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
app = Flask(__name__)
app.secret_key = 'super_secret_key'

# connect to the database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    """check if user is logged in

    Returns:
        decarator function or redirect to login
        if user not in session
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            flash('User not allowed to access')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def user_in_session():
    """Check user is in session

    Returns:
        boolean if user already in session
    """
    return 'user_id' in login_session


def get_user_id(email):
    """Get a user by email

    Args:
        email: user email

    Returns:
        user id
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as e:
        print 'No user found for ' + email + ': ' + str(e)
        return None


def same_user(user_id):
    """Validate user is the same in sesion

    Args:
        user_id: user id

    Returns:
        boolean if user is the same
    """
    return user_id == login_session['user_id']


def get_category_in_list(category_id, category_list):
    """
    Retrieves a category from list that matches given id

    Args:
        category_id: category id to find
        category_list: list of categories

    Returns:
        category object
    """
    for category in category_list:
        if category_id == category.id:
            return category


def new_user(user_session):
    """Generate new user based on session

    Args:
        user_session: session containing user data

    Returns:
        id of user
    """
    user = User(
                name=user_session['username'],
                email=user_session['email'])
    session.add(user)
    session.flush()
    session.commit()
    return user.id


@app.route('/login')
def login():
    """Show login page

    Returns:
        login.html
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('views/login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def login_with_google():
    """Handle user login using Google

    Returns:
        success message
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print "data from oauth: " + str(data)
    login_session['email'] = data['email']
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    user_id = get_user_id(login_session['email'])
    # create new user if not found in database
    if not user_id:
        user_id = new_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src=\"'
    output += login_session['picture']
    output += ' \" ' \
              'style = \"width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;\"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def logout_with_google():
    """Handle user logout using google

    Revoke current user token and clear the session.

    Returns:
        redirect back to login page. Return error message on failure.
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['user_id']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('login'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog/')
def home():
    """Display home page

    Fetch all categories and latest items.

    Returns:
        catalog.html
    """
    categories = session.query(Category).all()
    latest_items = session.query(Item).order_by(
        Item.created_date.desc()).limit(ITEM_COUNT).all()
    return render_template(
        'views/catalog.html',
        categories=categories,
        latest_items=latest_items,
        user_in_session=user_in_session())


@app.route('/catalog/<int:category_id>/items')
def items_for_category(category_id):
    """Display items under a category

    Args:
        category_id: category id

    Returns:
        items.html
    """
    items_under_category = session.query(
        Item).filter_by(category_id=category_id).all()
    all_categories = session.query(Category).all()
    category = get_category_in_list(category_id, all_categories)
    return render_template(
        'views/items.html',
        items=items_under_category,
        current_category=category,
        categories=all_categories)


@app.route('/catalog/<int:category_id>/<int:item_id>')
def item_details(category_id, item_id):
    """Show item details

    Args:
        category_id: category id
        item_id: item id

    Returns:
        detail.html
    """
    item = session.query(
        Item).filter_by(id=item_id).one()
    category = session.query(
        Category).filter_by(id=category_id).one()
    return render_template(
        'views/detail.html',
        item=item,
        category=category,
        show_button=(
            user_in_session() and same_user(item.user_id)))


@app.route('/catalog/add', methods=['POST', 'GET'])
@login_required
def new_item():
    """Create a new item

    Returns:
        GET - serve add.html
        POST - add item and redirect to detail.html
    """
    if request.method == 'POST':
        new_item = Item(
            category_id=int(request.form['category']),
            name=request.form['name'],
            description=request.form['description'],
            created_date=datetime.datetime.now(),
            user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        return redirect(
            url_for(
                'item_details',
                category_id=new_item.category_id,
                item_id=new_item.id))
    else:
        categories = session.query(
            Category).all()
        return render_template(
            'views/add.html',
            categories=categories)


@app.route('/catalog/<int:item_id>/delete', methods=['POST', 'GET'])
@login_required
def remove_item(item_id):
    """Remove an item from the database

    Args:
        item_id: item id

    Returns:
        GET - redirect to delete.html
        POST - remove item and redirect to items.html
    """
    remove_item = session.query(Item).filter_by(id=item_id).one()
    category_id = remove_item.category_id

    # redirect to details page if current user does not own item
    if remove_item.user_id != login_session['user_id']:
        return redirect(
            url_for(
                'item_details',
                category_id=category_id,
                item_id=remove_item.id))

    if request.method == 'POST':
        session.delete(remove_item)
        session.commit()
        return redirect(
            url_for(
                'items_for_category', category_id=category_id))
    else:
        return render_template(
            'views/delete.html',
            item_to_delete=remove_item,
            category_id=category_id)


@app.route('/catalog/<int:item_id>/edit', methods=['POST', 'GET'])
@login_required
def update_item(item_id):
    """Update an item from the database

    Args:
        item_id: item id

    Returns:
        GET - serve edit.html
        POST: update an item and redirect to detail.html
    """
    edited_item = session.query(Item).filter_by(id=item_id).one()

    # redirect to details page if current user does not own item
    if edited_item.user_id != login_session['user_id']:
        return redirect(
            url_for(
                'item_details',
                category_id=edited_item.category_id,
                item_id=edited_item.id))

    if request.method == 'POST':
        if request.form['category']:
            edited_item.category_id = request.form['category']
        if request.form['name']:
            edited_item.name = request.form['name']
        if request.form['description']:
            edited_item.description = request.form['description']
        edited_item.updated_date = datetime.datetime.now()
        session.add(edited_item)
        session.commit()
        return redirect(
            url_for(
                'item_details',
                category_id=edited_item.category_id,
                item_id=edited_item.id))
    else:
        categories = session.query(Category).all()
        return render_template(
            'views/edit.html',
            edited_item=edited_item,
            categories=categories)


@app.route('/json/catalog')
def catalog_json():
    """Get JSON for all categories and items in database

        Returns:
            All Categories and items formatted as a JSON
    """
    catalog_json = []
    try:
        all_categories = session.query(Category).all()
        for category in all_categories:
            items_for_category = session.query(
                Item).filter_by(
                    category_id=category.id).all()
            items = []
            for current_item in items_for_category:
                items.append(current_item.serialize)
            catalog_json.append({
                'category_name': category.name,
                'category_id': category.id,
                'items': items
            })
    except Exception as e:
        error = {
            'result': 'No catalog data: ' + str(e)
        }
        catalog_json.append(error)
    return jsonify(catalog_json)


@app.route('/json/item/<int:item_id>')
def item_json(item_id):
    """Get JSON for an item in the database

    Args:
        item_id: item id

    Returns:
        Item from the database as a JSON
    """
    item_details_json = {}
    try:
        item_in_db = session.query(Item).filter_by(id=item_id).one()
        item_details_json['item'] = item_in_db.serialize
    except Exception as e:
        item_details_json['result'] = 'No data for item ID ' \
            + str(item_id) + ': ' + str(e)
    return jsonify(item_details_json)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
