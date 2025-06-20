// Sample job data
const sampleJobs = [
    {
        id: 1,
        title: "Farm Worker",
        company: "Mang Juan's Rice Farm",
        location: "Barangay San Isidro, Cabanatuan, Nueva Ecija",
        category: "Agriculture",
        province: "Nueva Ecija",
        description: "Looking for hardworking individuals to help with rice planting and harvesting. Experience preferred but not required.",
        salary: "₱300-400/day",
        posted: "2 days ago"
    },
    {
        id: 2,
        title: "Resort Staff",
        company: "Bohol Beach Resort",
        location: "Barangay Tawala, Panglao, Bohol",
        category: "Tourism",
        province: "Bohol",
        description: "Front desk, housekeeping, and maintenance positions available. Good English communication skills required.",
        salary: "₱15,000-18,000/month",
        posted: "1 week ago"
    },
    {
        id: 3,
        title: "Barangay Health Worker",
        company: "Barangay San Miguel LGU",
        location: "Barangay San Miguel, Tuguegarao, Cagayan",
        category: "Government",
        province: "Cagayan",
        description: "Community health worker position. Must be a resident of the barangay. Basic health training will be provided.",
        salary: "₱12,000/month",
        posted: "3 days ago"
    },
    {
        id: 4,
        title: "Sewing Machine Operator",
        company: "Ilocos Textile Cooperative",
        location: "Barangay Poblacion, Vigan, Ilocos Sur",
        category: "Manufacturing",
        province: "Ilocos Sur",
        description: "Experience with industrial sewing machines required. Full-time position with benefits.",
        salary: "₱16,000-20,000/month",
        posted: "5 days ago"
    },
    {
        id: 5,
        title: "Elementary Teacher",
        company: "Leyte Elementary School",
        location: "Barangay Mahayag, Tacloban, Leyte",
        category: "Education",
        province: "Leyte",
        description: "Licensed teacher needed for Grade 3. Must be willing to relocate to rural area.",
        salary: "₱22,000/month",
        posted: "1 day ago"
    },
    {
        id: 6,
        title: "Fish Pond Caretaker",
        company: "Davao Aquaculture Farm",
        location: "Barangay Crossing Bayabas, Toril, Davao del Sur",
        category: "Agriculture",
        province: "Davao del Sur",
        description: "Responsible for feeding fish, maintaining pond cleanliness, and monitoring water quality. Housing provided.",
        salary: "₱13,000/month + housing",
        posted: "6 days ago"
    }
];

let currentJobs = [...sampleJobs];
let isLoggedIn = false;
let userType = null; // 'jobseeker' or 'employer'
let currentUser = null;

// User storage (in a real app, this would be a database)
let users = JSON.parse(localStorage.getItem('trabaho_users') || '[]');
let currentSession = JSON.parse(localStorage.getItem('trabaho_session') || 'null');

