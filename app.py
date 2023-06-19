from flask import Flask,render_template,url_for,request,g,redirect,session,flash
from database import connect_to_database, getDatabase
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask import Flask,render_template,Response
import cv2
import numpy as np
import dlib
from math import hypot


app=Flask(__name__)

camera = cv2.VideoCapture(0)

app.config['SECRET_KEY'] = os.urandom(24)
#student
@app.teardown_appcontext
def close_database(error):
    if hasattr(g,'logreg'):
        g.logreg.close()

app.config['UPLOAD_FOLDER']="static\images"


def get_current_user():
    user_result=None
    if 'user' in session:
        
        user = session['user']
        db = getDatabase()
        user_cursor = db.execute("select * from stureg where name = ?" , [user])
        user_result = user_cursor.fetchone()
    return user_result

@app.route('/')
def index():
    user = get_current_user()
    return render_template('home.html',user = user)

#@app.route('/studentinterface')
#def studentinterface():
  #  user = get_current_user()
   # return render_template('studentinterface.html',user = user)


@app.route('/studentinterface', methods = ["POST","GET"])
def studentinterface():
    #usertea = get_current_usertea()
    db = getDatabase()
    user_cursor = db.execute("select * from examdetails")
    allexamdetails = user_cursor.fetchall()
    user = get_current_user()
    stuname = user['name']
    user_cursorscore = db.execute("select * from score where stuname = ?" , [stuname])
    markscored = user_cursorscore.fetchall()
    return render_template('studentinterface.html', user = user , allexamdetails = allexamdetails,markscored = markscored)



@app.route('/stulogin' ,methods = ["POST","GET"])
def stulogin():
    user = get_current_user()
    error = None
    if request.method == 'POST':
        db = getDatabase()

        username = request.form['username']
        password  = request.form['password']

       
        fetchedperson_cursor = db.execute("select * from stureg where username = ?",[username])
        personfromdatabase = fetchedperson_cursor.fetchone()

        if personfromdatabase:
            if check_password_hash(personfromdatabase['password'],password):
                session['user'] = personfromdatabase['name']
                return redirect(url_for('studentinterface'))
            else:
                error = "Username or password did not match. Try again."
                #return render_template('stulogin.html', error = error)

        else:
            error = "Username or password did not match. Try again."
            #return redirect(url_for('stulogin'))
        
    return render_template('stulogin.html', user = user, error=error)


@app.route('/sturegister', methods=["POST","GET"]) 
def sturegister():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = getDatabase()
        name= request.form['name']
        cgpa= request.form['cgpa']
        dob= request.form['dob']
        college= request.form['college']
        email= request.form['email']
        username= request.form['username']
        phone  = request.form['phone']
        password  = request.form['password']
        qualification  = request.form['qualification']

        conpassword  = request.form['conpassword']

        upload_image=request.files['upload_image']

        if upload_image.filename!='':
            filepath=os.path.join(app.config['UPLOAD_FOLDER'],upload_image.filename)
            upload_image.save(filepath)
            
            #curr=db.execute("insert into stureg(img)values(?)",(upload_image.filename,))
            #db.commit()

        user_fetcing_cursor = db.execute("select * from stureg where username=?",[username])
        existing_user = user_fetcing_cursor.fetchone()

        if existing_user:
            error = "Username already taken ,please choose a different username"
            return render_template("sturegister.html", error = error)
        hashed_password = generate_password_hash(password, method='sha256')

        db.execute('insert into stureg(name, dob, email,phone,qualification,cgpa,college,username,password,conpassword,img) values(?,?,?,?,?,?,?,?,?,?,?)',[name,dob,email,phone,qualification,cgpa,college,username, hashed_password,conpassword,upload_image.filename])
        db.commit()
        session['user']=name
        return redirect(url_for('studentinterface'))
    return render_template('sturegister.html')

#@app.route('/testwindow')
#def testwindow():
 #   user = get_current_user()
  #  return render_template('testwindow.html',user = user)

#teacher


def get_current_usertea():
    user_resulttea = None
    if 'usertea' in session:
        usertea = session['usertea']
        dbtea = getDatabase()
        user_cursortea = dbtea.execute("select * from teareg where name = ?" , [usertea])
        user_resulttea = user_cursortea.fetchone()
    return user_resulttea

