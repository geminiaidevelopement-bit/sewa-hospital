import sqlite3
import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "sewa_hospital_secret_key_beed"

# Database initialization
def init_db():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            doctor TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Shared Header HTML component
HEADER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>सेवा हॉस्पिटल - Sewa Hospital, Beed</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Poppins', sans-serif; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col justify-between">

    <!-- Top Emergency Bar -->
    <div class="bg-red-600 text-white text-xs sm:text-sm py-2 px-4 shadow-md">
        <div class="max-w-7xl mx-mx-auto flex justify-between items-center px-2 sm:px-6">
            <span class="font-medium"><i class="fas fa-ambulance mr-2 animate-pulse"></i> 24/7 Emergency Services Available in Beed</span>
            <span class="font-bold"><i class="fas fa-phone-alt mr-1"></i> Contact: Coming Soon</span>
        </div>
    </div>

    <!-- Main Navigation -->
    <nav class="bg-white shadow-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-20 items-center">
                <div class="flex items-center space-x-3">
                    <div class="bg-emerald-600 text-white p-3 rounded-lg shadow">
                        <i class="fas fa-hospital-user text-2xl"></i>
                    </div>
                    <div>
                        <a href="/" class="text-2xl font-bold text-slate-800 tracking-wide">सेवा हॉस्पिटल</a>
                        <p class="text-xs text-emerald-600 font-semibold tracking-wider uppercase">Sewa Hospital • Beed</p>
                    </div>
                </div>
                <div class="hidden md:flex items-center space-x-8 font-medium text-slate-600">
                    <a href="/" class="hover:text-emerald-600 transition">Home</a>
                    <a href="/doctors" class="hover:text-emerald-600 transition">Doctors</a>
                    <a href="/services" class="hover:text-emerald-600 transition">Services</a>
                    <a href="/book" class="bg-emerald-600 text-white px-5 py-2.5 rounded-full hover:bg-emerald-700 transition shadow-md">Book Appointment</a>
                </div>
            </div>
        </div>
    </nav>
"""

# Shared Footer HTML component
FOOTER_HTML = """
    <!-- Footer -->
    <footer class="bg-slate-900 text-slate-300 mt-16 border-t-4 border-emerald-600">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                    <h3 class="text-xl font-bold text-white mb-4">सेवा हॉस्पिटल (Sewa Hospital)</h3>
                    <p class="text-sm text-slate-400 leading-relaxed mb-4">
                        Providing compassionate, world-class orthopedic and healthcare services to the people of Beed and surrounding regions.
                    </p>
                </div>
                <div>
                    <h4 class="text-lg font-semibold text-white mb-4">Hospital Address</h4>
                    <p class="text-sm text-slate-400 leading-relaxed">
                        <i class="fas fa-map-marker-alt text-emerald-500 mr-2"></i> In front of Natyagraha,<br>
                        Gholave Hospital Road, Beed,<br>
                        Maharashtra - 431122, India
                    </p>
                </div>
                <div>
                    <h4 class="text-lg font-semibold text-white mb-4">Quick Links</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="/" class="hover:text-emerald-400 transition"><i class="fas fa-angle-right mr-2 text-emerald-500"></i>Home</a></li>
                        <li><a href="/doctors" class="hover:text-emerald-400 transition"><i class="fas fa-angle-right mr-2 text-emerald-500"></i>Doctors & Specialists</a></li>
                        <li><a href="/book" class="hover:text-emerald-400 transition"><i class="fas fa-angle-right mr-2 text-emerald-500"></i>Online Booking</a></li>
                        <li><a href="/admin" class="hover:text-emerald-400 transition"><i class="fas fa-angle-right mr-2 text-emerald-500"></i>Admin Portal</a></li>
                    </ul>
                </div>
            </div>

            <div class="border-t border-slate-800 mt-10 pt-6 flex flex-col sm:flex-row justify-between items-center text-xs text-slate-500">
                <p>&copy; 2026 सेवा हॉस्पिटल. All Rights Reserved.</p>
                <p class="mt-2 sm:mt-0 font-medium text-slate-400">
                    Developed by <span class="text-emerald-400 font-bold">Aditya Tidke</span>
                </p>
            </div>
        </div>
    </footer>