// Utility functions
function hashPassword(password) {
    // Simple hash function for demo (in real app, use proper encryption)
    let hash = 0;
    for (let i = 0; i < password.length; i++) {
        const char = password.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString();
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function validatePhoneNumber(phone) {
    const phoneRegex = /^[0-9]{11}$/;
    return phoneRegex.test(phone);
}

function generateUserId() {
    return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function saveUsers() {
    localStorage.setItem('trabaho_users', JSON.stringify(users));
}

function saveSession(user) {
    const session = {
        userId: user.id,
        email: user.email,
        userType: user.userType,
        loginTime: Date.now()
    };
    localStorage.setItem('trabaho_session', JSON.stringify(session));
    currentSession = session;
}

function clearSession() {
    localStorage.removeItem('trabaho_session');
    currentSession = null;
}

// Navigation functions
function showLogin() {
    hideAllForms();
    document.getElementById('authModal').style.display = 'block';
    document.getElementById('loginForm').style.display = 'block';
}

function showRegister() {
    hideAllForms();
    document.getElementById('authModal').style.display = 'block';
    document.getElementById('jobSeekerForm').style.display = 'block';
}

function showJobSeekerForm() {
    hideAllForms();
    document.getElementById('jobSeekerForm').style.display = 'block';
}

function showEmployerForm() {
    hideAllForms();
    document.getElementById('employerForm').style.display = 'block';
}

function showForgotPassword() {
    hideAllForms();
    document.getElementById('forgotPasswordForm').style.display = 'block';
}

function hideAllForms() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('jobSeekerForm').style.display = 'none';
    document.getElementById('employerForm').style.display = 'none';
    document.getElementById('forgotPasswordForm').style.display = 'none';
}

function closeModal() {
    document.getElementById('authModal').style.display = 'none';
}

// Job search and filtering
function searchJobs() {
    const location = document.getElementById('locationSearch').value.toLowerCase();

    if (location.trim() === '') {
        // Show all jobs if no search term
        currentJobs = [...sampleJobs];
    } else {
        // Filter jobs by location
        currentJobs = sampleJobs.filter(job => 
            job.location.toLowerCase().includes(location) ||
            job.province.toLowerCase().includes(location)
        );
    }

    displayJobs();
    document.getElementById('jobs').style.display = 'block';
    document.getElementById('jobs').scrollIntoView({ behavior: 'smooth' });
}

function applyFilters() {
    const provinceFilter = document.getElementById('provinceFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;

    currentJobs = sampleJobs.filter(job => {
        const matchesProvince = !provinceFilter || job.province === provinceFilter;
        const matchesCategory = !categoryFilter || job.category === categoryFilter;
        return matchesProvince && matchesCategory;
    });

    displayJobs();
}

function displayJobs() {
    const jobListings = document.getElementById('jobListings');

    if (currentJobs.length === 0) {
        jobListings.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
                <h3>No jobs found</h3>
                <p>Try adjusting your search criteria or check back later for new opportunities.</p>
            </div>
        `;
        return;
    }

    jobListings.innerHTML = currentJobs.map(job => `
        <div class="job-card fade-in">
            <div class="job-title">${job.title}</div>
            <div class="job-company">${job.company}</div>
            <div class="job-location"><i class="fas fa-map-marker-alt"></i> ${job.location}</div>
            <div class="job-description">${job.description}</div>
            <div class="job-salary"><i class="fas fa-money-bill-wave"></i> ${job.salary}</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                <small style="color: #666;">Posted ${job.posted}</small>
                <button class="btn btn-primary" onclick="applyToJob(${job.id})">Apply Now</button>
            </div>
        </div>
    `).join('');
}

function applyToJob(jobId) {
    if (!isLoggedIn) {
        alert('Please log in to apply for jobs.');
        showLogin();
        return;
    }

    if (userType !== 'jobseeker') {
        alert('Only job seekers can apply for positions. Please register as a job seeker to apply.');
        return;
    }

    const job = sampleJobs.find(j => j.id === jobId);

    // Store application (in real app, this would go to a database)
    const application = {
        id: 'app_' + Date.now(),
        jobId: jobId,
        jobTitle: job.title,
        company: job.company,
        applicantId: currentUser.id,
        applicantName: currentUser.fullName,
        applicantEmail: currentUser.email,
        applicantPhone: currentUser.mobile,
        applicationDate: new Date().toISOString(),
        status: 'pending'
    };

    // Add to user's applications
    if (!currentUser.applications) {
        currentUser.applications = [];
    }
    currentUser.applications.push(application);
    saveUsers();

    alert(`Application submitted successfully!\n\nJob: ${job.title}\nCompany: ${job.company}\n\nThe employer will contact you at ${currentUser.email} or ${currentUser.mobile} if you're selected for an interview.\n\nYou can track your applications in your dashboard.`);
}

// Form handlers
function registerJobSeeker(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    // Get form data
    const userData = {
        fullName: formData.get('fullName').trim(),
        email: formData.get('email').trim().toLowerCase(),
        password: formData.get('password'),
        confirmPassword: formData.get('confirmPassword'),
        mobile: formData.get('mobile').trim(),
        province: formData.get('province'),
        municipality: formData.get('municipality').trim(),
        barangay: formData.get('barangay').trim(),
        skills: formData.get('skills').trim(),
        smsAlerts: formData.get('smsAlerts') === 'on',
        terms: formData.get('terms') === 'on'
    };

    // Validation
    if (!validateEmail(userData.email)) {
        alert('Please enter a valid email address.');
        return;
    }

    if (!validatePassword(userData.password)) {
        alert('Password must be at least 6 characters long.');
        return;
    }

    if (userData.password !== userData.confirmPassword) {
        alert('Passwords do not match.');
        return;
    }

    if (!validatePhoneNumber(userData.mobile)) {
        alert('Please enter a valid 11-digit mobile number.');
        return;
    }

    if (!userData.terms) {
        alert('You must agree to the Terms of Service and Privacy Policy.');
        return;
    }

    // Check if email already exists
    if (users.find(user => user.email === userData.email)) {
        alert('An account with this email already exists. Please use a different email or login.');
        return;
    }

    // Create new user
    const newUser = {
        id: generateUserId(),
        fullName: userData.fullName,
        email: userData.email,
        password: hashPassword(userData.password), // In real app, use proper encryption
        mobile: userData.mobile,
        province: userData.province,
        municipality: userData.municipality,
        barangay: userData.barangay,
        skills: userData.skills,
        smsAlerts: userData.smsAlerts,
        userType: 'jobseeker',
        registrationDate: new Date().toISOString(),
        lastLogin: null,
        profileComplete: true
    };

    // Save user
    users.push(newUser);
    saveUsers();

    // Auto-login the new user
    currentUser = newUser;
    isLoggedIn = true;
    userType = 'jobseeker';
    saveSession(newUser);
    updateNavigation();

    alert(`Registration successful! Welcome to TrabahoPH, ${userData.fullName}. You will receive SMS notifications for new jobs in your area.`);

    // Redirect to main page after successful registration
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
}

function registerEmployer(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    // Get form data
    const userData = {
        businessName: formData.get('businessName').trim(),
        contactPerson: formData.get('contactPerson').trim(),
        email: formData.get('email').trim().toLowerCase(),
        password: formData.get('password'),
        confirmPassword: formData.get('confirmPassword'),
        contactNumber: formData.get('contactNumber').trim(),
        businessType: formData.get('businessType'),
        province: formData.get('province').trim(),
        municipality: formData.get('municipality').trim(),
        barangay: formData.get('barangay').trim(),
        businessDescription: formData.get('businessDescription').trim(),
        terms: formData.get('terms') === 'on'
    };

    // Validation
    if (!validateEmail(userData.email)) {
        alert('Please enter a valid email address.');
        return;
    }

    if (!validatePassword(userData.password)) {
        alert('Password must be at least 6 characters long.');
        return;
    }

    if (userData.password !== userData.confirmPassword) {
        alert('Passwords do not match.');
        return;
    }

    if (!validatePhoneNumber(userData.contactNumber)) {
        alert('Please enter a valid 11-digit contact number.');
        return;
    }

    if (!userData.terms) {
        alert('You must agree to the Terms of Service and Privacy Policy.');
        return;
    }

    // Check if email already exists
    if (users.find(user => user.email === userData.email)) {
        alert('An account with this email already exists. Please use a different email or login.');
        return;
    }

    // Create new employer
    const newUser = {
        id: generateUserId(),
        businessName: userData.businessName,
        contactPerson: userData.contactPerson,
        email: userData.email,
        password: hashPassword(userData.password),
        contactNumber: userData.contactNumber,
        businessType: userData.businessType,
        province: userData.province,
        municipality: userData.municipality,
        barangay: userData.barangay,
        businessDescription: userData.businessDescription,
        userType: 'employer',
        registrationDate: new Date().toISOString(),
        lastLogin: null,
        profileComplete: true,
        jobsPosted: []
    };

    // Save user
    users.push(newUser);
    saveUsers();

    // Auto-login the new user
    currentUser = newUser;
    isLoggedIn = true;
    userType = 'employer';
    saveSession(newUser);
    updateNavigation();

    alert(`Employer registration successful! Welcome to TrabahoPH, ${userData.businessName}. You can now post job opportunities for your local community.`);

    // Redirect to main page after successful registration
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
}

function login(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    const email = formData.get('email').trim().toLowerCase();
    const password = formData.get('password');
    const rememberMe = formData.get('rememberMe') === 'on';

    // Validation
    if (!validateEmail(email)) {
        alert('Please enter a valid email address.');
        return;
    }

    if (!password) {
        alert('Please enter your password.');
        return;
    }

    // Find user
    const user = users.find(u => u.email === email);

    if (!user) {
        alert('No account found with this email address. Please check your email or register for a new account.');
        return;
    }

    // Check password
    if (user.password !== hashPassword(password)) {
        alert('Incorrect password. Please try again.');
        return;
    }

    // Update last login
    user.lastLogin = new Date().toISOString();
    saveUsers();

    // Login user
    currentUser = user;
    isLoggedIn = true;
    userType = user.userType;
    saveSession(user);
    updateNavigation();

    const welcomeName = user.userType === 'employer' ? user.businessName : user.fullName;
    alert(`Login successful! Welcome back to TrabahoPH, ${welcomeName}.`);

    // Redirect to main page after successful login
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
}

function resetPassword(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    const email = formData.get('email').trim().toLowerCase();

    if (!validateEmail(email)) {
        alert('Please enter a valid email address.');
        return;
    }

    // Check if user exists
    const user = users.find(u => u.email === email);

    if (!user) {
        alert('No account found with this email address.');
        return;
    }

    // In a real app, you would send an email here
    alert(`Password reset instructions have been sent to ${email}. Please check your email inbox and spam folder.`);
    showLogin();
}

function updateNavigation() {
    const navButtons = document.querySelector('.nav-buttons');

    if (isLoggedIn && currentUser) {
        const userName = currentUser.userType === 'employer' ? currentUser.businessName : currentUser.fullName;
        const firstName = userName.split(' ')[0];

        navButtons.innerHTML = `
            <span style="color: white; margin-right: 10px;">Hello, ${firstName}!</span>
            <button class="btn btn-secondary" onclick="showDashboard()">Dashboard</button>
            <button class="btn btn-secondary" onclick="logout()">Logout</button>
        `;
    } else {
        // Check if we're on the auth page or main page
        if (window.location.pathname.includes('auth.html')) {
            navButtons.innerHTML = `
                <a href="index.html" class="btn btn-secondary">Back to Home</a>
            `;
        } else {
            navButtons.innerHTML = `
                <a href="auth.html" class="btn btn-secondary">Login</a>
                <a href="auth.html" class="btn btn-primary">Sign Up</a>
            `;
        }
    }
}

function showDashboard() {
    if (userType === 'employer') {
        alert(`Employer Dashboard for ${currentUser.businessName}:\n\n• Post new job listings\n• View and manage applications\n• Edit business profile\n• View analytics\n\nFeature coming soon!`);
    } else {
        alert(`Job Seeker Dashboard for ${currentUser.fullName}:\n\n• View your job applications\n• Update your profile and skills\n• Manage job alert preferences\n• Download certificates\n\nFeature coming soon!`);
    }
}

function logout() {
    isLoggedIn = false;
    userType = null;
    currentUser = null;
    clearSession();
    updateNavigation();
    alert('You have been logged out successfully. Thank you for using TrabahoPH!');
}

// Check for existing session on page load
function checkExistingSession() {
    if (currentSession) {
        // Check if session is still valid (less than 7 days old)
        const sessionAge = Date.now() - currentSession.loginTime;
        const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds

        if (sessionAge < maxAge) {
            // Find user and restore session
            const user = users.find(u => u.id === currentSession.userId);
            if (user) {
                currentUser = user;
                isLoggedIn = true;
                userType = user.userType;
                updateNavigation();
                return true;
            }
        } else {
            // Session expired, clear it
            clearSession();
        }
    }
    return false;
}

// SMS notification simulation
function sendSMSNotification(phoneNumber, message) {
    // In a real application, this would integrate with an SMS service
    console.log(`SMS to ${phoneNumber}: ${message}`);
}

// Simulate new job postings
function simulateNewJobPosting() {
    const newJob = {
        id: sampleJobs.length + 1,
        title: "Store Cashier",
        company: "Sari-Sari Store ni Aling Maria",
        location: "Barangay Poblacion, San Fernando, Pampanga",
        category: "Retail",
        province: "Pampanga",
        description: "Part-time cashier needed for busy sari-sari store. Basic math skills required.",
        salary: "₱200/day",
        posted: "Just now"
    };

    sampleJobs.unshift(newJob);
    currentJobs = [...sampleJobs];

    if (document.getElementById('jobs').style.display !== 'none') {
        displayJobs();
    }

    // Simulate SMS notification to subscribed users
    if (isLoggedIn && userType === 'jobseeker') {
        setTimeout(() => {
            alert('📱 SMS Alert: New job posted in your area! Store Cashier at Sari-Sari Store ni Aling Maria in Pampanga. Apply now on TrabahoPH!');
        }, 2000);
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Check for existing session
    checkExistingSession();

    // Display some jobs by default
    currentJobs = sampleJobs.slice(0, 3);

    // Close modal when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('authModal');
        if (event.target === modal) {
            closeModal();
        }
    };

    // Simulate a new job posting after 10 seconds
    setTimeout(simulateNewJobPosting, 10000);

    // Add smooth scrolling for navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add real-time form validation
    addFormValidation();
});

// Add real-time form validation
function addFormValidation() {
    // Email validation
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !validateEmail(this.value)) {
                this.style.borderColor = '#ff6b6b';
                this.title = 'Please enter a valid email address';
            } else {
                this.style.borderColor = '';
                this.title = '';
            }
        });
    });

    // Password confirmation validation
    document.querySelectorAll('input[name="confirmPassword"]').forEach(input => {
        input.addEventListener('input', function() {
            const passwordField = this.form.querySelector('input[name="password"]');
            if (passwordField && this.value !== passwordField.value) {
                this.style.borderColor = '#ff6b6b';
                this.title = 'Passwords do not match';
            } else {
                this.style.borderColor = '';
                this.title = '';
            }
        });
    });

    // Phone number validation
    document.querySelectorAll('input[type="tel"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !validatePhoneNumber(this.value)) {
                this.style.borderColor = '#ff6b6b';
                this.title = 'Please enter a valid 11-digit phone number';
            } else {
                this.style.borderColor = '';
                this.title = '';
            }
        });
    });

    // Only initialize location dropdowns if we're on the auth page
    if (document.getElementById('provinceSearch')) {
        // Initialize searchable province dropdown
        initializeSearchableProvince();

        // Initialize municipality and barangay dropdowns
        initializeMunicipalityDropdown();
        initializeBarangayDropdown();
    }
}

