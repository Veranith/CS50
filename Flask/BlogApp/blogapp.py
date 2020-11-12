from flask import Flask, render_template, url_for
app = Flask(__name__)

posts = [
    {
        'author': 'Ryan',
        'title': 'Post 1',
        'content': 'Post content',
        'date_posted': '10 Nov 2020'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', post=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


if __name__ == '__main__':
    app.run(debug=True)