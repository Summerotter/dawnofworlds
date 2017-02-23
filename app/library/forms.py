from flask.ext.wtf import Form
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, IntegerField, SelectField, RadioField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, InputRequired
from app.models import Books, Author, Publisher, Series


        
class MakeBook(Form):
    book_title = StringField("book_title", validators=[DataRequired()])

    def __init__(self):
        Form.__init__(self)

class MakeAuthor(Form):
    author_name = StringField("author_name", validators=[DataRequired()])

    def __init__(self):
        Form.__init__(self)

class MakePublisher(Form):
    publisher_name = StringField("publisher_name", validators=[DataRequired()])

    def __init__(self):
        Form.__init__(self)

        
class MakeSeries(Form):
    series_name = StringField("series_name", validators=[DataRequired()])

    def __init__(self):
        Form.__init__(self)