// Philippine location data (sample data - in production, this would come from a comprehensive database)
const philippineLocations = {
    "Metro Manila": {
        "Manila": ["Binondo", "Ermita", "Intramuros", "Malate", "Paco", "Pandacan", "Port Area", "Quiapo", "Sampaloc", "San Andres", "San Miguel", "San Nicolas", "Santa Ana", "Santa Cruz", "Santa Mesa", "Tondo"],
        "Quezon City": ["Bagong Pag-asa", "Batasan Hills", "Commonwealth", "Diliman", "Fairview", "Kamuning", "Libis", "New Manila", "Novaliches", "Project 6", "Teachers Village", "Timog"],
        "Makati": ["Bel-Air", "Forbes Park", "Greenbelt", "Legazpi Village", "Poblacion", "Rockwell", "Salcedo Village", "San Lorenzo", "Urdaneta"],
        "Pasig": ["Bagong Ilog", "Kapitolyo", "Malinao", "Oranbo", "Pinagbuhatan", "Rosario", "Sagad", "San Antonio", "San Joaquin", "Santolan"],
        "Taguig": ["Bagumbayan", "Bambang", "Calzada", "Central Bicutan", "Fort Bonifacio", "Hagonoy", "Ibayo-Tipas", "Ligid-Tipas", "Lower Bicutan", "New Lower Bicutan", "Napindan", "Palingon", "Pinagsama", "San Miguel", "Santa Ana", "Tuktukan", "Ususan", "Wawa"]
    },
    "Cebu": {
        "Cebu City": ["Apas", "Banilad", "Basak San Nicolas", "Busay", "Calamba", "Capitol Site", "Carreta", "Centro", "Cogon Ramos", "Duljo Fatima", "Guadalupe", "IT Park", "Lahug", "Mabolo", "Pardo", "Poblacion", "Talamban", "Tejero"],
        "Lapu-Lapu": ["Agus", "Babag", "Bankal", "Basak", "Buaya", "Calawisan", "Canjulao", "Caubian", "Gun-ob", "Ibo", "Looc", "Mactan", "Marigondon", "Pajac", "Pajo", "Poblacion", "Punta Engaño", "Pusok", "Suba-basbas", "Subabasbas", "Talima", "Tingub", "Tuyom"],
        "Mandaue": ["Alang-alang", "Bakilid", "Banilad", "Basak", "Cabancalan", "Cambaro", "Canduman", "Centro", "Cubacub", "Guizo", "Ibabao-Estancia", "Jagobiao", "Labogon", "Looc", "Maguikay", "Mantuyong", "Opao", "Pagsabungan", "Paknaan", "Subangdaku", "Tabok", "Tingub", "Tipolo", "Umapad"]
    },
    "Davao del Sur": {
        "Davao City": ["Agdao", "Baguio", "Buhangin", "Bunawan", "Calinan", "Marilog", "Paquibato", "Poblacion", "Talomo", "Toril", "Tugbok"],
        "Digos": ["Aplaya", "Balabag", "Colorado", "Cogon", "Danlugan", "Goma", "Igpit", "Kapatagan", "Kiagot", "Lungag", "Mahayag", "Palkan", "Poblacion", "Ruparan", "San Jose", "San Miguel", "Sinawilan", "Soong", "Tiguman", "Tres de Mayo", "Zone I", "Zone II", "Zone III"],
        "Hagonoy": ["Aplaya", "Balutakay", "Clib", "Guihing", "Hagonoy Crossing", "Kapatagan", "La Union", "Leling", "Mabuhay", "Makiling", "Malabog", "Paligue", "Palili", "Poblacion", "San Guillermo", "San Isidro", "San Pablo", "Sinayawan", "Tologan"]
    },
    "Nueva Ecija": {
        "Cabanatuan": ["Aduas Norte", "Aduas Sur", "Bagong Buhay", "Bakero", "Barrera", "Camp Tinio", "Caudillo", "H. Concepcion", "Kadayawan", "Kalikid Norte", "Kalikid Sur", "Kapitan Pepe", "Mabini Homesite", "Maharlika", "Magsaysay Norte", "Magsaysay Sur", "Mayapyap Norte", "Mayapyap Sur", "MS Oro", "Polilio", "Prospero", "Rosario", "San Isidro", "San Juan", "San Roque", "Santa Arcadia", "Santa Rita", "Sapang Palay", "Talledo", "Zulueta"],
        "Gapan": ["Bayanihan", "Bungo", "Callos", "Kapalangan", "Mangino", "Pambuan", "Poblacion", "San Lorenzo", "San Nicolas", "San Vicente", "Santo Cristo", "Santo Niño"],
        "San Jose": ["Abar 1st", "Abar 2nd", "Bagong Sikat", "Calizon", "Camanacsacan", "Culiat", "Kaliwanagan", "Kita-kita", "Lawang Kupang", "Malasin", "Malayantoc", "Minuyan 1st", "Minuyan 2nd", "Palestina", "Poblacion Norte", "Poblacion Sur", "San Agustin", "San Mauricio", "Santa Teresita", "Sibut", "Tabulac", "Villa Joson"]
    },
    "Bohol": {
        "Tagbilaran": ["Bool", "Booy", "Cabawan", "Cogon", "Dao", "Dampas", "Mansasa", "Poblacion I", "Poblacion II", "Poblacion III", "San Isidro", "Taloto", "Tiptip", "Ubujan"],
        "Panglao": ["Bil-isan", "Bolod", "Danao", "Doljo", "Lourdes", "Looc", "Poblacion", "Tangnan", "Tawala"],
        "Loboc": ["Alegria", "Bagacay", "Bonbon", "Calvario", "Camayaan", "Candabong", "Candasig", "Gasa", "Jimilian", "Lourdes", "Napo", "Poblacion", "Santo Niño", "Taytay", "Tejero", "Ugpong", "Valladolid"]
    },
    "Ilocos Norte": {
        "Laoag": ["Balatong", "Balacad", "Bengcag", "Buttong", "Camangaan", "Cavit", "Darayday", "Dibua Norte", "Dibua Sur", "Gabu Norte", "Gabu Sur", "Nangalisan", "Poblacion", "San Lorenzo", "Santa Angela", "Salet", "Suyo", "Tangid", "Vira", "Zamboanga"],
        "Batac": ["Ablan Sarat", "Aglipay", "Baay", "Baligat", "Ben-agan", "Billoca", "Binacag", "Biningan", "Caba", "Callaguip", "Capacuan", "Caunayan", "Dariwdiw", "Lacub", "Magnuang", "Maipalig", "Nalupta", "Naguirangan", "Pamulapula", "Poblacion", "Quiling Norte", "Quiling Sur", "Rayuray", "Ricarte", "San Mateo", "Sumader", "Tabayag", "Valdez", "Windus"],
        "Vigan": ["Ayusan Norte", "Ayusan Sur", "Barangay I", "Barangay II", "Barangay III", "Barangay IV", "Barangay V", "Barangay VI", "Barangay VII", "Barangay VIII", "Barangay IX", "Bulala", "Cabalangegan", "Camangaan", "Capangpangan", "Nagsangalan", "Paoa", "Poblacion", "Purok-a-bassit", "Purok-a-dackel", "Raois", "Rugsunan", "Salindeg", "San Jose", "San Julian Norte", "San Julian Sur", "Tamag"]
    }
};

