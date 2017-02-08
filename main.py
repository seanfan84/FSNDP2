import os
import webapp2
import jinja2
import codecs
import datetime
import random
import string
import hashlib

from jinja2 import Template
from jinja2 import Environment, PackageLoader

from google.appengine.ext import db
import re

import logging  # for logging bugs
import time

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


def make_salt():
    return ''.join(random.choice(string.letters) for i in range(5))


def make_pw_hash(name, pw):
    salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)


def valid_pw(name, pw, h):
    if h.split(",")[0] ==  \
            hashlib.sha256(name + pw + h.split(",")[1]).hexdigest():
        return True
    else:
        return False


# Data
class Blog(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    user = db.StringProperty(required=True)
    likecount = db.IntegerProperty(default=0)


class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    signupdate = db.DateTimeProperty(auto_now_add=True)


class Like(db.Model):
    user_id = db.StringProperty(required=True)
    post_id = db.StringProperty(required=True)


class Comment(db.Model):
    post = db.ReferenceProperty(Blog)
    content = db.TextProperty(required=True)
    user = db.ReferenceProperty(User)
    created = db.DateTimeProperty(auto_now_add=True)

# Input Verification
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Handler(webapp2.RequestHandler):
    """docstring for Handler"""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_cookie(self, user, rememberme='0'):
        # self.response.headers.add_header('Set-Cookie\
        # ','name= %s'%(str(user.username)))
        # self.response.headers.add_header('Set-Cookie\
        # ','UID= %s'%user.key().id())
        logging.info('setting cookie')
        if rememberme == '1':
            self.response.set_cookie(
                'name',
                str(user.username),
                path='/',
                expires=datetime.datetime.now() + datetime.timedelta(weeks=4))
            self.response.set_cookie(
                'UID',
                str(user.key().id()),
                path='/',
                expires=datetime.datetime.now() + datetime.timedelta(weeks=4))
            self.response.set_cookie(
                'PID',
                user.password.split(",")[0],
                path='/',
                expires=datetime.datetime.now() + datetime.timedelta(weeks=4))
        else:
            self.response.set_cookie('name', str(user.username), path='/')
            self.response.set_cookie('UID', str(user.key().id()), path='/')
            self.response.set_cookie(
                'PID',
                user.password.split(",")[0],
                path='/')

        # self.redirect('/welcome?name= '+username)
        self.redirect('/')


    def valid_cookie(self, redirect=True):
    	#There is a bug in this function
    	#Only user id, and password are checked
    	#As blog only have username saved
        username = self.request.cookies.get("name")
        uid = self.request.cookies.get('UID')
        pid = self.request.cookies.get('PID')
        params = dict()

        if username and uid and pid:
            user = User.get_by_id(int(uid))
            if pid != user.password.split(',')[0] or username != user.username:
                if redirect is True:
                    self.redirect('/login')
                return params
        else:
            if redirect is True:
                self.redirect('/login')
            return params
        params['name'] = username
        params['button'] = 'Logout'
        params['link'] = '/logout'
        params['UID'] = uid
        params['user'] = user
        params['PID'] = pid
        return params


class SignUp(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get('email')

        params = dict(
            username=username,
            password=password)

        if not valid_username(username):
            params['error_username'] = 'Invalid Username'
            have_error = True
        if not valid_password(password):
            params['error_password'] = 'Invalid Password:Under 3 or\
            over 20 digits'
            have_error = True
        if password != verify:
            params['error_verify'] = 'Passwords do not match'
            have_error = True
        if not valid_email(email):
            params['error_email'] = "invalid email address"
            have_error = True

        if (User.gql("where username=:1", username).get()):
            params['error_username'] = 'User already exists'
            have_error = True

        if have_error is True:
            self.render('signup.html', **params)
        else:
            h = make_pw_hash(username, password)
            user = User(username=username, password=h)
            user.put()
            time.sleep(0.1)
            self.set_cookie(user)


class Login(Handler):
    def get(self):
        self.render('login.html')

    def valid_user(self, username, password):
        user = db.GqlQuery(
            'select * from User where username=:1', username).get()
        if user and valid_pw(username, password, user.password):
            return user

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        chkRM = self.request.get('chkRM')

        user = self.valid_user(username, password)
        if user:
            self.set_cookie(user, chkRM)

        else:
            self.render('login.html', username=username, error="invalid login")


class Logout(Handler):
    def get(self):
        # self.response.headers.add_header('Set-Cookie','name= ')
        self.response.delete_cookie('name')
        self.response.delete_cookie('UID')
        self.response.delete_cookie('PID')
        self.redirect('/login')


class NewPost(Handler):

    def render_front(self, subject="", content="", error_subject="",
                     error_content="", **params):

        self.render(
            'newpost.html', subject=subject,
            content=content, error_subject=error_subject,
            error_content=error_content, **params)

    def get(self):
        params = self.valid_cookie()
        self.render_front(**params)

    def post(self):
        params = self.valid_cookie()
        subject = self.request.get('subject')
        content = self.request.get('content')
        params['subject'] = subject
        params['content'] = content

        #check if the user is logged in and making sure nobody is playing
        #tricks with params['name']
        if not params['user'] or not params['user'].username == params['name']:
        	self.response.write("you are not authorised to perform this \
        		operation due to verification issue, click <a href='/'>Here\
        		</a> to go to homepage")

        if not subject:
            params['error_subject'] = 'The blog must have a tittle'
        if not content:
            params['error_content'] = 'The blog must have a content'
        if subject and content:
            blog = Blog(subject=subject, content=content, user=params['name'])
            blog.put()
            time.sleep(0.1)

            self.redirect('/post/' + str(blog.key().id()))
        else:
            self.render_front(**params)


class BlogList(Handler):
    def get(self):
        params = self.valid_cookie(False)
        if not any(params):
            params['name'] = 'Guest'
            params['link'] = '/login'
            params['button'] = "Login"
        blogs = db.GqlQuery('select * from Blog order by created desc')
        params['blogs'] = blogs
        self.render("bloglist.html", **params)


class HomePage(Handler):
    def get(self):
        params = self.valid_cookie(False)
        # check if param is empty any()check if there is at least one
        if not any(params):
            self.render(
                'homepage.html', name='Guest',
                link="/login", button="LOGIN")
        else:
            self.render('homepage.html', **params)


class MyPosts(Handler):
    def get(self):
        params = self.valid_cookie()
        if any(params):
            user = params['user']
            blogs = db.GqlQuery(
                'select * from Blog where user=:1', params['name'])
            params['blogs'] = blogs
            self.render('myposts.html', **params)
        else:
            self.redirect('/login')


class PostDelete(Handler):
    def get(self, blog_id):
        self.response.write('entered handler corretly.')
        params = self.valid_cookie()
        blog = Blog.get_by_id(int(blog_id))
        if blog.user == params['name'] and \
        params['name'] == params['user'].username:

            comments = Comment.gql('where post=:post', post=blog)
            for c in comments:
                c.delete()
            likes = Like.gql(
                'where post_id=:post_id', post_id=blog.key().id())
            for l in likes:
                l.delete()
            blog.delete()
            time.sleep(0.1)
        self.redirect('/myposts')


class PostEdit(Handler):

    def get(self, blog_id):
        params = self.valid_cookie()
        blog = Blog.get_by_id(int(blog_id))
        if blog.user == params['name']:
            params['user'] = blog.user
            params['subject'] = blog.subject
            params['content'] = blog.content
            params['sourceUrl'] = "/myposts"
            self.render('editpost.html', **params)
        else:
            self.redirect('/myposts')

    def post(self, blog_id):
        params = self.valid_cookie()
        blog = Blog.get_by_id(int(blog_id))
        user = params['user']

        if params['name'] == blog.user and user and \
        user.username == params['name']:
	        subject = self.request.get('subject')
	        content = self.request.get('content')

        if not content:
            params['error_content'] = 'content cannot be empty'
        if not subject:
            params['error_subject'] = 'subject cannot be empty'
        if subject and content:
            blog.subject = subject
            blog.content = content
            blog.put()
            time.sleep(0.2)
            self.redirect('/myposts')
        else:
            params['subject'] = subject
            params['content'] = content
            self.render('editpost.html', **params)


class PostLike(Handler):
    def get(self, post_id):
        params = self.valid_cookie()
        post = Blog.get_by_id(int(post_id))

        if post.user == params['name']:
            self.response.write('You cannot like your\
             own post, click <a href= "/bloglist">here</a> to get back')
        else:
            user_id = params['UID']
            like = db.GqlQuery(
                'select * from Like where user_id=:1 and post_id=:2',
                user_id, post_id).get()
            post = Blog.get_by_id(int(post_id))

            if like:
                like.delete()
                post.likecount = post.likecount - 1
                post.put()
                time.sleep(0.1)
                self.redirect('/bloglist')
            else:
                Like(user_id=user_id, post_id=post_id).put()
                post.likecount = post.likecount + 1
                post.put()
                time.sleep(0.1)
                self.redirect('/bloglist')


class SinglePost(Handler):
    def get(self, post_id):
        params = self.valid_cookie()
        post = Blog.get_by_id(int(post_id))
        params['blog'] = post
        comments = Comment.gql('where post=:1 order by created desc  ', post)
        params['comments'] = comments
        params['sourceUrl'] = "/bloglist"

        self.render("blog_single.html", **params)


class CommentSubmit(Handler):
    def post(self, post_id):
        params = self.valid_cookie()
        user = User.get_by_id(int(params['UID']))
        post = Blog.get_by_id(int(post_id))

        if not user or user.username != params['name']:
        	self.response.write("Operation not permitted, contact Admin. \
        		Click <a href='/'>Here</a> to get back to homepage")

        content = self.request.get('content')
        # logging.info(content)
        comment = Comment(post=post, content=content, user=user)
        comment.put()
        time.sleep(0.15)
        self.redirect('/post/' + post_id)


class CommentDelete(Handler):
    def get(self, comment_id):
        params = self.valid_cookie()
        comment = Comment.get_by_id(int(comment_id))
        sourceURL = '/post/' + str(comment.post.key().id())
        if params['UID'] == str(comment.user.key().id()):
            # self.response.write('you are about to delete a comment')
            comment.delete()
            time.sleep(0.1)
            self.redirect(sourceURL)
        else:
            self.response.write(
                'Only comment submitter can delete a \
                comment, click <a href= "%s"> Here </a> to get back'
                % str(sourceURL))


class CommentEdit(Handler):
    def get(self, comment_id):
        params = self.valid_cookie()
        comment = Comment.get_by_id(int(comment_id))
        params['comment'] = comment
        sourceURL = '/post/'+str(comment.post.key().id())
        params['sourceUrl'] = sourceURL
        if params['UID'] == str(comment.user.key().id()):
            # self.response.write('you are about to edit a comment')
            self.render('editcomment.html', **params)
        else:
            self.response.write('Only comment submitter can edit a comment,\
             click <a href= "%s"> Here </a> to get back' % str(sourceURL))

    def post(self, comment_id):
        params = self.valid_cookie()
        comment = Comment.get_by_id(int(comment_id))
        sourceURL = '/post/' + str(comment.post.key().id())
        if params['UID'] == str(comment.user.key().id()):
            content = self.request.get('content')
            comment = Comment.get_by_id(int(comment_id))
            comment.content = content
            comment.put()
            time.sleep(0.1)
            self.redirect(sourceURL)
        else:
            self.response.write('Only comment submitter can edit a comment,\
            click <a href= "%s"> Here </a> to get back' % str(sourceURL))


app = webapp2.WSGIApplication([
    ('/', HomePage),

    ('/signup', SignUp),
    ('/login', Login),
    ('/logout', Logout),

    ('/newpost', NewPost),
    ('/bloglist', BlogList),
    (r'/postlist/(\d+)/like', PostLike),

    ('/myposts', MyPosts),
    (r'/myposts/(\d+)/delete', PostDelete),
    (r'/myposts/(\d+)/edit', PostEdit),

    (r'/post/(\d+)', SinglePost),  # r stands for Raw u stands for Unicode
    (r'/post/(\d+)/comment', CommentSubmit),
    (r'/comment/(\d+)/delete', CommentDelete),
    (r'/comment/(\d+)/edit', CommentEdit)

], debug=True)
