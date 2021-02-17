from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField, FloatField
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, InputRequired
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=32)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=32)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user is not None:
            raise ValidationError('Please pick a different username!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is not None:
            raise ValidationError('Please use a different email address!')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=140)])
    post = PageDownField('Say Something...', validators=[DataRequired()])
    submit = SubmitField('Post')


class DataInputForm(FlaskForm):
    height_feet = IntegerField("Height (Feet)", validators=[DataRequired(), NumberRange(4,8,message='Enter a number from 4 to 8')])
    height_inch = IntegerField('Height (Inches)', validators=[InputRequired(), NumberRange(0, 11, message= 'Enter a number from 0 to 11')])
    weight = FloatField('Weight (lbs)', validators=[DataRequired(),NumberRange(10, 1000, message='Enter a number from 10 to 1000')])
    age = IntegerField('Age', validators=[DataRequired(),NumberRange(4,150, message='Enter a number from 4 to 150')])
    gender = SelectField('Gender', choices=[('male', 'Male'),('female','Female')])
    activity_level = SelectField('Activity Level',
                                 choices=[(1.2,'Sedentary'),(1.375,'Lightly Active'),(1.55,'Moderately Active'),(1.725, 'Very Active'),(1.9, 'Extremely Active')], coerce=float)
    submit = SubmitField('Calculate')


class MacroForm(FlaskForm):

    carb_perc = FloatField('Carb Percent (%)', validators = [DataRequired(), NumberRange(0,100, message='Enter a valid number from 0 to 100')], default= 25)
    fat_perc = FloatField('Fat Percent (%)', validators = [DataRequired(), NumberRange(0,100, message='Enter a valid number from 0 to 100')], default=35)
    protein_perc = FloatField('Protein Percent (%)', validators = [DataRequired(), NumberRange(0,100, message='Enter a valid number from 0 to 100')], default=40)
    submit = SubmitField("Calculate")

    def validate_on_submit(self):
        if not super().validate():
            return False
        """
        Check if percents add up to 100 for all 3 macro fields
        """
        percent_sum = self.carb_perc.data + self.fat_perc.data + self.protein_perc.data

        if percent_sum != 100.00:
            self.carb_perc.errors = ["Macro split must equal 100%! Results rolled back to default."]
            self.fat_perc.errors = ["Macro split must equal 100%! Results rolled back to default."]
            self.protein_perc.errors = ["Macro split must equal 100%! Results rolled back to default."]
            return False

        return True


class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min = 2, max = 140, message = 'Enter a name between 2 and 140 characters.')])
    comment = PageDownField('Say something... (Must be >= 3 characters)', validators=[DataRequired(), Length(min = 3, message = 'Enter a message greater >= 3 characters')])
    submit = SubmitField('Comment')