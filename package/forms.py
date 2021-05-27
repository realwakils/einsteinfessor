from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from package import db
from package.models import Calculation
import re

class Lesson(FlaskForm):
    def hasResults(form, field):
        code = field.data
        locs = [i.start() for i in re.finditer('"explanation":"', code)]
        if not locs:
            print("Error: No questions has been found")
            raise ValidationError('Ingen spørgsmål blev fundet')

    content = TextAreaField('Kilden', validators=[DataRequired(message="Udfyld venligst formularen først"), hasResults])
    submit = SubmitField('Få Svar')