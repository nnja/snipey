from flask import (g, session, request, url_for, flash, redirect,
                   render_template)
from snipey import app, meetup_oauth, model, controller
from snipey.meetup import fetch_user_groups
from flask_wtf import widgets, Form, SelectMultipleField


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
    if 'user_id' in session:
        g.user = model.User.query.filter_by(id=session['user_id']).first()

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
    #name = resp['name']
    oauth_token = resp['oauth_token']
    oauth_secret = resp['oauth_token_secret']

    user = controller.fetch_user(meetup_id, (oauth_token, oauth_secret))

    session['user_id'] = user.id
    flash('You were signed in', 'alert-info')

    return redirect(url_for('subscribe'))


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

@app.route('/about')
def about():
    return 'about'


class SubscriptionForm(Form):
    groups = SelectMultipleField(
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if g.user is None:
        return url_for('index')

    # TODO Redo below with proper form validation. Good enough for now.
    form = SubscriptionForm()
    form.groups.choices = controller.get_group_list(g.user)

    if request.method == 'POST':
        selected_groups = form.data['groups']
        if not selected_groups:
            flash('Please select at least one group.', 'alert-error')
        else:
            controller.subcribe_to_groups(g.user, selected_groups)
            flash('You are subscribed to %s groups'
                  % len(selected_groups), 'alert-success')
            return render_template("snipe.html")

    return render_template('subscribe.html', form=form)


@app.route('/snipes')
def snipes():
    snipes = g.user.snipes
    subscriptions = g.user.subscriptions
    return render_template('snipe.html', snipes=snipes, subscriptions=subscriptions)
