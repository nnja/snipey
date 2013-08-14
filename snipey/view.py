from flask import (g, session, request, url_for, flash, redirect,
                   render_template)
from snipey import app, meetup_oauth, model, controller


@app.before_request
def before_request():
    """
    If a user_id is specified in the session, fetch the user from the db
    """
    g.user = None
    if 'user_id' in session:
        g.user = model.User.query.filter_by(id=session['user_id']).first()


@meetup_oauth.tokengetter
def get_meetup_token(token=None):
    """
    This is used by the API to look for the auth token and secret it
    should use for API calls.  During the authorization handshake a
    temporary set of token and secret is used, but afterwards this
    function has to return the token and secret.  If you don't want to
    store this in the database, consider putting it into the session
    instead.
    """
    # oauth_secret = request.args.get('secret', '')
    # oauth_token = request.args.get('token', '')

    # if oauth_secret and oauth_token:
    #     return oauth_token, oauth_secret

    print 'token is %s' % token
    if token is not None:
        print '\n\ni had token@!\n\n'
        user = model.User.query.filter_by(token=token).first()
        return token, user.secret

    if 'user_id' in session:
        print '\n\nuser_id in session %s \n\n' % session['user_id']
        user = model.User.query.filter_by(id=session['user_id']).first()
        return user.token, user.secret

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


@app.route('/oauth-authorized')
@meetup_oauth.authorized_handler
def oauth_authorized(resp):
    if resp is None or resp['member_id'] is None:
        flash(u'You denied the request to sign in.', 'alert-error')
        return redirect(url_for('index'))

    meetup_id = resp['member_id']
    name = resp['name']
    oauth_token = resp['oauth_token']
    oauth_secret = resp['oauth_token_secret']

    user = controller.fetch_user(meetup_id, (oauth_token, oauth_secret), name)

    session['user_id'] = user.id
    flash('You were signed in', 'alert-info')

    return redirect(url_for('snipe'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    mup_user = None
    if g.user is not None:
        resp = meetup_oauth.post('member/self', data={
            'page': '20'
        })
        if resp.status == 200:
            mup_user = resp.data
        else:
            flash('Something went wrong', 'alert-error')
    return render_template('index.html', mup_user=mup_user)


@app.route('/snipe')
def snipe():
 #   import tasks
#    tasks.rsvp.delay(48598382, 133591952, g.user.token) 
    return 'hello'