// Initialize searchable province dropdown
function initializeSearchableProvince() {
    const provinceInput = document.getElementById('provinceSearch');
    const provinceOptions = document.getElementById('provinceOptions');

    if (!provinceInput || !provinceOptions) return;

    const options = provinceOptions.querySelectorAll('.option');
    let selectedIndex = -1;

    // Show dropdown when input is focused
    provinceInput.addEventListener('focus', function() {
        provinceOptions.style.display = 'block';
        filterOptions('');
    });

    // Filter options as user types
    provinceInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        filterOptions(searchTerm);
        selectedIndex = -1;
        updateSelection();
    });

    // Handle keyboard navigation
    provinceInput.addEventListener('keydown', function(e) {
        const visibleOptions = Array.from(options).filter(option => !option.classList.contains('hidden'));

        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, visibleOptions.length - 1);
                updateSelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateSelection();
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && visibleOptions[selectedIndex]) {
                    selectOption(visibleOptions[selectedIndex]);
                }
                break;
            case 'Escape':
                provinceOptions.style.display = 'none';
                selectedIndex = -1;
                updateSelection();
                break;
        }
    });

    // Handle option clicks
    options.forEach(option => {
        option.addEventListener('click', function() {
            selectOption(this);
        });
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!provinceInput.contains(e.target) && !provinceOptions.contains(e.target)) {
            provinceOptions.style.display = 'none';
            selectedIndex = -1;
            updateSelection();
        }
    });

    function filterOptions(searchTerm) {
        options.forEach(option => {
            const optionText = option.textContent.toLowerCase();
            if (optionText.includes(searchTerm)) {
                option.classList.remove('hidden');
            } else {
                option.classList.add('hidden');
            }
        });
    }

    function updateSelection() {
        options.forEach(option => option.classList.remove('selected'));
        const visibleOptions = Array.from(options).filter(option => !option.classList.contains('hidden'));
        if (selectedIndex >= 0 && visibleOptions[selectedIndex]) {
            visibleOptions[selectedIndex].classList.add('selected');
        }
    }

    function selectOption(option) {
        provinceInput.value = option.getAttribute('data-value');
        provinceOptions.style.display = 'none';
        selectedIndex = -1;
        updateSelection();

        // Enable and populate municipality dropdown
        populateMunicipalities(option.getAttribute('data-value'));

        // Trigger change event for form validation
        const changeEvent = new Event('change', { bubbles: true });
        provinceInput.dispatchEvent(changeEvent);
    }
}

