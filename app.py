from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import secrets

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend') #correct static and template folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/kangers.db'  # Use relative path
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generate a random secret key
# app.config['UPLOAD_FOLDER'] = 'uploads'  #  If you were handling direct uploads
db = SQLAlchemy(app)

# --- Database Model ---
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)  # Store URL or Cloudinary/S3 ID
    # filename = db.Column(db.String(255))  #  If storing filenames locally

    def __repr__(self):
        return f'<Video {self.title}>'
# --- API Routes ---

@app.route('/api/videos', methods=['GET', 'POST'])
def videos():
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        # file = request.files.get('file')  # For direct file uploads

        # --- Input Validation (CRUCIAL) ---
        if not title or not url:
            return jsonify({'message': 'Title and URL are required'}), 400
        if len(title) > 255 or len(url) > 255:
             return jsonify({'message': 'Title and URL cannot exceed 255 characters'}), 400
        # Add more validation as needed (e.g., check for valid URL format)

        # --- Handle File Upload (if applicable) ---
        # if file:
        #     if file.filename == '':
        #          return jsonify({'message': 'No selected file'}), 400
        #     if not allowed_file(file.filename): #function to check if file extension is allowed
        #          return jsonify({'message': 'Invalid file type'}), 400
        #     filename = secure_filename(file.filename) #make it secure
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #saving file
        #     # url = f"/uploads/{filename}"  # Construct URL to access the file

        # --- Save to Database ---
        new_video = Video(title=title, url=url) #, filename=filename if uploading locally)
        db.session.add(new_video)
        try:
            db.session.commit()
            return jsonify({'message': 'Video added successfully'}), 201  # 201 Created
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Database error: ' + str(e)}), 500

    elif request.method == 'GET':
        search_query = request.args.get('search', '')
        if search_query:
            videos = Video.query.filter(Video.title.ilike(f'%{search_query}%')).all() #case-insensitive search
        else:
            videos = Video.query.all()

        video_list = [{'id': v.id, 'title': v.title, 'url': v.url} for v in videos]
        return jsonify(video_list)
@app.route('/')
def index():
  return render_template('index.html')

# def allowed_file(filename): #check allowed file extensions
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov', 'mkv'}


if __name__ == '__main__':
    with app.app_context(): #creates app context
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True, port=5001)  # Run the app in debug mode, specify different port
