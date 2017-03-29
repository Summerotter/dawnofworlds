from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, HiddenField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')
    
class ActivateForm(Form):
    deactivate = SelectField('Deactivate', coerce=int,  choices=[(0,"Enabled"),(1,"Disabled"),])


class EditProfileForm(Form):
    
    name = StringField('Real name', validators=[Length(1, 24)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = PageDownField('About me')
    short_ad = TextAreaField('Short Ad',validators=[Length(0,140)])
    weasyl = StringField('Weasyl Account Name', validators=[Length(0, 128)])
    furaffinity = StringField('Furaffinity Account Name', validators=[Length(0, 128)])
    website = StringField('Website URL', validators=[Length(0, 128)])
    submit = SubmitField('Submit')

class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 24), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(1, 24)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = PageDownField('About me')
    short_ad = TextAreaField('Short Ad',validators=[Length(0,140)])
    weasyl = StringField('Weasyl Account Name', validators=[Length(0, 128)])
    furaffinity = StringField('Furaffinity Account Name', validators=[Length(0, 128)])
    website = StringField('Website URL', validators=[Length(0, 128)])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')

class GroupApplication(Form):
    username = StringField('Group Name', validators=[Length(0, 64)])
    about = PageDownField("Group Info", validators=[Required()])
    submit = SubmitField('Submit')
     
class GroupEdit(Form):
    about_me = PageDownField("Group Info", validators=[Required()])
    submit = SubmitField('Submit')
    
class GroupEditAdmin(Form):
    username = StringField('Group Name', validators=[Length(0, 64)])
    about_me = PageDownField("Group Info", validators=[Required()])
    approved = BooleanField('Approved')
    submit = SubmitField('Submit')
    
class UpdateUserMedia(Form):
    submit = SubmitField('Submit')
    
class GroupBrowseForm(Form):
    choice = SelectField('Choice', coerce=int)
    submit = SubmitField('Submit')