// Populate municipalities based on selected province
function populateMunicipalities(province) {
    const municipalityInput = document.getElementById('municipalitySearch');
    const municipalityOptions = document.getElementById('municipalityOptions');
    const barangayInput = document.getElementById('barangaySearch');
    const barangayOptions = document.getElementById('barangayOptions');

    if (!municipalityInput || !municipalityOptions) return;

    // Clear previous selections
    municipalityInput.value = '';
    if (barangayInput) {
        barangayInput.value = '';
        barangayInput.disabled = true;
    }
    if (barangayOptions) {
        barangayOptions.innerHTML = '';
        barangayOptions.style.display = 'none';
    }

    // Get municipalities for the selected province
    const municipalities = philippineLocations[province] || {};
    const municipalityNames = Object.keys(municipalities);

    if (municipalityNames.length > 0) {
        // Enable municipality dropdown
        municipalityInput.disabled = false;

        // Populate municipality options
        municipalityOptions.innerHTML = municipalityNames.map(municipality => 
            `<div class="option" data-value="${municipality}">${municipality}</div>`
        ).join('');

        // Add click handlers to new options
        municipalityOptions.querySelectorAll('.option').forEach(option => {
            option.addEventListener('click', function() {
                selectMunicipality(this);
            });
        });
    } else {
        // Disable if no municipalities found
        municipalityInput.disabled = true;
        municipalityOptions.innerHTML = '<div class="option">No municipalities available</div>';
    }
}

