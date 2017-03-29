from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, session
from flask.ext.login import login_required, current_user
from . import main
from .forms import *
from .. import db
from ..models import *
from ..decorators import admin_required, permission_required
from random import randint


@main.route('/', methods=['GET', 'POST'])
def index():
    premium_ads = User.query.filter_by(premium=True).all()
    while len(premium_ads) > 4:
        del premium_ads[randint(0,len(premium_ads)-1)]
    return render_template('index.html',premium_ads=premium_ads)


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.role.name == "Disabled" and current_user.id != user.id:
        flash("This user has disabled their account their account.")
        return redirect(url_for('.index'))
    if user.role.name == "Banned":
        flash("This user has been banned.")
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES):
        if current_user.username == username and form.validate_on_submit():
            post = Post(body=form.body.data,author=current_user._get_current_object())
            db.session.add(post)
            return redirect(url_for('.user',username=username))
    groups = user.group_membership.filter(Group.approved==True).all()
    media = user.media_offered.order_by(Media.username).all()
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination,form=form,groups=groups,media=media)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.furaffinity = form.furaffinity.data
        current_user.weasyl = form.weasyl.data
        current_user.website = form.website.data
        current_user.short_ad = form.short_ad.data
        flash('Your profile has been updated.')
        db.session.add(current_user)
        
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    form.short_ad.data = current_user.short_ad
    form.furaffinity.data = current_user.furaffinity
    form.weasyl.data = current_user.weasyl
    form.website.data = current_user.website
    return render_template('edit_profile.html', form=form)
    
@main.route('/edit-profile/disable',methods=['GET','POST'])
@login_required
def disable_account():
    form = ActivateForm()
    if form.validate_on_submit():
        if current_user.role.name not in ["Banned","Disabled"]:
            current_user.role = Role.query.filter_by(name="Disabled").first()
            flash("You have disabled your account.")
            return redirect(url_for(".index"))
        elif current_user.role.name == "Disabled":
            current_user.role = Role.query.filter_by(name="User").first()
            flash("You have reactivated your account.")
            return redirect(url_for(".index"))

@main.route('/manage-media',methods=['GET','POST'])
@login_required
def user_media():
    all_media = Media.query.all()
    offered_media = current_user.media_offered.all()
    unoffered_media = []
    for i in all_media:
        if i not in offered_media:
            unoffered_media.append(i)
    form = UpdateUserMedia()
    
    if form.validate_on_submit():
        data = request.form
        for media in all_media:
            if media.username in data:
                current_user.offer_media(media)
            else:
                current_user.remove_media(media)
        flash("Changes Saved")
        return redirect(url_for('.user_media'))
    return render_template('user_options.html',media=offered_media,unoffered_media=unoffered_media,form=form)
    
@main.route('/edit-group/<groupname>',methods=['GET', 'POST'])
@login_required
def edit_group(groupname):
    group = Group.query.filter_by(username=groupname).first()
    form = GroupEdit()
    if current_user.id != group.owner_id:
        flash("You are not authorized for this page")
        return redirect(url_for('.index'))
    if form.validate_on_submit():
        group.about_me = form.about_me.data
        db.session.add(group)
        flash('Your group has been updated.')
        return redirect(url_for('.group_page', groupname=groupname))
    form.about_me.data = group.about_me
    return render_template('edit_group.html',form=form,group=group,)
    
@main.route('/edit-group-admin/<groupname>',methods=['GET', 'POST'])
@login_required
@admin_required
def edit_group_admin(groupname):
    group = Group.query.filter_by(username=groupname).first()
    form = GroupEditAdmin()
    if form.validate_on_submit():
        group.about_me = form.about_me.data
        group.username = form.username.data
        group.approved = form.approved.data
        db.session.add(group)
        flash('The group has been updated.')
        return redirect(url_for('.group'))
    form.about_me.data = group.about_me
    form.username.data = group.username
    form.approved.data = group.approved
    return render_template('edit_group.html',form=form,group=group,)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.furaffinity = form.furaffinity.data
        user.weasyl = form.weasyl.data
        user.short_ad = form.short_ad.data
        user.website = form.website.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.short_ad.data = user.short_ad
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.furaffinity.data = user.furaffinity
    form.weasyl.data = user.weasyl
    form.website.data = user.website
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp
    
@main.route("/users")
def user_list():
    players = User.query.all()
    return render_template("user_list.html",
                           players = players,)

    
### Groups ###    
    
@main.route('/group')
def group():
    groups = Group.query.filter_by(approved=True).all()
    pending_groups = Group.query.filter_by(approved=False).all()
    return render_template("groups.html", groups=groups,pending_groups=pending_groups,)

@main.route('/groupapplication', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.FOLLOW)
def group_application():
    form = GroupApplication()
    if form.validate_on_submit():
        username = form.username.data
        about = form.about.data
        owner_id = current_user.id
        group = Group(owner_id=owner_id,username=username,about_me=about)
        db.session.add(group)
        current_user.follow_group(group)
        flash('Your application has been made.')
        return redirect(url_for('.group'))
    return render_template('group_application.html', form=form)
    