@app.route('/teacherinterface', methods = ["POST","GET"])
def teacherinterface():
    #usertea = get_current_usertea()
    dbtea = getDatabase()
    user_cursor = dbtea.execute("select * from stureg")
    allusers = user_cursor.fetchall()
    usertea = get_current_usertea()   
    user_cursorscore = dbtea.execute("select * from score")
    markscored = user_cursorscore.fetchall()
    return render_template('teacherinterface.html', usertea = usertea , allusers = allusers,markscored= markscored)



@app.route('/tealogin' ,methods = ["POST","GET"])
def tealogin():
    usertea = get_current_usertea()
    error = None
    if request.method == 'POST':
        dbtea = getDatabase()

        teacheridtea = request.form['teacherid']
        passwordtea  = request.form['password']

       
        fetchedperson_cursortea = dbtea.execute("select * from teareg where teacherid = ?",[teacheridtea])
        personfromdatabasetea = fetchedperson_cursortea.fetchone()

        if personfromdatabasetea:
            if check_password_hash(personfromdatabasetea['password'],passwordtea):
                session['usertea'] = personfromdatabasetea['name']
                return redirect(url_for('teacherinterface'))
            else:
                error = "Username or password did not match. Try again."
                #return render_template('stulogin.html', error = error)

        else:
            error = "Username or password did not match. Try again."
            #return redirect(url_for('stulogin'))
        
    return render_template('tealogin.html', usertea = usertea, error=error)

@app.route('/tearegister', methods=["POST","GET"]) 
def tearegister():
    usertea = get_current_usertea()
    error = None
    if request.method == "POST":
        dbtea = getDatabase()
        nametea= request.form['name']
        posttea= request.form['post']
        dobtea= request.form['dob']
        teacheridtea= request.form['teacherid']
        emailtea= request.form['email']
        
        phonetea  = request.form['phone']
        passwordtea  = request.form['password']
        qualificationtea  = request.form['qualification']

        conpasswordtea  = request.form['conpassword']

        upload_image=request.files['upload_image']

        if upload_image.filename!='':
            filepath=os.path.join(app.config['UPLOAD_FOLDER'],upload_image.filename)
            upload_image.save(filepath)
            
            #curr=db.execute("insert into stureg(img)values(?)",(upload_image.filename,))
            #db.commit()

   
        user_fetcing_cursortea = dbtea.execute("select * from teareg where teacherid=?",[teacheridtea])
        existing_usertea = user_fetcing_cursortea.fetchone()

        if existing_usertea:
            error = "Username already taken ,please choose a different username"
            return render_template("tearegister.html", error = error)
        hashed_passwordtea = generate_password_hash(passwordtea, method='sha256')

        dbtea.execute('insert into teareg(name, dob, email,phone,qualification,post,teacherid,password,conpassword,img) values(?,?,?,?,?,?,?,?,?,?)',[nametea,dobtea,emailtea,phonetea,qualificationtea,posttea,teacheridtea, hashed_passwordtea,conpasswordtea,upload_image.filename])
        dbtea.commit()
        session['usertea']=nametea
        return redirect(url_for('teacherinterface'))
    return render_template('tearegister.html')

#@app.route('/createexam')
#def createexam():
    #usertea = get_current_usertea()
    #return render_template('createexam.html',usertea = usertea)



#createexam form


@app.route('/createexamform', methods=["POST","GET"]) 
def createexamform():
    usertea = get_current_usertea()
    error = None
    if request.method == "POST":
        dbtea = getDatabase()
        examname= request.form['examname']
        noofque= request.form['noofque']
        totalmarks= request.form['totalmarks']
        duration= request.form['duration']
        user_fetcing_cursortea = dbtea.execute("select * from examdetails where examname=?",[examname])
        existing_usertea = user_fetcing_cursortea.fetchone()

        if existing_usertea:
            error = "Exam name must be unique, Please choose a different exam name"
            return render_template("createexam.html", error = error)

        dbtea.execute('insert into examdetails(examname, noofque, totalmarks, duration) values(?,?,?,?)',[examname,noofque,totalmarks,duration])
        dbtea.commit()
        
        return redirect(url_for('teacherinterface'))
    return render_template('createexam.html',usertea = usertea)