// Populate barangays based on selected municipality
function populateBarangays(province, municipality) {
    const barangayInput = document.getElementById('barangaySearch');
    const barangayOptions = document.getElementById('barangayOptions');

    if (!barangayInput || !barangayOptions) return;

    // Clear previous selection
    barangayInput.value = '';
    barangayOptions.style.display = 'none';

    // Get barangays for the selected municipality
    const barangays = philippineLocations[province]?.[municipality] || [];

    if (barangays.length > 0) {
        // Enable barangay dropdown
        barangayInput.disabled = false;

        // Populate barangay options
        barangayOptions.innerHTML = barangays.map(barangay => 
            `<div class="option" data-value="${barangay}">${barangay}</div>`
        ).join('');

        // Add click handlers to new options
        barangayOptions.querySelectorAll('.option').forEach(option => {
            option.addEventListener('click', function() {
                selectBarangay(this);
            });
        });
    } else {
        // Disable if no barangays found
        barangayInput.disabled = true;
        barangayOptions.innerHTML = '<div class="option">No barangays available</div>';
    }
}

// Initialize municipality dropdown
function initializeMunicipalityDropdown() {
    const municipalityInput = document.getElementById('municipalitySearch');
    const municipalityOptions = document.getElementById('municipalityOptions');

    if (!municipalityInput || !municipalityOptions) return;

    let selectedIndex = -1;

    // Show dropdown when input is focused
    municipalityInput.addEventListener('focus', function() {
        if (!this.disabled && municipalityOptions.children.length > 0) {
            municipalityOptions.style.display = 'block';
            filterMunicipalityOptions('');
        }
    });

    // Filter options as user types
    municipalityInput.addEventListener('input', function() {
        if (!this.disabled) {
            const searchTerm = this.value.toLowerCase();
            filterMunicipalityOptions(searchTerm);
            selectedIndex = -1;
            updateMunicipalitySelection();
            if (municipalityOptions.children.length > 0) {
                municipalityOptions.style.display = 'block';
            }
        }
    });

    // Handle keyboard navigation
    municipalityInput.addEventListener('keydown', function(e) {
        if (this.disabled) return;
        
        const visibleOptions = Array.from(municipalityOptions.querySelectorAll('.option:not(.hidden)'));

        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, visibleOptions.length - 1);
                updateMunicipalitySelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateMunicipalitySelection();
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && visibleOptions[selectedIndex]) {
                    selectMunicipality(visibleOptions[selectedIndex]);
                }
                break;
            case 'Escape':
                municipalityOptions.style.display = 'none';
                selectedIndex = -1;
                updateMunicipalitySelection();
                break;
        }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!municipalityInput.contains(e.target) && !municipalityOptions.contains(e.target)) {
            municipalityOptions.style.display = 'none';
            selectedIndex = -1;
            updateMunicipalitySelection();
        }
    });

    function filterMunicipalityOptions(searchTerm) {
        municipalityOptions.querySelectorAll('.option').forEach(option => {
            const optionText = option.textContent.toLowerCase();
            if (optionText.includes(searchTerm)) {
                option.classList.remove('hidden');
            } else {
                option.classList.add('hidden');
            }
        });
    }

    function updateMunicipalitySelection() {
        municipalityOptions.querySelectorAll('.option').forEach(option => option.classList.remove('selected'));
        const visibleOptions = Array.from(municipalityOptions.querySelectorAll('.option:not(.hidden)'));
        if (selectedIndex >= 0 && visibleOptions[selectedIndex]) {
            visibleOptions[selectedIndex].classList.add('selected');
        }
    }
}

