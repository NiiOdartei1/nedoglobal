from flask import Flask, render_template, jsonify, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import sys, os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ngo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

print("Flask app initializing...")  # Check if app starts


#------------- MODELS ----------------
class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

class FeaturedProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=True)


#------------- MAIN ROUTES ----------------
@app.route('/admin')
def admin_dashboard():
    news_articles = NewsArticle.query.order_by(NewsArticle.date_posted.desc()).all()
    return render_template('admin/admin.html', news_articles=news_articles)


@app.route('/admin/news/edit/<int:id>', methods=['GET', 'POST'])
def edit_news(id):
    article = NewsArticle.query.get_or_404(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        
        # If a new image is uploaded, update it
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                article.image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        db.session.commit()
        flash('News updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_news.html', article=article)


@app.route('/admin/news/delete/<int:id>', methods=['POST'])
def delete_news(id):
    article = NewsArticle.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    flash('News deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/news', methods=['POST'])
def admin_news_post():
    if 'image' not in request.files:
        return redirect(request.url)
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    title = request.form['title']
    content = request.form['content']

    new_article = NewsArticle(title=title, content=content, image_url=image_url)
    db.session.add(new_article)
    db.session.commit()

    return redirect(url_for('news'))

@app.route('/news')
def news():
    news_articles = NewsArticle.query.order_by(NewsArticle.date_posted.desc()).all()
    featured_projects = FeaturedProject.query.all()
    return render_template('news.html', news_articles=news_articles, featured_projects=featured_projects)


@app.route('/')
def index():
    print("Rendering index.html")  # Track function call
    return render_template('index.html')


#----------- ABOUT US ------------------
@app.route('/mission-vision')
def mission_vision():
    return render_template('mission_vision.html')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/testimonials')
def testimonials():
    print("Rendering testimonials.html")
    reviews = [
        {"name": "John Doe", "text": "Amazing platform!"},
        {"name": "Jane Smith", "text": "This service changed my life."},
        {"name": "Carlos M.", "text": "Highly recommended!"}
    ]
    return render_template('testimonials.html', reviews=reviews)


#----------- ARTICLES ------------------
@app.route('/stories')
def stories():
    app.logger.info("Rendering stories.html")
    print("Rendering stories.html")
    return render_template('stories.html')

@app.route('/programs')
def programs():
    app.logger.info("Rendering programs.html")
    print("Rendering programs.html")
    return render_template('programs.html')

@app.route('/articles/impact')
def impact_article():
    print("Rendering impact.html")
    return render_template('impact.html')

@app.route("/articles/innovation")
def innovation():
    return render_template("innovation.html")

#-------------------------------------------
@app.route('/women-empowerment')
def women_empowerment():
    return render_template('women_empowerment.html')

@app.route('/education')
def education():
    return render_template('education.html')  # Ensure education.html exists

@app.route('/healthcare')
def healthcare():
    return render_template('healthcare.html')

@app.route('/agriculture')
def agriculture():
    return render_template('agriculture.html')

#----------- NEWS ------------------
#@app.route('/news')
#def news():
 #   print("Rendering news.html")
  #  return render_template('news.html')

#----------- DONATE ------------------
@app.route('/donate')
def donate():
    print("Rendering donate.html")
    return render_template('donate.html')

#-----------CONTACT_US------------------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        # Here you can add code to save the message to a database or send an email

        flash("Thank you for contacting us! We will get back to you soon.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/youth-empowerment')
def youth_empowerment():
    return render_template('youth_empowerment.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if email:
        flash("You have successfully subscribed!", "success")
    return redirect(url_for("home"))


#----------- DONATE ------------------
import requests
import base64

def send_sms(to_number, message):
    client_id = 'your_hubtel_client_id'
    client_secret = 'your_hubtel_client_secret'
    sender_id = 'NEDO-Global'  # must be approved by Hubtel

    url = "https://smsc.hubtel.com"

    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/json"
    }

    data = {
        "From": sender_id,
        "To": to_number,
        "Content": message
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("SMS sent successfully")
    else:
        print("Failed to send SMS", response.text)


# Error handling for 404
@app.errorhandler(404)
def page_not_found(e):
    print("404 error triggered")
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database and tables are created
    print("Starting Flask app...")
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Flask crashed with error: {e}", file=sys.stderr)
