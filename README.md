# FSNDP2 - Full Stack Nano Degree Project 2: Multi-user BLog

This project is a multi-user blog, which people can view blog list but only logged in user can post new content, edit/delete the user's own content, like other users' post, and be able to comment on all posts.

The auther of a comment can also edit or delete the comment.
## Prerequisites
*Must have Google App Engine installed and configured on your local machine.
*install google app engine python component
```
gcloud components install app-engine-python
```
*install jinja2 if you plan to use on localhost
```
pip install Jinja2
```
## Getting Started
*clone the repository to your local machine
*in command line window, navigate to the repository
*if you would like to test on local host, navigate to the parent folder of the repository and type:
```
dev_appserver.py engineapp
```
*if you would like to deploy, you need to
*deploy index.yaml first, after the index is built, deploy the app
example:
```
gclould app deploy index.yaml
# Wait for the index to be built, then
gclould app deploy engineapp
```
### Running on localhost
if you are running localhost on port 8080
your starting page will be:

* [http://localhost:8080/](http://localhost:8080/)


## Viewing as a guest

If you did not log in, you will be viewing as a guest which has limited access.
Guest can only access:
* [http://localhost:8080/bloglist](http://localhost:8080/bloglist) - All Post (without like/comment access)
* [http://localhost:8080/signup](http://localhost:8080/signup) - Sign up page
* [http://localhost:8080/login](http://localhost:8080/login) - login page

You will be redirected to login page if you try to access a page which logged in user can access

## Login/Sign Up

You can switch between [Login](http://localhost:8080/login) page and [SignUp](http://localhost:8080/signup) page following the link on the page.
Login sets cookies, remember me will set the cookies to expire in 4 weeks
## Logged in User

Here is the operation a logged in user can have.
### Logout
It clears cookie
### Post new content

### Like posts in All Posts page.

### Click on the title of a post and look at its detail

This page shows all the comments.

### Post Comment

User can write and submit comments by hitting submit button under the comment

### Delete Comment

User can delete comment by hitting delete button under the comment.

### Edit Comment

User will be redirected to a separate page to edit the comment

## Authors

* **Sean Fan** - *Initial work* - [SeanFan84](https://github.com/seanfan84)

## License

This project is not licensed.

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
