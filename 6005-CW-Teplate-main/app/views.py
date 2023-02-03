from .meta import *
import sqlite3
import datetime
import hashlib
import logging
import requests
import os
import bcrypt
#from flask import request
logging.basicConfig(filename="log.txt")
#from flask import session
from werkzeug.utils import secure_filename
from flask import Flask, flash, redirect, session, request
#session['attempts'] = 0
#admin = 0
UPLOAD_FOLDER = '/abby'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
salt = "wCaxz"
#app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#UPLOAD_FOLDER = '/uploads'
@app.route("/")

def index():
    """
    Main Page.
    """

    session['attempt'] = 0
    #Get data from the DB using meta function
    
    rows = query_db("SELECT * FROM product")
    app.logger.info(rows)
    #if admin == 1:
    #    return flask.render_template("admindex.html", bookList = rows)
    #else:
    return flask.render_template("index.html", bookList = rows)


@app.route("/admin")
def admin():
    #theQry = "Select * FROM User WHERE id = '{0}'".format(userId)      
    #userQry =  query_db(theQry, one=True)
    
    rows = query_db("SELECT * FROM product")
    app.logger.info(rows)
    return flask.render_template("admindex.html", bookList = rows)

@app.route('/userview', methods=['GET', 'POST']) #route to view users and set admin 1 or 0
def userView():
    
    if flask.request.method == 'POST':
        #return insertNewStock(, r)
        a=request.form['aidi']
        n=request.form['admp']
        con = sqlite3.connect('database.db')
        con.execute(f"UPDATE user SET adm = '{n}' WHERE id = '{a}'")
        con.commit()
        con.close()
        print("i am success")
    
        #return showusers();
    print("main function")
    con = sqlite3.connect('database.db') #connection to database
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * from user")
    rows = cur.fetchall()
    con.close()
    return flask.render_template("userview.html",rows = rows) #prints out all of the user
    



@app.route("/stockedit", methods=["GET","POST"])
def stockEdit(): 
    if flask.request.method == 'POST':
        #return insertNewStock(, r)
        a=request.form['aidy']
        b=request.form['namee']
        c=request.form['desc']
        d=request.form['pric']
        e=request.form['imag']
        #f=request.form['imag']
        #e.save(app.config["UPLOAD_FOLDER"])
        con = sqlite3.connect('database.db')
        con.execute("INSERT INTO product values(?,?,?,?,?);", (a, b, c, d, e))
        con.commit()
        
        con.close()
        
    
    print("main function")
    con = sqlite3.connect('database.db') #connection to database
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * from product")
    rows = cur.fetchall()
    con.close()
    return flask.render_template("stockedit.html",rows = rows) #prints out all of the user

#@app.route("/stockedit/imag", methods=["GET","POST"])
#def main():
#    if flask.request.method == 'POST':
#        a=request.files['imag']
#        print("got file")
 #       if a:
#            filename = secure_filename(a.filename)    
 #           a.save(app.config['UPLOAD_FOLDER'], filename)
 #           return flask.render_template("stockedit.html")
 #   return flask.render_template("imag.html")



@app.route("/products", methods=["GET","POST"])
def products():
    """
    Single Page (ish) Application for Products
    """
    theItem = flask.request.args.get("item")
    if theItem:
        
        #We Do A Query for It
        itemQry = query_db(f"SELECT * FROM product WHERE id = ?",[theItem], one=True)

        #And Associated Reviews
        #reviewQry = query_db("SELECT * FROM review WHERE productID = ?", [theItem])
        theSQL = f"""
        SELECT * 
        FROM review
        INNER JOIN user ON review.userID = user.id
        WHERE review.productID = {itemQry['id']};
        """
        reviewQry = query_db(theSQL)
        
        #If there is form interaction and they put somehing in the basket
        if flask.request.method == "POST":

            quantity = flask.request.form.get("quantity")
            try:
                quantity = int(quantity)
            except ValueError:
                flask.flash("Error Buying Item")
                return flask.render_template("product.html",
                                             item = itemQry,
                                             reviews=reviewQry)
            
            app.logger.warning("Buy Clicked %s items", quantity)
            
            #And we add something to the Session for the user to keep track
            basket = flask.session.get("basket", {})

            basket[theItem] = quantity
            flask.session["basket"] = basket
            flask.flash("Item Added to Cart")

            
        return flask.render_template("product.html",
                                     item = itemQry,
                                     reviews=reviewQry)
    else:
        
        books = query_db("SELECT * FROM product")        
        return flask.render_template("products.html",
                                     books = books)