#adding question to the database
@app.route('/addqueform', methods=["POST","GET"]) 
def addqueform():
    usertea = get_current_usertea()
    
    if request.method == "POST":
        dbtea = getDatabase()
        examname= request.form['examname']
        question= request.form['question']
        option1= request.form['option1']
        option2= request.form['option2']
        option3= request.form['option3']
        option4= request.form['option4']
        correctoption= request.form['correctoption']
        

        dbtea.execute('insert into questions(examname, question, option1, option2, option3, option4, correctoption) values(?,?,?,?,?,?,?)',[examname,question,option1,option2,option3,option4,correctoption])
        dbtea.commit()
        
        return redirect(url_for('teacherinterface'))
    return render_template('addqueform.html',usertea = usertea)

# for add question table
@app.route('/addquestion', methods = ["POST","GET"])
def addquestion():
    #usertea = get_current_usertea()
    dbtea = getDatabase()
    user_cursor = dbtea.execute("select * from examdetails")
    allexamdetails = user_cursor.fetchall()
    usertea = get_current_usertea()
    return render_template('addquestion.html', usertea = usertea , allexamdetails = allexamdetails)


#view exam details
@app.route('/viewexamdetails', methods = ["POST","GET"])
def viewexamdetails():
    #usertea = get_current_usertea()
    dbtea = getDatabase()
    user_cursor = dbtea.execute("select * from examdetails")
    allexamdetails = user_cursor.fetchall()
    usertea = get_current_usertea()
    return render_template('viewexamdetails.html', usertea = usertea , allexamdetails = allexamdetails)





#view questions
@app.route('/viewquestions/<examname>', methods = ["POST","GET"])
def viewquestions(examname):
    #usertea = get_current_usertea()
    dbtea = getDatabase()
    user_cursor = dbtea.execute("select * from questions where examname =?" ,[examname] )
    allquestions = user_cursor.fetchall()
    usertea = get_current_usertea()
    return render_template('viewquestions.html', usertea = usertea , allquestions = allquestions)


#testwindow
@app.route('/testwindow/<examname>',methods =["POST","GET"])
def testwindow(examname):
   
       dbtea = getDatabase()
    
       user_cursorex = dbtea.execute("select * from examdetails  where examname =?" , [examname])
       examdetail = user_cursorex.fetchone()

      
       #user = get_current_user()
       return render_template('testwindow.html',examdetail = examdetail)

#start test
@app.route('/starttest/<nameofex>',methods =["POST","GET"])
def starttest(nameofex):   
       #db = getDatabase()
       #user_cursor = db.execute("select quenumber,question,option1,option2,option3,option4,correctoption from questions  where examname =?" , [nameofex])
       #allquestion = user_cursor.fetchall()
       #user = get_current_user()
       #print("hello")
       #return render_template('starttest.html',allquestion= allquestion)
       
       dbtea = getDatabase()
       user_cursor = dbtea.execute("select * from questions where examname = ?",[nameofex])
       allquestion = user_cursor.fetchall()

       user_cursorex = dbtea.execute("select * from examdetails  where examname =?" , [nameofex])
       examdetail = user_cursorex.fetchone()

       usertea = get_current_usertea()
       return render_template('starttest.html', usertea=usertea, allquestion = allquestion,examdetail=examdetail)

@app.route('/prescore/<nameofex>',methods =["POST","GET"])
def prescore(nameofex):
       
       
       if camera.isOpened():
           camera.release()
       


       option =''
       dbtea = getDatabase()
       user_cursorcount = dbtea.execute("select * from questions where examname = ?",[nameofex])
       count = len(user_cursorcount.fetchall())

       user_cursorque = dbtea.execute("select question,correctoption from questions where examname = ?",[nameofex])
       allque = user_cursorque.fetchall()

       user_cursorop = dbtea.execute("select correctoption from questions where examname = ?",[nameofex])
       crtop = user_cursorop.fetchall()
       correct_count =0
       for que in allque:
           
           option = "option"+que[0]
           selected_option = request.form.get(option)
           if  selected_option == que[1]:
                   #print(que[1])
                   #print(selected_option)
                   correct_count = int(correct_count)+1
                   #print(correct_count)
       user = get_current_user() 
       stuname=(user['name'])
       markscored=str(correct_count)+'/'+str(count)
       dbtea.execute('insert into score(stuname ,examname , markscored) values(?,?,?)',[stuname,nameofex,markscored])
       dbtea.commit()                
       return render_template('prescore.html',correct_count = correct_count)


