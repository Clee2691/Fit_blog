from flask import render_template, url_for, flash, redirect, request
from werkzeug.urls import url_parse
from app import app, db, functions
from app.forms import LoginForm, RegisterForm, PostForm, DataInputForm, CommentForm, MacroForm
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.models import User, Post, Comment

@app.route('/')
@app.route('/home')
def home():

    user = User.query.filter_by(username='clee2691').first()

    page = request.args.get('page', 1, type=int)

    # For new databases, will produce an error if no user or posts. This stops that
    if user:
        posts = user.posts.order_by(Post.timestamp.desc()).paginate(page,app.config['POSTS_PER_PAGE'], False)
        next_url = url_for('home', page=posts.next_num) if posts.has_next else None
        prev_url = url_for('home', page=posts.prev_num) if posts.has_prev else None
        return render_template('home.html', title='TC&NG - Home', posts=posts.items, next_url=next_url, prev_url=prev_url)
    else:
        return render_template('home.html', title='TC&NG - Home')

@app.route('/post_submission', methods =['GET','POST'])
@login_required
def submit_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post successfully made!', 'success')
        return redirect(url_for('home'))

    return render_template('post_submission.html', title='TC&NG - Submit Post', form=form)

@app.route('/edit_post/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):

    post = Post.query.get(id)

    form = PostForm(title = post.title, post = post.body )

    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.post.data
        post.edited_time= datetime.utcnow()
        db.session.commit()

        flash('Post successfully edited!', 'success')
        return redirect(url_for('post_view', id = post.id))

    return render_template("edit_post.html", form=form)

@app.route('/delete_post/<int:id>', methods=['GET','POST'])
@login_required
def delete_post(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/delete_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get(id)
    post_id = comment.content_id

    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('post_view', id= post_id))

@app.route('/post/<int:id>', methods=['GET','POST'])
def post_view(id):
    post = Post.query.get(id)
    comments = post.comments.all()
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(name = form.name.data, body = form.comment.data, content = post) # needed to put backref "content" as the post so it can be recognized
        db.session.add(comment)
        db.session.commit()
        flash('Comment successfully made!', 'success')
        return redirect(url_for('post_view', id = post.id))

    if comments:
        comments_desc = post.comments.order_by(Comment.timestamp.desc())
        return render_template('post.html', post=post, form=form, comments = comments_desc, num_comments = len(comments))
    else:
        return render_template('post.html', post=post, form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        # Needed for redirect to login after a page forces login_required
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        flash('Success! You are now logged in as {}'.format(user.username),'success')
        return redirect(next_page)

        flash('Success! You are now logged in as {}'.format(user.username),'success')
        return redirect(url_for('home'))

    return render_template('login.html', title='TC&NG - Login', form = form)

@app.route('/secret_register_cl', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User, {} successfully registered!'.format(form.username.data),'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='TC&NG - Register', form = form)

@app.route('/about')
def about():
    return render_template('about.html', title='TC&NG - About')

@app.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('home'))

@app.route('/tdee_calc', methods=['GET','POST'])
def tdee_calc():
    form = DataInputForm()

    if form.validate_on_submit():
        ft = form.height_feet.data
        inch = form.height_inch.data
        wt = form.weight.data
        age = form.age.data
        gender = form.gender.data
        act_level = form.activity_level.data

        data_list = [ft, inch, wt, age, gender, act_level]

        return redirect(url_for('tdee_calc_result', data = data_list))

    return render_template('tdee/tdeeCalc.html',title='TC&NG - TDEE Calculator' , form=form)

@app.route('/tdee_result', methods=['POST', 'GET'])
def tdee_calc_result():
    
    data = request.args.getlist('data') #[ft, inch, wt, age, gender, act_level]
    form = MacroForm()

    data_num = []

    for item in data:
        try:
            data_num.append(float(item))
        except:
            data_num.append(item)
    
    carbs = 25
    fats = 35
    prot = 40

    ht_met, wt_met = functions.imp_to_met(data_num[0], data_num[1], data_num[2])

    bmr, tdee = functions.tdee_calc(ht_met, wt_met, data_num[3], data_num[5], data_num[4])

    calories = 500

    cut = tdee - calories
    bulk = tdee + calories

    cut_mac = functions.macro_calc(cut, carbs, fats, prot)
    bulk_mac = functions.macro_calc(bulk, carbs, fats, prot)
    maint_mac = functions.macro_calc(tdee, carbs, fats, prot)

    if form.validate_on_submit():
        carbs = form.carb_perc.data
        fats = form.fat_perc.data
        prot = form.protein_perc.data

        perc_total = carbs + fats + prot

        if perc_total == 100:

            cut_mac = functions.macro_calc(cut, carbs, fats, prot)
            bulk_mac = functions.macro_calc(bulk, carbs, fats, prot)
            maint_mac = functions.macro_calc(tdee, carbs, fats, prot)

            return render_template('tdee/tdee_results.html', 
                                    data=data, cut= cut, bulk=bulk, tdee=tdee, bmr=bmr,
                                    cut_mac = cut_mac, bulk_mac = bulk_mac, maint_mac=maint_mac, form = form)
        else:
            return render_template('tdee/tdee_results.html',
                                    data=data, cut= cut, bulk=bulk, tdee=tdee, bmr=bmr,
                                    cut_mac = cut_mac, bulk_mac = bulk_mac, maint_mac=maint_mac, form = form)

    return render_template('tdee/tdee_results.html', 
                            tdee = tdee, bmr = bmr, data = data,
                            cut= cut, bulk = bulk,
                            cut_mac = cut_mac, bulk_mac = bulk_mac, maint_mac=maint_mac, form = form)