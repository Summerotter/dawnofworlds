from flask.ext.wtf import Form
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, IntegerField, SelectField, RadioField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, InputRequired
from app.models import World, Race

class MakeWorld(Form):
    world = StringField('world',validators=[DataRequired()])
    size = IntegerField('size', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self):
        Form.__init__(self)

class MakeRace(Form):
    culture = StringField('culture_name',validators=[DataRequired()])
    race = StringField('race_name',validators=[DataRequired()])
    align = IntegerField('alignment', validators=[InputRequired()])
    subrace = SelectField('subrace',coerce=int)
    religion = StringField('religion',validators=[DataRequired()])
    made_by = SelectField('made_by',coerce=int)


    def __init__(self):
        Form.__init__(self)
        
class MakePlayer(Form):
    player_name = StringField("player_name", validators=[DataRequired()])

    def __init__(self):
        Form.__init__(self)

class MakeAvatar(Form):
    name = StringField("name", validators=[DataRequired()])
    god = SelectField('owner',coerce=int)
    description = StringField("description")
    def __init__(self):
        Form.__init__(self)
   
class MakeCity(Form):
    name = StringField("name", validators=[DataRequired()])
    alignment= IntegerField("alignment",validators=[InputRequired()])
    
class MakeOrder(Form):
    owner = SelectField("owners",coerce=int)
    name = StringField("name", validators=[DataRequired()])
    description = TextAreaField("description",validators=[DataRequired()])
    type = SelectField("type",coerce=int, choices=[[2,"Religious"],[3,"Military"],[4,"Trade"],[5,"Criminal"],[6,"Technology"],[7,"Magic"],])

    def __init__(self):
        Form.__init__(self)
    
class LoginForm(Form):
    user = StringField("user",validators=[DataRequired()])
    password = StringField("password",validators=[DataRequired()])

class AddPlayer(Form):
    player_list = SelectField("player_list",coerce=int)

    def __init__(self):
        Form.__init__(self)

class MakeProvBldg(Form):
    name = StringField("name", validators=[DataRequired()])
    description = StringField("description")

    def __init__(self):
        Form.__init__(self)
    
class MakeCityBldg(Form):
    name = StringField("name", validators=[DataRequired()])
    description = StringField("description", validators=[DataRequired()])
    
class MakeArmy(Form):
    name = StringField("name", validators=[DataRequired()])
    army = SelectField("army", coerce=int, choices=[[1,"Army"],[0,"Navy"],])

class MakeEvent(Form):
    event_info = StringField("event_info", validators=[DataRequired()])
    played_by = SelectField("played_by", coerce=int)
    duration = SelectField("duration", coerce=int, choices=[[9001,'Forever'],[1,'One Turn'],[2,'Two Turn'],[3,'Three Turn'],[4,'Four Turn'],[5,'Five Turn'],])
    x_coords = []
    y_coords = []
    for i in range(50):
        x_coords.append([i,"x"+str(i)])
        y_coords.append([i,"y"+str(i)])
    
    letter = SelectField("letter", coerce=int, choices=x_coords,validators=[InputRequired()])
    number = SelectField("number", coerce=int, choices=y_coords,validators=[InputRequired()])
#    def __init__(self):
#        Form.__init__(self)

class RemoveEvent(Form):
    played_by = SelectField("played_by", coerce=int,validators=[DataRequired()])
    removal = SelectField("duration", coerce=int,validators=[DataRequired()])

        

class UpdateLocation(Form):
    x_coords = []
    y_coords = []
    for i in range(50):
        x_coords.append([i,"x"+str(i)])
        y_coords.append([i,"y"+str(i)])
    
    letter = SelectField("letter", coerce=int, choices=x_coords,validators=[InputRequired()])
    number = SelectField("number", coerce=int, choices=y_coords,validators=[InputRequired()])
class Rename(Form):
    new_name = StringField("new_name",validators=[DataRequired()])

class NewOwner_Form(Form):
    new_owner = SelectField("new_owner",coerce=int,validators=[DataRequired()])

class Destroy_Form(Form):
    destroy = BooleanField("destroy",validators=[DataRequired()])
    
class AdvanceTurn(Form):
    advance_turn = HiddenField("advance_turn")
    
class AdvanceAge(Form):
    advance_age =  HiddenField("advance_age")

class ArmySupportFrom(Form):
    support = SelectField("support",coerce=int,validators=[DataRequired()])
    
class UpdatePoints(Form):
    points = IntegerField("update_points", validators=[DataRequired()])
    def __init__(self):
        Form.__init__(self)
        
class HistoryEntry(Form):
    text = StringField("entry",validators=[DataRequired()])
    
class ChangeTerrain(Form):
    terrain = SelectField("terrain")

class WorldOwner(Form):
    player_list = SelectField("player_list",coerce=int)

    def __init__(self):
        Form.__init__(self)
        
class CommandRace(Form):
    command_list = SelectField("order_list", coerce=int)
    submit = SubmitField('Submit')
    
class CommandOrder(Form):
    command_list = SelectField("order_list", coerce=int)
    submit = SubmitField('Submit')
    
class ExpandButton(Form):
    submit = SubmitField("Submit")
    
class SpawnRace(Form):
    submit = SubmitField("Submit")

class AvatarMovement(Form):
    move = HiddenField("move")