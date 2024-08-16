import os
import random
import openai
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

# Ensure the API key is set from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No API key found in environment variables. Please set the OPENAI_API_KEY environment variable.")
openai.api_key = api_key

# Function to generate workout and diet plans
def generate_plan(name, age, gender, height, weight, waist, lifestyle, diet, dietary_complications, location, plan_duration, food_preference):
    # Hardcoded workout plan with 5-6 exercises per day
    workout_plan = f"""
    <table>
        <tr>
            <th>Day</th>
            <th>Workout Type</th>
            <th>Exercises</th>
            <th>Reps/Sets</th>
        </tr>
        <tr>
            <td>Monday</td>
            <td>Upper Body Strength</td>
            <td>Bench Press, Push-ups, Incline Dumbbell Press, Tricep Dips, Shoulder Press</td>
            <td>4 sets of 8-10 reps</td>
        </tr>
        <tr>
            <td>Tuesday</td>
            <td>Cardio</td>
            <td>Running, Cycling, Jump Rope, Mountain Climbers, Burpees</td>
            <td>30 minutes at moderate intensity</td>
        </tr>
        <tr>
            <td>Wednesday</td>
            <td>Lower Body Strength</td>
            <td>Squats, Lunges, Deadlifts, Leg Press, Calf Raises</td>
            <td>4 sets of 8-10 reps</td>
        </tr>
        <tr>
            <td>Thursday</td>
            <td>Cardio & Flexibility</td>
            <td>Yoga, Stretching, Pilates, Mobility Drills</td>
            <td>30 minutes of cardio + 15 minutes of stretching</td>
        </tr>
        <tr>
            <td>Friday</td>
            <td>Full Body Circuit</td>
            <td>Kettlebell Swings, Medicine Ball Slams, Battle Ropes, Box Jumps, Pull-Ups</td>
            <td>3 rounds, minimal rest between exercises</td>
        </tr>
        <tr>
            <td>Saturday</td>
            <td>Cardio & Core</td>
            <td>Plank, Bicycle Crunches, Russian Twists, Leg Raises, Sit-ups</td>
            <td>30 minutes of cardio + core exercises</td>
        </tr>
        <tr>
            <td>Sunday</td>
            <td>Rest or Light Activity</td>
            <td>Walking, Yoga, Light Jogging, Stretching</td>
            <td>Active recovery recommended</td>
        </tr>
    </table>
    """

    # Rule-based diet plan based on dietary preference
    if diet == "Vegan":
        diet_plan = f"""
        <ul>
            <li><strong>Breakfast:</strong> Smoothie with almond milk, spinach, banana, and chia seeds</li>
            <li><strong>Mid-Morning Snack:</strong> Mixed nuts and seeds</li>
            <li><strong>Lunch:</strong> Quinoa salad with black beans, corn, avocado, and lime dressing</li>
            <li><strong>Afternoon Snack:</strong> Carrot and cucumber sticks with hummus</li>
            <li><strong>Dinner:</strong> Stir-fried tofu with mixed vegetables and brown rice</li>
            <li><strong>Evening Snack:</strong> Apple slices with almond butter</li>
        </ul>
        """
    elif diet == "Vegetarian":
        diet_plan = f"""
        <ul>
            <li><strong>Breakfast:</strong> Greek yogurt with mixed berries and honey</li>
            <li><strong>Mid-Morning Snack:</strong> A handful of almonds and walnuts</li>
            <li><strong>Lunch:</strong> Grilled paneer salad with mixed greens and vinaigrette</li>
            <li><strong>Afternoon Snack:</strong> Cottage cheese with sliced cucumber and tomatoes</li>
            <li><strong>Dinner:</strong> Vegetable curry with brown rice and lentils</li>
            <li><strong>Evening Snack:</strong> A small bowl of mixed fruit</li>
        </ul>
        """
    elif diet == "Non-Vegetarian":
        diet_plan = f"""
        <ul>
            <li><strong>Breakfast:</strong> 3 Egg Omelet with spinach, tomatoes, and onions</li>
            <li><strong>Mid-Morning Snack:</strong> Greek yogurt with a handful of almonds</li>
            <li><strong>Lunch:</strong> Grilled chicken breast (150g) with mixed greens salad and 1 cup of brown rice</li>
            <li><strong>Afternoon Snack:</strong> A protein shake with whey protein, 1 banana, and 1 apple</li>
            <li><strong>Dinner:</strong> Baked salmon (150g) with steamed broccoli and sweet potato (about 150g)</li>
            <li><strong>Evening Snack:</strong> Cottage cheese (1 cup) with cinnamon</li>
        </ul>
        """
    else:
        diet_plan = "Diet plan not available for this dietary preference."

    return workout_plan, diet_plan

# Function to estimate body fat percentage based on descriptive metrics
def process_image(name, height, weight, waist, gender):
    prompt = f"""
    Based on the following physical metrics, provide an estimated body fat percentage range for {name}:
    
    Height: {height} cm
    Weight: {weight} kg
    Waist Size: {waist} cm
    Gender: {gender}

    Please provide only the estimated body fat percentage range. No text, just the range. Just give the numbers and range. No letters.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that estimates body fat percentage based on physical metrics."},
            {"role": "user", "content": prompt}
        ]
    )

    body_fat_percentage = response.choices[0].message['content'].strip()
    return body_fat_percentage

# Function to calculate BMI
def calculate_bmi(weight, height):
    height_in_meters = height / 100  # Convert height to meters
    bmi = weight / (height_in_meters ** 2)
    return round(bmi, 2)

# Function to get top 5 gyms in the user's city using OpenAI API
def get_top_gyms(city):
    prompt = f"""
    Provide a list of the top 5 gyms in {city}. Include the name of each gym and a brief description.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that lists the top gyms in a given city."},
            {"role": "user", "content": prompt}
        ]
    )

    # Parse and format the response
    gyms_info = response.choices[0].message['content'].strip()
    
    # Convert the response into a list (assuming each gym is on a new line)
    gyms = gyms_info.split('\n')
    
    return gyms

# Flask application setup
app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    body_fat_percentage = "No picture uploaded to analyze body fat percentage."
    bmi = None
    workout_plan = "Workout plan information is not available."
    diet_plan = "Diet plan information is not available."
    top_gyms = []

    # Ensure current_city is initialized to avoid UnboundLocalError
    current_city = None

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        waist = request.form['waist']
        lifestyle = request.form['lifestyle']
        diet = request.form['diet']
        dietary_complications = request.form['dietary_complications']
        current_city = request.form['current_city']
        plan_duration = request.form['plan_duration']
        food_preference = request.form['food_preference']

        # Calculate BMI
        bmi = calculate_bmi(weight, height)

        # Image upload handling
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                body_fat_percentage = process_image(name, height, weight, waist, gender)
        else:
            body_fat_percentage = "No image uploaded to calculate body fat percentage."

        # Generate workout and diet plans
        workout_plan, diet_plan = generate_plan(name, age, gender, height, weight, waist, lifestyle, diet, dietary_complications, current_city, plan_duration, food_preference)

        # Get top gyms in the user's city
        if current_city:
            top_gyms = get_top_gyms(current_city)

    return render_template('index.html', 
                            body_fat_percentage=body_fat_percentage, 
                            bmi=bmi, 
                            workout_plan=workout_plan,
                            diet_plan=diet_plan,
                            top_gyms=top_gyms,
                            current_city=current_city)

if __name__ == '__main__':
    app.run(debug=True)