# ------------------
# USER Level Stuff
# ---------------------
    
@app.route("/user/login", methods=["GET", "POST"])

def login():
    """
    Login Page
    """
    

    if flask.request.method == "POST":
        #Get data
        user = flask.request.form.get("email")
        user1=user
        password = salt+flask.request.form.get("password")
        encrypt = hashlib.md5(password.encode()).hexdigest() #ENCRYPT
        #encrypt = bcrypt.hashpw(password.encode(), salt)
        app.logger.info("Attempt to login as %s:%s", user, encrypt) #ENCRYPT
        #loglogger=app.logger.info("Attempt to login as %s:%s", user, encrypt) #ENCRYPT
        #logging.info(loglogger)
        theQry = "Select * FROM User WHERE email = '{0}'".format(user)

        userQry =  query_db(theQry, one=True)
        attempt=session["attempt"]
        print(session["attempt"])
        
        #app.logger.info(attempt) #ENCRYPT
        if userQry is None:
            if attempt<5:

                flask.flash("No Such User")
                attempt = session.get('attempt')
                attempt = attempt + 1
                session['attempt'] = attempt
            elif(attempt == 3):
                flask.flash("This is your last attempt to log in")
        else:
            if attempt<5:
                app.logger.info("User is Ok")
                
                #matched = bcrypt.checkpw(userQry["password"], encrypt)
                if userQry["adm"] == 1 and userQry["password"] == encrypt:
                    
                    app.logger.info("ADMIN:Login as %s Success", userQry["email"])
                    flask.session["user"] = userQry["id"]
                    #flask.session["admin"] = userQry["adm"]
                    #admin=+1
                    flask.flash("Login Successful")
                    attempt = 0
                    session['attempt'] = attempt
                    return (flask.redirect(flask.url_for("admin")))
                elif userQry["adm"] == 0 and userQry["password"] == encrypt: #ENCRYPT
                    app.logger.info("Login as %s Success", userQry["email"])
                    flask.session["user"] = userQry["id"]
                    flask.flash("Login Successful")
                    attempt = 0
                    session['attempt'] = attempt
                    return (flask.redirect(flask.url_for("index")))
                else:
                    flask.flash("Password is Incorrect")
                    attempt = session.get('attempt')
                    attempt = attempt + 1
                    session['attempt'] = attempt
            else:
                flask.flash("You can't log in anymore.")
            
    return flask.render_template("login.html")

#def isUserAdmin():



@app.route("/user/create", methods=["GET","POST"])
def create():
    """ Create a new account,
    we will redirect to a homepage here
    """

    if flask.request.method == "GET":
        return flask.render_template("create_account.html")
    
    #Get the form data
    email = flask.request.form.get("email")
    password = salt+flask.request.form.get("password")
    encrypt = hashlib.md5(password.encode()).hexdigest() #ENCRYPT
    #encrypt = bcrypt.hashpw(password.encode(), salt)
    #Sanity check do we have a name, email and password
    if not email or not password: 
        flask.flash("Not all info supplied")
        return flask.render_template("create_account.html",
                                     email = email)


    #Otherwise we can add the user
    theQry = "Select * FROM User WHERE email = '{0}'".format(email)                                                   
    userQry =  query_db(theQry, one=True)
   
    if userQry:
        flask.flash("A User with that Email Exists")
        return flask.render_template("create_account.html",
                                     name = name,
                                     email = email)

    else:
        #Crate the user
        app.logger.info("Create New User")
        #print(encrypt)
        #encrypt=str(encrypt)
        theQry = f"INSERT INTO user (id, email, password, adm) VALUES (NULL, '{email}', '{encrypt}', 0)"
        

        userQry = write_db(theQry)
        
        flask.flash("Account Created, you can now Login")
        return flask.redirect(flask.url_for("login"))

