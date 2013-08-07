from flask import g, session, request, url_for, flash, redirect
from snipey import app, meetup_oauth, model, controller


@app.before_request
def before_request():
    """
    If a user_id is specified in the session, fetch the user from the db
    """
    g.user = None
    if 'user_id' in session:
        g.user = model.User.query.get(session['user_id']).first()


@meetup_oauth.tokengetter
def get_meetup_token():
    """
    This is used by the API to look for the auth token and secret it
    should use for API calls.  During the authorization handshake a
    temporary set of token and secret is used, but afterwards this
    function has to return the token and secret.  If you don't want to
    store this in the database, consider putting it into the session
    instead.
    """
    oauth_secret = request.args.get('secret', '')
    oauth_token = request.args.get('token', '')

    if oauth_secret and oauth_token:
        return oauth_token, oauth_secret

    if g.user:
        return g.user.token, g.user.secret


@app.route('/login')
def login():
    """Calling into authorize will cause the OpenID auth machinery to kick
    in.  When all worked out as expected, the remote application will
    redirect back to the callback URL provided.
    """
    return meetup_oauth.authorize(
        callback=url_for('oauth_authorized',
                         next=request.args.get('next')
                         or request.referrer
                         or None))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were signed out', 'alert-success')
    return redirect(request.referrer or url_for('index'))


@app.route('/')
def hello_world():
    return 'hello world'


@app.route('/oauth-authorized')
@meetup_oauth.authorized_handler
def oauth_authorized(resp):
    if resp is None or resp['member_id'] is None:
        flash(u'You denied the request to sign in.', 'alert-error')
        return redirect(url_for('index'))

    meetup_id = resp['member_id']
    oauth_token = resp['oauth_token']
    oauth_secret = resp['oauth_token_secret']

    user = controller.fetch_user(meetup_id, (oauth_token, oauth_secret))

    session['user_id'] = user.id
    flash('You were signed in', 'alert-info')

    return redirect(url_for('snipe'))
