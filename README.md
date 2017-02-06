# FSNDP2 - Full Stack Nano Degree Project 2: Multi-user BLog

This project is a multi-user blog, which people can view blog list but only logged in user can post new content, edit/delete the user's own content, like other users' post, and be able to comment on all posts.

The auther of a comment can also edit or delete the comment.

## Getting Started

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