@app.route("/user/<userId>/adminsettings")
def adminSettings(userId):
    """
    Update a users settings, 
    Allow them to make reviews
    """

    theQry = "Select * FROM User WHERE id = '{0}'".format(userId)                                                   
    thisUser =  query_db(theQry, one=True)

    
    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask.url_for("admin"))

    #Purchases
    theSQL = f"Select * FROM purchase WHERE userID = {userId}"
    purchaces = query_db(theSQL)

    theSQL = """
    SELECT productId, date, product.name
    FROM purchase
    INNER JOIN product ON purchase.productID = product.id
    WHERE userID = {0};
    """.format(userId)

    purchaces = query_db(theSQL)
    
    return flask.render_template("adminsettings.html",
                                 user = thisUser,
                                 purchaces = purchaces)

@app.route("/user/<userId>/settings")
def settings(userId):
    """
    Update a users settings, 
    Allow them to make reviews
    """

    theQry = "Select * FROM User WHERE id = '{0}'".format(userId)                                                   
    thisUser =  query_db(theQry, one=True)

    
    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask.url_for("index"))

    #Purchases
    theSQL = f"Select * FROM purchase WHERE userID = {userId}"
    purchaces = query_db(theSQL)

    theSQL = """
    SELECT productId, date, product.name
    FROM purchase
    INNER JOIN product ON purchase.productID = product.id
    WHERE userID = {0};
    """.format(userId)

    purchaces = query_db(theSQL)
    
    return flask.render_template("usersettings.html",
                                 user = thisUser,
                                 purchaces = purchaces)

    
@app.route("/logout")
def logout():
    """
    Login Page
    """
    flask.session.clear()
    return flask.redirect(flask.url_for("index"))
    


@app.route("/user/<userId>/update", methods=["GET","POST"])
def updateUser(userId):
    """
    Process any chances from the user settings page
    """

    theQry = "Select * FROM User WHERE id = '{0}'".format(userId)   
    thisUser = query_db(theQry, one=True)
    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask_url_for("index"))

    #otherwise we want to do the checks
    if flask.request.method == "POST":
        current = salt+flask.request.form.get("current")
        encryptcurrent = hashlib.md5(current.encode()).hexdigest() #ENCRYPT
        #encryptcurrent = bcrypt.hashpw(current.encode(), salt)
        password = salt+flask.request.form.get("password")
        encrypt = hashlib.md5(password.encode()).hexdigest() #ENCRYPT
        #encrypt = bcrypt.hashpw(password.encode(), salt)
        app.logger.info("Attempt password update for %s from %s to %s", userId, encryptcurrent, encrypt)
        app.logger.info("%s == %s", encryptcurrent, thisUser["password"])
        #matched = bcrypt.checkpw(userQry["password"], encryptcurrent)
        if encryptcurrent:
            if encryptcurrent == userQry["password"]:
                app.logger.info("Password OK, update")
                #Update the Password
                encrypt = salt+hashlib.md5(password.encode()).hexdigest() #ENCRYPT
                theSQL = f"UPDATE user SET password = '{encrypt}' WHERE id = {userId}"
                app.logger.info("SQL %s", theSQL)
                write_db(theSQL)
                flask.flash("Password Updated")
                
            else:
                app.logger.info("Mismatch")
                flask.flash("Current Password is incorrect")
            return flask.redirect(flask.url_for("settings",
                                                userId = thisUser['id']))

            
    
        flask.flash("Update Error")

    return flask.redirect(flask.url_for("settings", userId=userId))

# -------------------------------------
#
# Functionality to allow user to review items
#
# ------------------------------------------