@main.route('/grouppage/<groupname>')
def group_page(groupname):
    group = Group.query.filter_by(username=groupname).first()
    users = group.members.all()
    return render_template('group_page.html',group=group,users=users)
    
@main.route('/follow_group/<groupname>')
@login_required
@permission_required(Permission.FOLLOW)
def follow_group(groupname):
    group = Group.query.filter_by(username=groupname).first()
    if group is None:
        flash('Invalid group.')
        return redirect(url_for('.index'))
    if current_user.is_following_group(group):
        flash('You are already following this group.')
        return redirect(url_for('.group_page', groupname=groupname))
    current_user.follow_group(group)
    flash('You are now following %s.' % groupname)
    return redirect(url_for('.group_page', groupname=groupname))
    
@main.route('/unfollow_group/<groupname>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow_group(groupname):
    group = Group.query.filter_by(username=groupname).first()
    if group is None:
        flash('Invalid group.')
        return redirect(url_for('.index'))
    if not current_user.is_following_group(group):
        flash('You are already not following this group.')
        return redirect(url_for('.group_page', groupname=groupname))
    current_user.unfollow_group(group)
    flash('You are no longer following %s.' % groupname)
    return redirect(url_for('.group_page', groupname=groupname))

@main.route('/grouppage/<groupname>/browse',methods=['GET', 'POST'])    
def browse_group(groupname):
    ''' '''
    group = Group.query.filter_by(username=groupname).first()
    if group is None:
        flash("Invalid Group")
        return redirect(url_for(".index"))
    form = GroupBrowseForm()
    options = []
    users = False
    media = Media.query.filter_by(visible=True).all()
    for i in media:
        options.append([i.id,i.username])
    form.choice.choices = options
    matches=[]
    if form.validate_on_submit():
        chosen_media = Media.query.get(form.choice.data)
        media_users = chosen_media.members.all()
        group_users = group.members.all()
        for i in media_users:
            if i in group_users:
                matches.append(i)
        return render_template("group_browse.html",group=group,chosen_media=chosen_media,form=form,users=matches)
    return render_template("group_browse.html",group=group,form=form)
### Media ###

@main.route('/media')
def media():
    media = Media.query.filter_by(visible=True).order_by(Media.username).all()
    hidden_media = Media.query.filter_by(visible=False).order_by(Media.username).all()
    return render_template("media.html", media=media,hidden_media=hidden_media)

@main.route('/create-media', methods=['GET', 'POST'])
@login_required
@admin_required
def create_media():
    form = GroupApplication()
    if form.validate_on_submit():
        username = form.username.data
        about = form.about.data
        media = Media(username=username,description=about)
        db.session.add(media)
        flash('Your application has been made.')
        return redirect(url_for('.media'))
    return render_template('group_application.html', form=form)
    
@main.route('/edit-media/<mediatype>',methods=['GET', 'POST'])
@login_required
@admin_required
def edit_media(mediatype):
    media = Media.query.filter_by(username=mediatype).first()
    form = GroupEditAdmin()
    if form.validate_on_submit():
        media.description = form.about_me.data
        media.username = form.username.data
        media.visible = form.approved.data
        db.session.add(media)
        flash('Your group has been updated.')
        return redirect(url_for('.media_page', mediatype=mediatype))
    form.about_me.data = media.description
    form.username.data = media.username
    form.approved.data = media.visible
    return render_template('edit_media.html',form=form,media=media,)
    
@main.route('/media/<mediatype>')
def media_page(mediatype):
    group = Media.query.filter_by(username=mediatype).first()
    users = group.members.all()
    return render_template('media_page.html',group=group,users=users)
    
@main.route('/offer_media/<mediatype>')
@login_required
@permission_required(Permission.FOLLOW)
def offer_media(mediatype):
    group = Media.query.filter_by(username=mediatype).first()
    if group is None:
        flash('Invalid media.')
        return redirect(url_for('.index'))
    if current_user.is_offering_media(group):
        flash('You are already offering this media.')
        return redirect(url_for('.media_page', mediatype=mediatype))
    current_user.offer_media(group)
    flash('You are now offering %s.' % mediatype)
    return redirect(url_for('.media_page', mediatype=mediatype))
    
@main.route('/remove_media/<mediatype>')
@login_required
@permission_required(Permission.FOLLOW)
def remove_media(mediatype):
    group = Media.query.filter_by(username=mediatype).first()
    if group is None:
        flash('Invalid Media.')
        return redirect(url_for('.index'))
    if not current_user.is_offering_media(group):
        flash('You are already not offering this media.')
        return redirect(url_for('.media_page', mediatype=mediatype))
    current_user.remove_media(group)
    flash('You are no longer offering %s.' % mediatype)
    return redirect(url_for('.media_page', mediatype=mediatype))