#video streaming
def generate_frames(camera,detector,count):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    def midpoint(p1 ,p2):
         return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)
    
    def get_blinking_ratio(eye_points, facial_landmarks):
        left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
        right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
        center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
        center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

        #hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
        #ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

    

        hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
        ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

        ratio = hor_line_lenght / ver_line_lenght
        return ratio
    
    def get_gaze_ratio(eye_points, facial_landmarks):
        left_eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
                                (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
                                (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
                                (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
                                (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
                                (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)
        # cv2.polylines(frame, [left_eye_region], True, (0, 0, 255), 2)

        height, width, _ = frame.shape
        mask = np.zeros((height, width), np.uint8)
        cv2.polylines(mask, [left_eye_region], True, 255, 2)
        cv2.fillPoly(mask, [left_eye_region], 255)
        eye = cv2.bitwise_and(gray, gray, mask=mask)
        min_x = np.min(left_eye_region[:, 0])
        max_x = np.max(left_eye_region[:, 0])
        min_y = np.min(left_eye_region[:, 1])
        max_y = np.max(left_eye_region[:, 1])

        gray_eye = eye[min_y: max_y, min_x: max_x]
        _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
        height, width = threshold_eye.shape
        left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
        left_side_white = cv2.countNonZero(left_side_threshold)
        right_side_threshold = threshold_eye[0: height, int(width / 2): width]
        right_side_white = cv2.countNonZero(right_side_threshold)

        if left_side_white == 0:
            gaze_ratio = 1
        elif right_side_white == 0:
            gaze_ratio = 5
        else:
            gaze_ratio = left_side_white / right_side_white
        return gaze_ratio



    #read cam frame
    while True:
       
        success,frame = camera.read()
        if not success:
            break
        else:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)
                
                if len(faces) ==0:
                     #if count>100:
                         #cv2.putText(frame, "count exceeded ", (50, 50), font, 1, (0, 0, 255), 2,cv2.LINE_4)
                     #else:
                         #count=count+1
                     font = cv2.FONT_HERSHEY_DUPLEX
                     cv2.putText(frame, "your face is not detected", (50, 50), font, 1, (0, 0, 255), 2,cv2.LINE_4)
                     
                i = 0
                for face in faces:
                    x, y = face.left(), face.top()
                    x1, y1 = face.right(), face.bottom()
                    i = i+1
                    if i>1:
                       #if count>100:
                           #cv2.putText(frame, "count exceeded ", (50, 50), font, 1, (0, 0, 255), 2,cv2.LINE_4)
                       #else:
                           #count=count+1
                       font = cv2.FONT_HERSHEY_DUPLEX
                       cv2.putText(frame, "multiple faces  detected", (50, 50), font, 1, (0, 0, 255), 2,cv2.LINE_4)
                
                
                for face in faces:
                    #x, y = face.left(), face.top()
                    #x1, y1 = face.right(), face.bottom()
                    #cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)

                    landmarks = predictor(gray, face)

                    # Detect blinking
                    left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
                    right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
                    blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2
                    if blinking_ratio > 5.7:
                        cv2.putText(frame, "BLINKING", (50, 150), font, 3, (255, 0, 0))

                    #gaze detection

                    gaze_ratio_left_eye = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks)
                    gaze_ratio_right_eye = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks)
                    gaze_ratio = (gaze_ratio_right_eye + gaze_ratio_left_eye) / 2

                    if gaze_ratio <= 0.3:
                        #if count>100:
                           #cv2.putText(frame, "count exceeded ", (50, 50), font, 1, (0, 0, 255), 2,cv2.LINE_4)
                        #else:
                           #count=count+1
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(frame, "You are not looking at screen", (50, 50), font, 1, (0, 0, 255), 2,cv2.LINE_4)
                     
                    elif gaze_ratio > 6: 
                        #if count>100:
                           #cv2.putText(frame, "count exceeded ", (50, 50), font, 1, (0, 0, 255), 2,cv2.LINE_4)

                        #else:
                           #count=count+1         
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(frame, "You are not looking at screen ", (50, 50), font, 1, (0, 0, 255), 2,cv2.LINE_4)
                     
                    #else:
                        #cv2.putText(frame, "CENTER", (50, 100), font, 2, (0, 0, 255), 3) #center




                ret,buffer = cv2.imencode('.jpg',frame)
                frame = buffer.tobytes()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n'+ frame +b'\r\n')
        
@app.route('/video')
def video():
    camera = cv2.VideoCapture(0)
    # Detect the coordinates
    detector = dlib.get_frontal_face_detector()
    count=0
    return Response(generate_frames(camera,detector,count),mimetype='multipart/x-mixed-replace; boundary=frame')   
       







if __name__ =="__main__":
    app.run(debug=True)