@app.route("/review/<userId>/<itemId>", methods=["GET", "POST"])
def reviewItem(userId, itemId):
    """Add a Review"""

    #Handle input
    if flask.request.method == "POST":
        reviewStars = flask.request.form.get("rating")
        reviewComment = flask.request.form.get("review")

        #Clean up review whitespace
        reviewComment = reviewComment.strip()
        reviewId = flask.request.form.get("reviewId")

        app.logger.info("Review Made %s", reviewId)
        app.logger.info("Rating %s  Text %s", reviewStars, reviewComment)

        if reviewId:
            #Update an existing oe
            app.logger.info("Update Existing")

            theSQL = f"""
            UPDATE review
            SET stars = {reviewStars},
                review = '{reviewComment}'
            WHERE
                id = {reviewId}"""

            app.logger.debug("%s", theSQL)
            write_db(theSQL)

            flask.flash("Review Updated")
            
        else:
            app.logger.info("New Review")

            theSQL = f"""
            INSERT INTO review (userId, productId, stars, review)
            VALUES ({userId}, {itemId}, {reviewStars}, '{reviewComment}');
            """

            app.logger.info("%s", theSQL)
            write_db(theSQL)

            flask.flash("Review Made")

    #Otherwise get the review
    theQry = f"SELECT * FROM product WHERE id = {itemId};"
    item = query_db(theQry, one=True)
    
    theQry = f"SELECT * FROM review WHERE userID = {userId} AND productID = {itemId};"
    review = query_db(theQry, one=True)
    app.logger.debug("Review Exists %s", review)

    return flask.render_template("reviewItem.html",
                                 item = item,
                                 review = review,
                                 )

# ---------------------------------------
#
# BASKET AND PAYMEN
#
# ------------------------------------------



@app.route("/basket", methods=["GET","POST"])
def basket():

    #Check for user
    if not flask.session["user"]:
        flask.flash("You need to be logged in")
        return flask.redirect(flask.url_for("index"))


    theBasket = []
    #Otherwise we need to work out the Basket
    #Get it from the session
    sessionBasket = flask.session.get("basket", None)
    if not sessionBasket:
        flask.flash("No items in basket")
        return flask.redirect(flask.url_for("index"))

    totalPrice = 0
    for key in sessionBasket:
        theQry = f"SELECT * FROM product WHERE id = {key}"
        theItem =  query_db(theQry, one=True)
        quantity = int(sessionBasket[key])
        thePrice = theItem["price"] * quantity
        totalPrice += thePrice
        theBasket.append([theItem, quantity, thePrice])
    
        
    return flask.render_template("basket.html",
                                 basket = theBasket,
                                 total=totalPrice)

@app.route("/basket/payment", methods=["GET", "POST"])
def pay():
    """
    Fake paymeent.

    YOU DO NOT NEED TO IMPLEMENT PAYMENT
    """
    
    if not flask.session["user"]:
        flask.flash("You need to be logged in")
        return flask.redirect(flask.url_for("index"))

    #Get the total cost
    cost = flask.request.form.get("total")


    
    #Fetch USer ID from Sssion
    theQry = "Select * FROM User WHERE id = {0}".format(flask.session["user"])
    theUser = query_db(theQry, one=True)

    #Add products to the user
    sessionBasket = flask.session.get("basket", None)

    theDate = datetime.datetime.utcnow()
    for key in sessionBasket:

        #As we should have a trustworthy key in the basket.
        theQry = "INSERT INTO PURCHASE (userID, productID, date) VALUES ({0},{1},'{2}')".format(theUser['id'],
                                                                                              key,
                                                                                              theDate)
                                                                                              
        app.logger.debug(theQry)
        write_db(theQry)

    #Clear the Session
    flask.session.pop("basket", None)
    
    return flask.render_template("pay.html",
                                 total=cost)



# ---------------------------
# HELPER FUNCTIONS
# ---------------------------


@app.route('/uploads/<name>')
def serve_image(name):
    """
    Helper function to serve an uploaded image
    """
    return flask.send_from_directory(app.config["UPLOAD_FOLDER"], name)
    


@app.route("/initdb")
def database_helper():
    """
    Helper / Debug Function to create the initial database

    You are free to ignore scurity implications of this
    """
    init_db()
    return "Done"

