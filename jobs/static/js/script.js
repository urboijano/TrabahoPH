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
let userType = null;
let currentUser = null;

let users = JSON.parse(localStorage.getItem('trabaho_users') || '[]');
let currentSession = JSON.parse(localStorage.getItem('trabaho_session') || 'null');

function hashPassword(password) {
    let hash = 0;
    for (let i = 0; i < password.length; i++) {
        const char = password.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
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

function searchJobs() {
    const location = document.getElementById('locationSearch').value.toLowerCase();

    if (location.trim() === '') {
        currentJobs = [...sampleJobs];
    } else {
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

    if (!currentUser.applications) {
        currentUser.applications = [];
    }
    currentUser.applications.push(application);
    saveUsers();

    alert(`Application submitted successfully!\n\nJob: ${job.title}\nCompany: ${job.company}\n\nThe employer will contact you at ${currentUser.email} or ${currentUser.mobile} if you're selected for an interview.\n\nYou can track your applications in your dashboard.`);
}

function registerJobSeeker(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

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

    if (users.find(user => user.email === userData.email)) {
        alert('An account with this email already exists. Please use a different email or login.');
        return;
    }

    const newUser = {
        id: generateUserId(),
        fullName: userData.fullName,
        email: userData.email,
        password: hashPassword(userData.password),
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

    users.push(newUser);
    saveUsers();

    currentUser = newUser;
    isLoggedIn = true;
    userType = 'jobseeker';
    saveSession(newUser);
    updateNavigation();

    alert(`Registration successful! Welcome to TrabahoPH, ${userData.fullName}. You will receive SMS notifications for new jobs in your area.`);

    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

function registerEmployer(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

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

    if (users.find(user => user.email === userData.email)) {
        alert('An account with this email already exists. Please use a different email or login.');
        return;
    }

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

    users.push(newUser);
    saveUsers();

    currentUser = newUser;
    isLoggedIn = true;
    userType = 'employer';
    saveSession(newUser);
    updateNavigation();

    alert(`Employer registration successful! Welcome to TrabahoPH, ${userData.businessName}. You can now post job opportunities for your local community.`);

    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

function login(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    const email = formData.get('email').trim().toLowerCase();
    const password = formData.get('password');
    const rememberMe = formData.get('rememberMe') === 'on';

    if (!validateEmail(email)) {
        alert('Please enter a valid email address.');
        return;
    }

    if (!password) {
        alert('Please enter your password.');
        return;
    }

    const user = users.find(u => u.email === email);

    if (!user) {
        alert('No account found with this email address. Please check your email or register for a new account.');
        return;
    }

    if (user.password !== hashPassword(password)) {
        alert('Incorrect password. Please try again.');
        return;
    }

    user.lastLogin = new Date().toISOString();
    saveUsers();

    currentUser = user;
    isLoggedIn = true;
    userType = user.userType;
    saveSession(user);
    updateNavigation();

    const welcomeName = user.userType === 'employer' ? user.businessName : user.fullName;
    alert(`Login successful! Welcome back to TrabahoPH, ${welcomeName}.`);

    setTimeout(() => {
        window.location.href = '/';
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

    const user = users.find(u => u.email === email);

    if (!user) {
        alert('No account found with this email address.');
        return;
    }

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
        navButtons.innerHTML = `
            <a href="/auth/" class="btn btn-secondary">Login</a>
            <a href="/auth/" class="btn btn-primary">Sign Up</a>
        `;
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

function checkExistingSession() {
    if (currentSession) {
        const sessionAge = Date.now() - currentSession.loginTime;
        const maxAge = 7 * 24 * 60 * 60 * 1000;

        if (sessionAge < maxAge) {
            const user = users.find(u => u.id === currentSession.userId);
            if (user) {
                currentUser = user;
                isLoggedIn = true;
                userType = user.userType;
                updateNavigation();
                return true;
            }
        } else {
            clearSession();
        }
    }
    return false;
}

function downloadResumeGuide() {
    const resumeGuideContent = `TRABAHO PH - RESUME WRITING GUIDE\n=================================\n\nA Complete Guide to Writing an Effective Resume for Filipino Job Seekers\n\nFor more information, visit TrabahoPH.com`;

    const blob = new Blob([resumeGuideContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'TrabahoPH_Resume_Writing_Guide.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    alert('Resume Writing Guide downloaded successfully! Check your Downloads folder.');
}

function openInterviewTips() {
    const youtubeSearchUrl = 'https://www.youtube.com/results?search_query=interview+tips+job+preparation';
    window.open(youtubeSearchUrl, '_blank');
}

function openTESDAcourses() {
    const tesdaCoursesUrl = 'https://e-tesda.gov.ph/course/';
    window.open(tesdaCoursesUrl, '_blank');
}

function openDigitalLiteracy() {
    const digitalLiteracyUrl = 'https://www.youtube.com/results?search_query=digital+literacy+computer+basics+tutorial';
    window.open(digitalLiteracyUrl, '_blank');
}

document.addEventListener('DOMContentLoaded', function() {
    checkExistingSession();
    currentJobs = sampleJobs.slice(0, 3);

    window.onclick = function(event) {
        const modal = document.getElementById('authModal');
        if (event.target === modal) {
            closeModal();
        }
    };

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
});