</body>
</html>
"""

# Home Page Route
@app.route('/')
def home():
    content = """
    <!-- Hero Banner -->
    <div class="bg-gradient-to-r from-emerald-800 via-emerald-700 to-teal-800 text-white py-20 px-4">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between">
            <div class="md:w-1/2 mb-10 md:mb-0 space-y-6">
                <span class="bg-emerald-500/30 text-emerald-200 px-4 py-1 rounded-full text-sm font-semibold tracking-wide uppercase border border-emerald-400/30">Excellence in Orthopedics</span>
                <h1 class="text-4xl md:text-5xl font-extrabold leading-tight">Expert Healthcare & Specialized Orthopedic Care in Beed</h1>
                <p class="text-slate-200 text-lg">Leading orthopedic treatments, trauma surgery, and comprehensive medical care delivered with dedication and compassion.</p>
                <div class="pt-4 flex flex-wrap gap-4">
                    <a href="/book" class="bg-white text-emerald-800 font-bold px-8 py-3.5 rounded-lg shadow-lg hover:bg-slate-100 transition">Book Online Appointment</a>
                    <a href="/doctors" class="bg-emerald-900/60 text-white font-semibold px-6 py-3.5 rounded-lg border border-emerald-400/30 hover:bg-emerald-900 transition">View Doctor Profile</a>
                </div>
            </div>
            <div class="md:w-5/12 bg-white/10 backdrop-blur-md p-8 rounded-2xl border border-white/20 shadow-2xl">
                <h3 class="text-2xl font-bold mb-4 border-b border-emerald-400/30 pb-2">Primary Doctor</h3>
                <div class="flex items-center space-x-4 mb-4">
                    <div class="bg-emerald-500 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold shadow">
                        <i class="fas fa-user-md"></i>
                    </div>
                    <div>
                        <h4 class="text-xl font-bold text-white">Dr. Siddheshwar S. Andhale</h4>
                        <p class="text-emerald-300 font-medium">MBBS, MS Orthopedics</p>
                        <p class="text-xs text-slate-300 mt-1">Consultant Orthopedic Surgeon</p>
                    </div>
                </div>
                <div class="space-y-2 text-sm text-slate-200 bg-black/20 p-4 rounded-xl">
                    <p><i class="fas fa-bone text-emerald-400 mr-2"></i> Specialization: Joint Replacement, Bone Fracture & Trauma Surgery</p>
                    <p><i class="fas fa-clock text-emerald-400 mr-2"></i> OPD Timings: Coming Soon</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Info Cards -->
    <div class="max-w-7xl mx-auto px-4 -mt-10 grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
        <div class="bg-white p-6 rounded-xl shadow-lg border border-slate-100 flex items-start space-x-4">
            <div class="bg-emerald-100 text-emerald-600 p-3 rounded-lg"><i class="fas fa-map-marked-alt text-2xl"></i></div>
            <div>
                <h4 class="font-bold text-slate-800 text-lg">Hospital Location</h4>
                <p class="text-sm text-slate-600 mt-1">In front of Natyagraha, Gholave Hospital Road, Beed - 431122</p>
            </div>
        </div>
        <div class="bg-white p-6 rounded-xl shadow-lg border border-slate-100 flex items-start space-x-4">
            <div class="bg-emerald-100 text-emerald-600 p-3 rounded-lg"><i class="fas fa-calendar-check text-2xl"></i></div>
            <div>
                <h4 class="font-bold text-slate-800 text-lg">Online Booking</h4>
                <p class="text-sm text-slate-600 mt-1">Schedule your OPD slot effortlessly from home anytime.</p>
            </div>
        </div>
        <div class="bg-white p-6 rounded-xl shadow-lg border border-slate-100 flex items-start space-x-4">
            <div class="bg-emerald-100 text-emerald-600 p-3 rounded-lg"><i class="fas fa-phone-volume text-2xl"></i></div>
            <div>
                <h4 class="font-bold text-slate-800 text-lg">Emergency Helpline</h4>
                <p class="text-sm text-slate-600 mt-1">Direct Contact: <span class="font-semibold text-slate-800">Coming Soon</span></p>
            </div>
        </div>
    </div>
    """
    return HEADER_HTML + content + FOOTER_HTML

# Doctor Profile Route
@app.route('/doctors')
def doctors():
    content = """
    <div class="max-w-7xl mx-auto px-4 py-12">
        <div class="text-center mb-12">
            <h2 class="text-3xl font-bold text-slate-800">Our Medical Specialists</h2>
            <p class="text-slate-600 mt-2">Dedicated doctors committed to your recovery and health</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <!-- Doctor Card 1 -->
            <div class="bg-white rounded-2xl shadow-md overflow-hidden border border-slate-100 hover:shadow-xl transition">
                <div class="bg-gradient-to-r from-emerald-600 to-teal-600 h-28 flex items-center justify-center">
                    <i class="fas fa-user-md text-6xl text-white/80"></i>
                </div>
                <div class="p-6">
                    <span class="bg-emerald-100 text-emerald-700 text-xs font-bold px-3 py-1 rounded-full uppercase">Primary Specialist</span>
                    <h3 class="text-2xl font-bold text-slate-800 mt-3">Dr. Siddheshwar S. Andhale</h3>
                    <p class="text-emerald-600 font-semibold text-sm">MBBS, MS Orthopedics</p>
                    <p class="text-slate-500 text-sm mt-2">Specialist in Joint Replacements, Complex Fracture Management, Arthroscopy, and Pediatric Orthopedics.</p>

                    <div class="mt-6 border-t border-slate-100 pt-4 text-xs text-slate-500 space-y-1">
                        <p><strong>OPD Schedule:</strong> Coming Soon</p>
                        <p><strong>Experience:</strong> Senior Orthopedic Consultant</p>
                    </div>

                    <a href="/book" class="mt-6 block text-center bg-emerald-600 text-white font-medium py-2.5 rounded-lg hover:bg-emerald-700 transition">Book Consultation</a>
                </div>
            </div>

            <!-- Coming Soon Doctor Placeholder -->
            <div class="bg-slate-50 rounded-2xl border-2 border-dashed border-slate-300 p-8 flex flex-col items-center justify-center text-center min-h-[350px]">
                <div class="w-16 h-16 bg-slate-200 text-slate-400 rounded-full flex items-center justify-center text-2xl mb-4">
                    <i class="fas fa-plus"></i>
                </div>
                <h4 class="text-xl font-bold text-slate-700">More Specialists Joining Soon</h4>
                <p class="text-sm text-slate-500 mt-2">We are expanding our panel of visiting consultants and specialists across departments.</p>
                <span class="mt-4 inline-block bg-slate-200 text-slate-600 text-xs font-bold px-4 py-1.5 rounded-full">Coming Soon</span>
            </div>
        </div>
    </div>
    """
    return HEADER_HTML + content + FOOTER_HTML

# Hospital Services Route
@app.route('/services')
def services():
    content = """
    <div class="max-w-7xl mx-auto px-4 py-12">
        <div class="text-center mb-12">
            <h2 class="text-3xl font-bold text-slate-800">Hospital Departments & Services</h2>
            <p class="text-slate-600 mt-2">State-of-the-art facilities for complete patient care in Beed</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white p-6 rounded-xl shadow border border-slate-100">
                <div class="text-emerald-600 text-3xl mb-3"><i class="fas fa-bone"></i></div>
                <h3 class="text-xl font-bold text-slate-800">Orthopedic Surgery</h3>
                <p class="text-slate-600 text-sm mt-2">Expert care for bone fractures, joint replacements, ligament repairs, and spine conditions.</p>
            </div>
            <div class="bg-white p-6 rounded-xl shadow border border-slate-100">
                <div class="text-emerald-600 text-3xl mb-3"><i class="fas fa-x-ray"></i></div>
                <h3 class="text-xl font-bold text-slate-800">X-Ray & Diagnostics</h3>
                <p class="text-slate-600 text-sm mt-2">Advanced digital imaging and fast diagnostic reporting.</p>
                <span class="mt-3 inline-block text-xs bg-amber-100 text-amber-700 font-semibold px-2.5 py-0.5 rounded">Details Coming Soon</span>
            </div>
            <div class="bg-white p-6 rounded-xl shadow border border-slate-100">
                <div class="text-emerald-600 text-3xl mb-3"><i class="fas fa-procedures"></i></div>
                <h3 class="text-xl font-bold text-slate-800">Emergency & Trauma</h3>
                <p class="text-slate-600 text-sm mt-2">24/7 casualty wing ready to handle accident and trauma cases.</p>
            </div>
            <div class="bg-white p-6 rounded-xl shadow border border-slate-100">
                <div class="text-emerald-600 text-3xl mb-3"><i class="fas fa-vials"></i></div>
                <h3 class="text-xl font-bold text-slate-800">Pathology Laboratory</h3>
                <p class="text-slate-600 text-sm mt-2">Comprehensive routine blood tests and specialized lab diagnostics.</p>
                <span class="mt-3 inline-block text-xs bg-amber-100 text-amber-700 font-semibold px-2.5 py-0.5 rounded">Details Coming Soon</span>
            </div>
            <div class="bg-white p-6 rounded-xl shadow border border-slate-100">
                <div class="text-emerald-600 text-3xl mb-3"><i class="fas fa-pills"></i></div>
                <h3 class="text-xl font-bold text-slate-800">In-house Pharmacy</h3>
                <p class="text-slate-600 text-sm mt-2">Essential medications and surgical supplies available on site.</p>
                <span class="mt-3 inline-block text-xs bg-amber-100 text-amber-700 font-semibold px-2.5 py-0.5 rounded">Details Coming Soon</span>
            </div>
            <div class="bg-white p-6 rounded-xl shadow border border-slate-100">
                <div class="text-emerald-600 text-3xl mb-3"><i class="fas fa-bed"></i></div>
                <h3 class="text-xl font-bold text-slate-800">IPD & ICU Facilities</h3>
                <p class="text-slate-600 text-sm mt-2">Comfortable in-patient rooms and post-operative care units.</p>
                <span class="mt-3 inline-block text-xs bg-amber-100 text-amber-700 font-semibold px-2.5 py-0.5 rounded">Details Coming Soon</span>
            </div>
        </div>
    </div>
    """
    return HEADER_HTML + content + FOOTER_HTML

# Appointment Booking Route
@app.route('/book', methods=['GET', 'POST'])
def book():
    message = ""
    if request.method == 'POST':
        patient_name = request.form.get('patient_name')
        phone = request.form.get('phone')
        department = request.form.get('department')
        doctor = request.form.get('doctor')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')

        if patient_name and phone and appointment_date:
            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO appointments (patient_name, phone, department, doctor, appointment_date, appointment_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_name, phone, department, doctor, appointment_date, appointment_time))
            conn.commit()
            conn.close()
            message = "SUCCESS"
        else:
            message = "ERROR"

    content = f"""
    <div class="max-w-3xl mx-auto px-4 py-12">
        <div class="bg-white p-8 rounded-2xl shadow-xl border border-slate-100">
            <h2 class="text-3xl font-bold text-slate-800 text-center mb-2">Book OPD Appointment</h2>
            <p class="text-slate-500 text-center text-sm mb-8">Fill in your details below to schedule your visit at सेवा हॉस्पिटल</p>

            {'<div class="bg-emerald-100 border border-emerald-400 text-emerald-700 px-4 py-3 rounded-lg mb-6 text-center font-medium"><i class="fas fa-check-circle mr-2"></i>Appointment request submitted successfully! We will contact you for confirmation.</div>' if message == 'SUCCESS' else ''}
            {'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6 text-center font-medium"><i class="fas fa-exclamation-circle mr-2"></i>Please fill in all required fields.</div>' if message == 'ERROR' else ''}

            <form action="/book" method="POST" class="space-y-5">
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Patient Full Name *</label>
                    <input type="text" name="patient_name" required placeholder="e.g. Ramesh Kumar" class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                </div>

                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Phone / Mobile Number *</label>
                    <input type="tel" name="phone" required placeholder="e.g. 9876543210" class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-1">Department</label>
                        <select name="department" class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                            <option value="Orthopedics">Orthopedics</option>
                            <option value="General OPD">General OPD</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-1">Select Doctor</label>
                        <select name="doctor" class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                            <option value="Dr. Siddheshwar S. Andhale">Dr. Siddheshwar S. Andhale (MBBS, MS Orthopedics)</option>
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-1">Preferred Date *</label>
                        <input type="date" name="appointment_date" required class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-1">Preferred Slot</label>
                        <select name="appointment_time" class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                            <option value="Morning (10:00 AM - 01:00 PM)">Morning (10:00 AM - 01:00 PM)</option>
                            <option value="Evening (05:00 PM - 08:00 PM)">Evening (05:00 PM - 08:00 PM)</option>
                        </select>
                    </div>
                </div>

                <button type="submit" class="w-full bg-emerald-600 text-white font-bold py-3.5 rounded-lg hover:bg-emerald-700 transition shadow-lg mt-4">Confirm Appointment Booking</button>
            </form>
        </div>
    </div>
    """
    return HEADER_HTML + content + FOOTER_HTML

# Admin Portal for Staff
@app.route('/admin')
def admin():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, patient_name, phone, department, doctor, appointment_date, appointment_time, created_at FROM appointments ORDER BY id DESC")
    appointments = cursor.fetchall()
    conn.close()

    rows = ""
    for appt in appointments:
        rows += f"""
        <tr class="border-b hover:bg-slate-50">
            <td class="p-3 font-semibold text-slate-700">#{appt[0]}</td>
            <td class="p-3 font-bold text-slate-800">{appt[1]}</td>
            <td class="p-3 text-slate-600">{appt[2]}</td>
            <td class="p-3 text-slate-600">{appt[3]}</td>
            <td class="p-3 text-slate-600">{appt[4]}</td>
            <td class="p-3 text-emerald-700 font-medium">{appt[5]} ({appt[6]})</td>
            <td class="p-3 text-xs text-slate-400">{appt[7]}</td>
        </tr>
        """

    if not appointments:
        rows = '<tr><td colspan="7" class="p-6 text-center text-slate-400">No appointments booked yet.</td></tr>'

    content = f"""
    <div class="max-w-7xl mx-auto px-4 py-12">
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-3xl font-bold text-slate-800">Hospital Admin - Booked Appointments</h2>
            <span class="bg-emerald-100 text-emerald-800 font-semibold px-3 py-1 rounded-full text-sm">Total: {len(appointments)}</span>
        </div>

        <div class="bg-white rounded-xl shadow overflow-hidden border border-slate-200">
            <table class="w-full text-left text-sm">
                <thead class="bg-slate-800 text-white uppercase text-xs">
                    <tr>
                        <th class="p-3">ID</th>
                        <th class="p-3">Patient Name</th>
                        <th class="p-3">Phone</th>
                        <th class="p-3">Department</th>
                        <th class="p-3">Doctor</th>
                        <th class="p-3">Date & Time</th>
                        <th class="p-3">Booked At</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
    """
    return HEADER_HTML + content + FOOTER_HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