// Initialize barangay dropdown
function initializeBarangayDropdown() {
    const barangayInput = document.getElementById('barangaySearch');
    const barangayOptions = document.getElementById('barangayOptions');

    if (!barangayInput || !barangayOptions) return;

    let selectedIndex = -1;

    // Show dropdown when input is focused
    barangayInput.addEventListener('focus', function() {
        if (!this.disabled && barangayOptions.children.length > 0) {
            barangayOptions.style.display = 'block';
            filterBarangayOptions('');
        }
    });

    // Filter options as user types
    barangayInput.addEventListener('input', function() {
        if (!this.disabled) {
            const searchTerm = this.value.toLowerCase();
            filterBarangayOptions(searchTerm);
            selectedIndex = -1;
            updateBarangaySelection();
            if (barangayOptions.children.length > 0) {
                barangayOptions.style.display = 'block';
            }
        }
    });

    // Handle keyboard navigation
    barangayInput.addEventListener('keydown', function(e) {
        if (this.disabled) return;
        
        const visibleOptions = Array.from(barangayOptions.querySelectorAll('.option:not(.hidden)'));

        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, visibleOptions.length - 1);
                updateBarangaySelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateBarangaySelection();
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && visibleOptions[selectedIndex]) {
                    selectBarangay(visibleOptions[selectedIndex]);
                }
                break;
            case 'Escape':
                barangayOptions.style.display = 'none';
                selectedIndex = -1;
                updateBarangaySelection();
                break;
        }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!barangayInput.contains(e.target) && !barangayOptions.contains(e.target)) {
            barangayOptions.style.display = 'none';
            selectedIndex = -1;
            updateBarangaySelection();
        }
    });

    function filterBarangayOptions(searchTerm) {
        barangayOptions.querySelectorAll('.option').forEach(option => {
            const optionText = option.textContent.toLowerCase();
            if (optionText.includes(searchTerm)) {
                option.classList.remove('hidden');
            } else {
                option.classList.add('hidden');
            }
        });
    }

    function updateBarangaySelection() {
        barangayOptions.querySelectorAll('.option').forEach(option => option.classList.remove('selected'));
        const visibleOptions = Array.from(barangayOptions.querySelectorAll('.option:not(.hidden)'));
        if (selectedIndex >= 0 && visibleOptions[selectedIndex]) {
            visibleOptions[selectedIndex].classList.add('selected');
        }
    }
}

// Select municipality and populate barangays
function selectMunicipality(option) {
    const municipalityInput = document.getElementById('municipalitySearch');
    const municipalityOptions = document.getElementById('municipalityOptions');
    const provinceInput = document.getElementById('provinceSearch');

    municipalityInput.value = option.getAttribute('data-value');
    municipalityOptions.style.display = 'none';

    // Populate barangays for the selected municipality
    const selectedProvince = provinceInput.value;
    const selectedMunicipality = option.getAttribute('data-value');
    populateBarangays(selectedProvince, selectedMunicipality);

    // Trigger change event for form validation
    const changeEvent = new Event('change', { bubbles: true });
    municipalityInput.dispatchEvent(changeEvent);
}

// Select barangay
function selectBarangay(option) {
    const barangayInput = document.getElementById('barangaySearch');
    const barangayOptions = document.getElementById('barangayOptions');

    barangayInput.value = option.getAttribute('data-value');
    barangayOptions.style.display = 'none';

    // Trigger change event for form validation
    const changeEvent = new Event('change', { bubbles: true });
    barangayInput.dispatchEvent(changeEvent);
}

// Resume Guide Download Function
function downloadResumeGuide() {
    // Create resume guide content
    const resumeGuideContent = `
TRABAHO PH - RESUME WRITING GUIDE
=================================

A Complete Guide to Writing an Effective Resume for Filipino Job Seekers

TABLE OF CONTENTS
1. Introduction
2. Resume Structure
3. Contact Information
4. Professional Summary
5. Work Experience
6. Education
7. Skills Section
8. Additional Sections
9. Formatting Tips
10. Common Mistakes to Avoid
11. Sample Resume Template

1. INTRODUCTION
===============
Your resume is your first impression with potential employers. In the Filipino job market, especially in rural areas, a well-written resume can set you apart from other candidates.

2. RESUME STRUCTURE
==================
A good resume should be:
- 1-2 pages maximum
- Easy to read
- Well-organized
- Free of grammatical errors

3. CONTACT INFORMATION
=====================
Include:
- Full Name
- Mobile Number
- Email Address
- Complete Address (Barangay, Municipality, Province)
- LinkedIn profile (if available)

Example:
Juan Santos Dela Cruz
Mobile: 0917-123-4567
Email: juan.delacruz@email.com
Address: Brgy. San Isidro, Cabanatuan City, Nueva Ecija

4. PROFESSIONAL SUMMARY
=======================
Write 2-3 sentences about yourself:
- Your profession/field
- Years of experience
- Key strengths

Example:
"Dedicated farm worker with 3 years of experience in rice cultivation and livestock care. Proven ability to work independently and as part of a team. Committed to sustainable farming practices and continuous learning."

5. WORK EXPERIENCE
==================
List jobs in reverse chronological order:
- Job Title
- Company Name
- Location
- Employment Dates
- 2-4 bullet points describing responsibilities and achievements

Example:
Farm Worker
Mang Pedro's Rice Farm
Brgy. Malabanan, Cabanatuan City
June 2021 - Present
• Assisted in planting, cultivating, and harvesting rice crops
• Maintained farm equipment and irrigation systems
• Increased crop yield by 15% through improved planting techniques
• Trained 2 new farm workers on proper harvesting methods

6. EDUCATION
============
Include:
- Degree/Certificate
- School Name
- Location
- Graduation Year
- Relevant coursework or honors (if applicable)

Example:
High School Diploma
Cabanatuan National High School
Cabanatuan City, Nueva Ecija
Graduated: March 2020

7. SKILLS SECTION
=================
List relevant skills:
- Technical skills
- Language skills
- Computer skills
- Soft skills

Example:
• Rice farming and crop rotation
• Basic computer skills (MS Word, Excel)
• Fluent in Filipino and English
• Excellent communication skills
• Team leadership

8. ADDITIONAL SECTIONS
=====================
Consider adding:
- Certifications
- Volunteer Work
- Awards and Recognition
- Training Programs

9. FORMATTING TIPS
==================
- Use a clean, professional font (Arial, Calibri)
- Keep font size between 10-12 points
- Use bullet points for easy reading
- Maintain consistent formatting
- Leave white space for readability
- Save as PDF to preserve formatting

10. COMMON MISTAKES TO AVOID
============================
- Spelling and grammar errors
- Using unprofessional email addresses
- Including personal information (age, marital status, religion)
- Making it too long
- Using fancy fonts or colors
- Including irrelevant information

11. SAMPLE RESUME TEMPLATE
==========================

[Your Full Name]
[Your Address]
[Your Phone Number]
[Your Email]

PROFESSIONAL SUMMARY
[2-3 sentences about your background and goals]

WORK EXPERIENCE
[Most Recent Job Title]
[Company Name], [Location]
[Start Date] - [End Date]
• [Achievement or responsibility]
• [Achievement or responsibility]
• [Achievement or responsibility]

[Previous Job Title]
[Company Name], [Location]
[Start Date] - [End Date]
• [Achievement or responsibility]
• [Achievement or responsibility]

EDUCATION
[Degree/Certificate]
[School Name], [Location]
[Graduation Date]

SKILLS
• [Skill 1]
• [Skill 2]
• [Skill 3]
• [Skill 4]

CERTIFICATIONS
• [Certification 1]
• [Certification 2]

---

Remember: Your resume should tell your story and highlight why you're the best candidate for the job. Tailor it for each position you apply for.

For more career resources and job opportunities, visit TrabahoPH.com

Good luck with your job search!
    `;

    // Create blob and download
    const blob = new Blob([resumeGuideContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'TrabahoPH_Resume_Writing_Guide.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    // Show success message
    alert('Resume Writing Guide downloaded successfully! Check your Downloads folder.');
}

// Interview Tips YouTube Function
function openInterviewTips() {
    // Open YouTube search for interview tips
    const youtubeSearchUrl = 'https://www.youtube.com/results?search_query=interview+tips+job+preparation';
    window.open(youtubeSearchUrl, '_blank');
}

// TESDA Courses Function
function openTESDAcourses() {
    // Open e-TESDA courses website
    const tesdaCoursesUrl = 'https://e-tesda.gov.ph/course/';
    window.open(tesdaCoursesUrl, '_blank');
}

// Digital Literacy Function
function openDigitalLiteracy() {
    // Open YouTube search for digital literacy courses
    const digitalLiteracyUrl = 'https://www.youtube.com/results?search_query=digital+literacy+computer+basics+tutorial';
    window.open(digitalLiteracyUrl, '_blank');
}

// Additional utility functions for future enhancements
function formatLocation(location) {
    // Helper function to format location strings consistently
    return location.split(',').map(part => part.trim()).join(', ');
}

function calculateDistance(userLocation, jobLocation) {
    // Placeholder for distance calculation
    // In a real app, this would use geolocation APIs
    return Math.floor(Math.random() * 50) + 1; // Random distance for demo
}

function sendJobAlert(job, recipients) {
    // Function to send job alerts to matching users
    recipients.forEach(recipient => {
        const message = `New job: ${job.title} at ${job.company} in ${job.location}. Salary: ${job.salary}. Apply on TrabahoPH!`;
        sendSMSNotification(recipient.phone, message);
    });
}

// Feature for Barangay officials to post community work
function postCommunityWork(workDetails) {
    const communityJob = {
        id: sampleJobs.length + 1,
        title: workDetails.title,
        company: `Barangay ${workDetails.barangay}`,
        location: workDetails.location,
        category: "Government",
        province: workDetails.province,
        description: workDetails.description,
        salary: workDetails.compensation || "Community service",
        posted: "Just now"
    };

    sampleJobs.unshift(communityJob);
    currentJobs = [...sampleJobs];

    alert('Community work program posted successfully! Local residents will be notified via SMS.');
}