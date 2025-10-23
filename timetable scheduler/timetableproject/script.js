// Global State Management
const appState = {
    departments: [],
    rooms: [],
    labs: [],
    yearConfigs: {
        1: { subjects: [] },
        2: { subjects: [] },
        3: { subjects: [] },
        4: { subjects: [] }
    },
    weekConfig: {
        startTime: '09:00',
        endTime: '16:00',
        workingDays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        lunchStart: '13:00',
        lunchEnd: '14:00'
    },
    miniProject: {
        enabled: false,
        hoursPerWeek: 4,
        daysPerWeek: 2,
        sessionDuration: 2
    },
    mathsTutorial: {
        enabled: false,
        hoursPerWeek: 2,
        daysPerWeek: 1
    },
    timetables: {},
    currentView: 'generate'
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeYearTabs();
    initializeSubjectManagement();
    initializeDepartmentManagement();
    initializeRoomManagement();
    initializeSpecialSessions();
    initializeGenerateOptions();
    initializeViewToggles();
    initializeModals();
    initializeHardcodedData();
    populateDepartmentSelects();
});

// Navigation
function initializeNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const viewName = this.dataset.view;
            switchView(viewName);
        });
    });
}

function switchView(viewName) {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.view === viewName) {
            btn.classList.add('active');
        }
    });

    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(viewName + 'View').classList.add('active');

    appState.currentView = viewName;

    if (viewName === 'view') {
        renderTimetableGrid();
    } else if (viewName === 'departments') {
        renderDepartmentsGrid();
    } else if (viewName === 'rooms') {
        renderRoomsGrid();
    }
}

// Year Tabs Management
function initializeYearTabs() {
    const yearTabs = document.querySelectorAll('.year-tab');
    yearTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const year = this.dataset.year;
            switchYearTab(year);
        });
    });
}

function switchYearTab(year) {
    document.querySelectorAll('.year-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.year === year) {
            tab.classList.add('active');
        }
    });

    document.querySelectorAll('.year-config').forEach(config => {
        config.classList.remove('active');
    });
    document.getElementById('year' + year + 'Config').classList.add('active');
}

// Subject Management for Each Year
function initializeSubjectManagement() {
    // Map UI years to predefined subjects
    // UI Year 1 (First Year) -> PREDEFINED_SUBJECTS[1] (First Year Sem 1)
    // UI Year 2 (Second Year) -> PREDEFINED_SUBJECTS[3] (Second Year Sem 1)
    // UI Year 3 (Third Year) -> PREDEFINED_SUBJECTS[5] (Third Year)
    // UI Year 4 (Fourth Year) -> PREDEFINED_SUBJECTS[6] (Fourth Year)
    
    const yearMapping = { 1: 1, 2: 3, 3: 5, 4: 6 };
    for (let uiYear = 1; uiYear <= 4; uiYear++) {
        const predefinedYear = yearMapping[uiYear];
        renderSubjectsWithPredefinedCustom(uiYear, predefinedYear);
    }
}

function addSubject(year) {
    const subject = {
        id: Date.now() + Math.random(),
        name: '',
        type: 'theory',
        theoryHours: 3,
        practicalHours: 0,
        lab: ''
    };
    appState.yearConfigs[year].subjects.push(subject);
    renderSubjects(year);
}

function addCoreSubject(year) {
    const subject = {
        id: Date.now() + Math.random(),
        name: '',
        type: 'theory',
        theoryHours: 3,
        practicalHours: 0,
        lab: ''
    };
    appState.yearConfigs[year].coreSubjects.push(subject);
    renderCoreSubjects(year);
}

function addElective(year) {
    const elective = {
        id: Date.now() + Math.random(),
        name: '',
        type: 'theory',
        theoryHours: 3,
        practicalHours: 0,
        lab: '',
        studentsEnrolled: 0
    };
    appState.yearConfigs[year].electives.push(elective);
    renderElectives(year);
}

function renderSubjects(year) {
    const container = document.getElementById(`subjectsListYear${year}`);
    container.innerHTML = '';

    appState.yearConfigs[year].subjects.forEach((subject, index) => {
        const item = document.createElement('div');
        item.className = 'subject-item';
        
        const showPractical = subject.type === 'both' || subject.type === 'practical';
        const showLab = showPractical;
        
        item.innerHTML = `
            <input type="text" placeholder="Subject Name" value="${subject.name}" 
                   onchange="updateSubject(${year}, ${index}, 'name', this.value)">
            <select onchange="updateSubject(${year}, ${index}, 'type', this.value)">
                <option value="theory" ${subject.type === 'theory' ? 'selected' : ''}>Theory Only</option>
                <option value="practical" ${subject.type === 'practical' ? 'selected' : ''}>Practical Only</option>
                <option value="both" ${subject.type === 'both' ? 'selected' : ''}>Theory + Practical</option>
            </select>
            <input type="number" placeholder="Theory Hours" value="${subject.theoryHours}" min="0" max="10"
                   onchange="updateSubject(${year}, ${index}, 'theoryHours', parseInt(this.value))"
                   ${subject.type === 'practical' ? 'disabled' : ''}>
            <input type="number" placeholder="Practical Hours" value="${subject.practicalHours}" min="0" max="10"
                   onchange="updateSubject(${year}, ${index}, 'practicalHours', parseInt(this.value))"
                   ${!showPractical ? 'disabled' : ''}>
            <button class="remove-subject" onclick="removeSubject(${year}, ${index})">✕</button>
        `;
        container.appendChild(item);
    });
}

function renderCoreSubjects(year) {
    const container = document.getElementById('subjectsListYear4Core');
    container.innerHTML = '';

    appState.yearConfigs[year].coreSubjects.forEach((subject, index) => {
        const item = document.createElement('div');
        item.className = 'subject-item';
        
        const showPractical = subject.type === 'both' || subject.type === 'practical';
        const showLab = showPractical;
        
        item.innerHTML = `
            <input type="text" placeholder="Subject Name" value="${subject.name}" 
                   onchange="updateCoreSubject(${year}, ${index}, 'name', this.value)">
            <select onchange="updateCoreSubject(${year}, ${index}, 'type', this.value)">
                <option value="theory" ${subject.type === 'theory' ? 'selected' : ''}>Theory Only</option>
                <option value="practical" ${subject.type === 'practical' ? 'selected' : ''}>Practical Only</option>
                <option value="both" ${subject.type === 'both' ? 'selected' : ''}>Theory + Practical</option>
            </select>
            <input type="number" placeholder="Theory Hours" value="${subject.theoryHours}" min="0" max="10"
                   onchange="updateCoreSubject(${year}, ${index}, 'theoryHours', parseInt(this.value))"
                   ${subject.type === 'practical' ? 'disabled' : ''}>
            <input type="number" placeholder="Practical Hours" value="${subject.practicalHours}" min="0" max="10"
                   onchange="updateCoreSubject(${year}, ${index}, 'practicalHours', parseInt(this.value))"
                   ${!showPractical ? 'disabled' : ''}>
            <button class="remove-subject" onclick="removeCoreSubject(${year}, ${index})">✕</button>
        `;
        container.appendChild(item);
    });
}

function renderElectives(year) {
    const container = document.getElementById('electivesListYear4');
    container.innerHTML = '';

    appState.yearConfigs[year].electives.forEach((elective, index) => {
        const item = document.createElement('div');
        item.className = 'elective-item';
        
        const showPractical = elective.type === 'both' || elective.type === 'practical';
        const showLab = showPractical;
        
        item.innerHTML = `
            <input type="text" placeholder="Elective Name" value="${elective.name}" 
                   onchange="updateElective(${year}, ${index}, 'name', this.value)">
            <select onchange="updateElective(${year}, ${index}, 'type', this.value)">
                <option value="theory" ${elective.type === 'theory' ? 'selected' : ''}>Theory Only</option>
                <option value="practical" ${elective.type === 'practical' ? 'selected' : ''}>Practical Only</option>
                <option value="both" ${elective.type === 'both' ? 'selected' : ''}>Theory + Practical</option>
            </select>
            <input type="number" placeholder="Theory Hours" value="${elective.theoryHours}" min="0" max="10"
                   onchange="updateElective(${year}, ${index}, 'theoryHours', parseInt(this.value))"
                   ${elective.type === 'practical' ? 'disabled' : ''}>
            <input type="number" placeholder="Practical Hours" value="${elective.practicalHours}" min="0" max="10"
                   onchange="updateElective(${year}, ${index}, 'practicalHours', parseInt(this.value))"
                   ${!showPractical ? 'disabled' : ''}>
            <input type="number" placeholder="Students Enrolled" value="${elective.studentsEnrolled}" min="0"
                   onchange="updateElective(${year}, ${index}, 'studentsEnrolled', parseInt(this.value))">
            <button class="remove-elective" onclick="removeElective(${year}, ${index})">✕</button>
        `;
        container.appendChild(item);
    });
}

function updateSubject(year, index, field, value) {
    appState.yearConfigs[year].subjects[index][field] = value;
    if (field === 'type') {
        if (value === 'theory') {
            appState.yearConfigs[year].subjects[index].practicalHours = 0;
            appState.yearConfigs[year].subjects[index].lab = '';
        } else if (value === 'practical') {
            appState.yearConfigs[year].subjects[index].theoryHours = 0;
        }
    }
    renderSubjects(year);
}

function updateCoreSubject(year, index, field, value) {
    appState.yearConfigs[year].coreSubjects[index][field] = value;
    if (field === 'type') {
        if (value === 'theory') {
            appState.yearConfigs[year].coreSubjects[index].practicalHours = 0;
            appState.yearConfigs[year].coreSubjects[index].lab = '';
        } else if (value === 'practical') {
            appState.yearConfigs[year].coreSubjects[index].theoryHours = 0;
        }
    }
    renderCoreSubjects(year);
}

function updateElective(year, index, field, value) {
    appState.yearConfigs[year].electives[index][field] = value;
    if (field === 'type') {
        if (value === 'theory') {
            appState.yearConfigs[year].electives[index].practicalHours = 0;
            appState.yearConfigs[year].electives[index].lab = '';
        } else if (value === 'practical') {
            appState.yearConfigs[year].electives[index].theoryHours = 0;
        }
    }
    renderElectives(year);
}

function removeSubject(year, index) {
    appState.yearConfigs[year].subjects.splice(index, 1);
    renderSubjects(year);
}

function removeCoreSubject(year, index) {
    appState.yearConfigs[year].coreSubjects.splice(index, 1);
    renderCoreSubjects(year);
}

function removeElective(year, index) {
    appState.yearConfigs[year].electives.splice(index, 1);
    renderElectives(year);
}

function renderSubjectsWithPredefinedCustom(uiYear, predefinedYear) {
    const container = document.getElementById(`subjectsListYear${uiYear}`);
    if (!container) return; // Skip if container doesn't exist
    container.innerHTML = '';

    // Get predefined subjects for this year
    const predefinedSubjects = PREDEFINED_SUBJECTS[predefinedYear] || [];

    // Create a section for selecting from predefined subjects
    const selectorDiv = document.createElement('div');
    selectorDiv.className = 'subject-selector';
    selectorDiv.innerHTML = `
        <label>Select Subject:</label>
        <select id="predefinedSelect${uiYear}" onchange="addPredefinedSubject(${uiYear}, this.value)">
            <option value="">-- Choose a subject --</option>
            ${predefinedSubjects.map((s, idx) => `
                <option value="${idx}">${s.name}</option>
            `).join('')}
        </select>
    `;
    container.appendChild(selectorDiv);

    // Display selected subjects
    const selectedDiv = document.createElement('div');
    selectedDiv.className = 'selected-subjects';
    selectedDiv.id = `selectedSubjects${uiYear}`;
    container.appendChild(selectedDiv);

    renderSelectedSubjects(uiYear);
}

function renderSubjectsWithPredefined(year) {
    // Legacy function - kept for compatibility
    renderSubjectsWithPredefinedCustom(year, year);
}

function renderSelectedSubjects(year) {
    const container = document.getElementById(`selectedSubjects${year}`);
    if (!container) return;
    container.innerHTML = '';

    appState.yearConfigs[year].subjects.forEach((subject, index) => {
        const item = document.createElement('div');
        item.className = 'subject-item';
        
        const showPractical = subject.type === 'both' || subject.type === 'practical';
        
        item.innerHTML = `
            <div class="subject-name">${subject.name}</div>
            <select onchange="updateSubject(${year}, ${index}, 'type', this.value)">
                <option value="theory" ${subject.type === 'theory' ? 'selected' : ''}>Theory Only</option>
                <option value="practical" ${subject.type === 'practical' ? 'selected' : ''}>Practical Only</option>
                <option value="both" ${subject.type === 'both' ? 'selected' : ''}>Theory + Practical</option>
            </select>
            <input type="number" placeholder="Theory Hours" value="${subject.theoryHours}" min="0" max="10"
                   onchange="updateSubject(${year}, ${index}, 'theoryHours', parseInt(this.value))"
                   ${subject.type === 'practical' ? 'disabled' : ''}>
            <input type="number" placeholder="Practical Hours" value="${subject.practicalHours}" min="0" max="10"
                   onchange="updateSubject(${year}, ${index}, 'practicalHours', parseInt(this.value))"
                   ${!showPractical ? 'disabled' : ''}>
            <input type="text" placeholder="Teacher Name" value="${subject.teacher || ''}"
                   onchange="updateSubject(${year}, ${index}, 'teacher', this.value)">
            <button class="remove-subject" onclick="removeSubject(${year}, ${index})">✕</button>
        `;
        container.appendChild(item);
    });
}

// Add predefined subject with correct year mapping
function addPredefinedSubject(uiYear, subjectIndex) {
    if (subjectIndex === '') return;
    
    // Map UI year to predefined subjects index
    const yearMapping = { 1: 1, 2: 3, 3: 5, 4: 6 };
    const predefinedYear = yearMapping[uiYear];
    
    const predefinedSubjects = PREDEFINED_SUBJECTS[predefinedYear] || [];
    const selectedSubject = predefinedSubjects[parseInt(subjectIndex)];
    
    if (!selectedSubject) return;

    // Check if already added
    const alreadyExists = appState.yearConfigs[uiYear].subjects.some(s => s.name === selectedSubject.name);
    if (alreadyExists) {
        alert('This subject is already added!');
        return;
    }

    const subject = {
        id: Date.now() + Math.random(),
        name: selectedSubject.name,
        type: selectedSubject.type,
        theoryHours: selectedSubject.type === 'practical' ? 0 : 3,
        practicalHours: selectedSubject.type === 'theory' ? 0 : 2,
        teacher: ''
    };
    
    appState.yearConfigs[uiYear].subjects.push(subject);
    
    // Reset dropdown
    document.getElementById(`predefinedSelect${uiYear}`).value = '';
    
    renderSelectedSubjects(uiYear);
}

function updateSubject(year, index, field, value) {
    appState.yearConfigs[year].subjects[index][field] = value;
    renderSelectedSubjects(year);
}

function removeSubject(year, index) {
    appState.yearConfigs[year].subjects.splice(index, 1);
    renderSelectedSubjects(year);
}

// Department Management
function initializeDepartmentManagement() {
    document.getElementById('addDepartmentBtn').addEventListener('click', () => {
        document.getElementById('departmentModal').classList.add('active');
    });

    document.getElementById('addDeptModalBtn').addEventListener('click', () => {
        document.getElementById('departmentModal').classList.add('active');
    });
}

function renderDepartmentsGrid() {
    const container = document.getElementById('departmentsGrid');
    
    if (appState.departments.length === 0) {
        container.innerHTML = '<p class="text-muted">No departments added yet. Click "Add Department" to get started.</p>';
        return;
    }
    
    container.innerHTML = '';
    appState.departments.forEach((dept, index) => {
        const card = document.createElement('div');
        card.className = 'department-card';
        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${dept.name}</div>
                <div class="card-actions">
                    <button class="btn-icon" onclick="editDepartment(${index})">✏️</button>
                    <button class="btn-icon" onclick="deleteDepartment(${index})">🗑️</button>
                </div>
            </div>
            <div class="card-info">
                <div class="info-row">
                    <span class="info-label">Code:</span>
                    <span class="info-value">${dept.code}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Description:</span>
                    <span class="info-value">${dept.description || 'N/A'}</span>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

function editDepartment(index) {
    const dept = appState.departments[index];
    document.getElementById('deptName').value = dept.name;
    document.getElementById('deptCode').value = dept.code;
    document.getElementById('deptDescription').value = dept.description || '';
    document.getElementById('departmentModal').classList.add('active');
    document.getElementById('departmentModal').dataset.editIndex = index;
}

function deleteDepartment(index) {
    if (confirm('Are you sure you want to delete this department?')) {
        appState.departments.splice(index, 1);
        renderDepartmentsGrid();
        populateDepartmentSelects();
    }
}

function populateDepartmentSelects() {
    const selects = document.querySelectorAll('#departmentSelect, #filterDept');
    selects.forEach(select => {
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select Department</option>';
        appState.departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.name;  
            option.textContent = dept.name;
            select.appendChild(option);
        });
        select.value = currentValue;
    });
}

// Room Management
function initializeRoomManagement() {
    document.getElementById('addRoomBtn').addEventListener('click', () => {
        openRoomModal();
    });

    document.getElementById('roomType').addEventListener('change', function() {
        const labSubjectGroup = document.getElementById('labSubjectGroup');
        if (this.value === 'lab') {
            labSubjectGroup.style.display = 'block';
        } else {
            labSubjectGroup.style.display = 'none';
        }
    });
}

function openRoomModal(roomIndex = null) {
    const modal = document.getElementById('roomModal');
    modal.classList.add('active');
    
    if (roomIndex !== null) {
        const room = appState.rooms[roomIndex];
        document.getElementById('roomName').value = room.name;
        document.getElementById('roomType').value = room.type;
        document.getElementById('roomCapacity').value = room.capacity;
        document.getElementById('roomLocation').value = room.location || '';
        document.getElementById('roomTags').value = room.tags.join(', ');
        document.getElementById('labSubject').value = room.labSubject || '';
        modal.dataset.editIndex = roomIndex;
        
        if (room.type === 'lab') {
            document.getElementById('labSubjectGroup').style.display = 'block';
        }
    } else {
        document.getElementById('roomName').value = '';
        document.getElementById('roomType').value = 'classroom';
        document.getElementById('roomCapacity').value = '';
        document.getElementById('roomLocation').value = '';
        document.getElementById('roomTags').value = '';
        document.getElementById('labSubject').value = '';
        document.getElementById('labSubjectGroup').style.display = 'none';
        delete modal.dataset.editIndex;
    }
}

function renderRoomsGrid() {
    const container = document.getElementById('roomsGrid');
    
    if (appState.rooms.length === 0) {
        container.innerHTML = '<p class="text-muted">No rooms added yet. Click "Add Room/Lab" to get started.</p>';
        return;
    }
    
    container.innerHTML = '';
    appState.rooms.forEach((room, index) => {
        const card = document.createElement('div');
        card.className = 'room-card';
        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${room.name}</div>
                <div class="card-actions">
                    <button class="btn-icon" onclick="editRoom(${index})">✏️</button>
                    <button class="btn-icon" onclick="deleteRoom(${index})">🗑️</button>
                </div>
            </div>
            <div class="card-info">
                <div class="info-row">
                    <span class="info-label">Type:</span>
                    <span class="info-value">${room.type}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Capacity:</span>
                    <span class="info-value">${room.capacity} students</span>
                </div>
                ${room.location ? `
                <div class="info-row">
                    <span class="info-label">Location:</span>
                    <span class="info-value">${room.location}</span>
                </div>
                ` : ''}
                ${room.type === 'lab' && room.labSubject ? `
                <div class="info-row">
                    <span class="info-label">For Subject:</span>
                    <span class="info-value">${room.labSubject}</span>
                </div>
                ` : ''}
                ${room.tags.length > 0 ? `
                <div class="tags">
                    ${room.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                </div>
                ` : ''}
            </div>
        `;
        container.appendChild(card);
    });
}

function editRoom(index) {
    openRoomModal(index);
}

function deleteRoom(index) {
    if (confirm('Are you sure you want to delete this room?')) {
        appState.rooms.splice(index, 1);
        renderRoomsGrid();
    }
}

// Special Sessions
function initializeSpecialSessions() {
    // Tutorial and Mini-Project sessions are now simple checkboxes with fixed 2 hours
    // No additional settings to show/hide
    // Checkboxes are handled automatically by the form
}

// Generate Options
function initializeGenerateOptions() {
    const modeRadios = document.querySelectorAll('input[name="generateMode"]');
    modeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const individualSelect = document.getElementById('individualYearSelect');
            if (this.value === 'individual') {
                individualSelect.style.display = 'block';
            } else {
                individualSelect.style.display = 'none';
            }
        });
    });

    document.getElementById('generateBtn').addEventListener('click', generateTimetable);
}

async function generateTimetable() {
    const deptSelect = document.getElementById('departmentSelect');
    const dept = deptSelect.value || deptSelect.options[deptSelect.selectedIndex]?.text;
    
    console.log('Selected department:', dept);
    console.log('Department select value:', deptSelect.value);
    console.log('Department select options:', Array.from(deptSelect.options).map(o => o.value + ' - ' + o.text));
    
    if (!dept) {
        alert('Please select a department');
        return;
    }

    const mode = document.querySelector('input[name="generateMode"]:checked').value;
    const selectedYear = mode === 'individual' ? parseInt(document.getElementById('generateYearSelect').value) : null;

    // Validate that subjects are configured
    if (mode === 'all') {
        for (let year = 1; year <= 4; year++) {
            if (!validateYearConfiguration(year)) {
                alert(`Please configure subjects for Year ${year}`);
                return;
            }
        }
    } else {
        if (!validateYearConfiguration(selectedYear)) {
            alert(`Please configure subjects for Year ${selectedYear}`);
            return;
        }
    }

    // Show loading
    document.getElementById('loadingOverlay').classList.add('active');

    // Prepare data for backend
    const requestData = {
        department: dept,
        mode: mode,
        selectedYear: selectedYear,
        yearConfigs: appState.yearConfigs,
        weekConfig: appState.weekConfig,
        miniProject: appState.miniProject,
        mathsTutorial: appState.mathsTutorial,
        rooms: appState.rooms,
        labs: appState.labs
    };

    try {
        // Simulate backend call (replace with actual API call)
        await simulateBackendCall(requestData);
        
        switchView('view');
        alert('Timetable generated successfully!');
    } catch (error) {
        alert('Error generating timetable: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').classList.remove('active');
    }
}

function validateYearConfiguration(year) {
    const config = appState.yearConfigs[year];
    if (!config) return false;
    
    // Check if subjects array exists and has items
    if (config.subjects && config.subjects.length > 0) {
        return true;
    }
    
    // For Year 4, also check coreSubjects and electives if they exist
    if (year === 4 && config.coreSubjects && config.electives) {
        return config.coreSubjects.length > 0 || config.electives.length > 0;
    }
    
    return false;
}

async function simulateBackendCall(data) {
    console.log('=== DEBUG: simulateBackendCall called ===');
    console.log('Data received:', data);
    
    // Determine which year to generate for
    const targetYear = data.mode === 'individual' ? data.selectedYear : 1;
    console.log(`Generating for Year ${targetYear}`);
    console.log(`Year ${targetYear} subjects:`, data.yearConfigs[targetYear].subjects);
    
    // Day name conversion
    const dayMap = {'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed', 'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'};
    const workingDays = data.weekConfig.workingDays.map(day => dayMap[day] || day);
    console.log('Working days:', workingDays);
    
    // Subject conversion
    if (!data.yearConfigs[targetYear].subjects || data.yearConfigs[targetYear].subjects.length === 0) {
        throw new Error(`No subjects configured for Year ${targetYear}`);
    }
    
    const subjects = data.yearConfigs[targetYear].subjects.map(s => ({
        name: s.name,
        type: s.type === 'both' ? 'theory+lab' : s.type,
        hours_per_week: s.theoryHours + (s.practicalHours || 0),
        teacher: s.teacher || ''
    }));
    console.log('Converted subjects:', subjects);
    
    // Check for special sessions (Tutorial and Mini-Project) and add as subjects
    const mathsTutorialCheckbox = document.getElementById(`mathsTutorialToggle${targetYear}`);
    const miniProjectCheckbox = document.getElementById(`miniProjectToggle${targetYear}`);
    
    console.log(`Checking special sessions for Year ${targetYear}:`);
    console.log(`  Maths Tutorial checkbox:`, mathsTutorialCheckbox, 'checked:', mathsTutorialCheckbox?.checked);
    console.log(`  Mini-Project checkbox:`, miniProjectCheckbox, 'checked:', miniProjectCheckbox?.checked);
    
    if (mathsTutorialCheckbox?.checked) {
        subjects.push({
            name: 'Maths Tutorial',
            type: 'theory',
            hours_per_week: 2
        });
        console.log('✅ Added Maths Tutorial (2 hours)');
    }
    
    if (miniProjectCheckbox?.checked) {
        subjects.push({
            name: 'Mini-Project',
            type: 'theory',
            hours_per_week: 2
        });
        console.log('✅ Added Mini-Project (2 hours)');
    }
    
    console.log(`Total subjects after special sessions: ${subjects.length}`);
    
    // Build clean request
    const payload = {
        department: data.department,
        week_config: {
            week_start_time: data.weekConfig.startTime,
            week_end_time: data.weekConfig.endTime,
            lunch_start: data.weekConfig.lunchStart,
            lunch_end: data.weekConfig.lunchEnd,
            working_days: workingDays
        },
        rooms: data.rooms.map(r => ({name: r.name, type: r.type, capacity: r.capacity, location: r.location || 'TBA'})),
        subjects: subjects,
        special_sessions: {}
    };
    
    console.log('Sending payload:', JSON.stringify(payload, null, 2));
    
    const response = await fetch('http://localhost:8000/api/timetable/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    const result = await response.json();
    
    if (!response.ok) {
        console.error('Backend error:', result);
        throw new Error(result.detail?.[0]?.msg || result.message || 'Failed to generate timetable');
    }
    
    if (result.status === 'success') {
        console.log('Backend returned timetable:', result.timetable);
        const timetableKey = `year${targetYear}`;
        appState.timetables[timetableKey] = result.timetable || [];
        console.log(`Stored in appState.timetables.${timetableKey}:`, appState.timetables[timetableKey]);
        return result;
    } else {
        throw new Error(result.message || 'Failed to generate timetable');
    }
}

function generateSampleTimetable(data) {
    const days = appState.weekConfig.workingDays;
    const hours = generateHourSlots();
    
    if (data.mode === 'all') {
        for (let year = 1; year <= 4; year++) {
            generateYearTimetable(year, days, hours);
        }
    } else {
        generateYearTimetable(data.selectedYear, days, hours);
    }
}

function generateHourSlots() {
    const start = parseInt(appState.weekConfig.startTime.split(':')[0]);
    const end = parseInt(appState.weekConfig.endTime.split(':')[0]);
    const lunchHour = parseInt(appState.weekConfig.lunchStart.split(':')[0]);
    
    const hours = [];
    for (let h = start; h < end; h++) {
        if (h !== lunchHour) {
            hours.push(h);
        }
    }
    return hours;
}

function generateYearTimetable(year, days, hours) {
    const config = appState.yearConfigs[year];
    const subjects = year === 4 ? [...config.coreSubjects, ...config.electives] : config.subjects;
    
    const timetableKey = `year${year}`;
    appState.timetables[timetableKey] = [];
    
    // Simple random distribution (will be replaced by GNN algorithm)
    days.forEach(day => {
        hours.forEach(hour => {
            if (Math.random() > 0.3 && subjects.length > 0) {
                const subject = subjects[Math.floor(Math.random() * subjects.length)];
                const room = appState.rooms[Math.floor(Math.random() * appState.rooms.length)];
                
                appState.timetables[timetableKey].push({
                    day: day,
                    hour: hour,
                    subject: subject,
                    room: room || { name: 'TBA', type: 'classroom' },
                    type: subject.type === 'both' ? (Math.random() > 0.5 ? 'theory' : 'practical') : subject.type,
                    batch: Math.random() > 0.5 ? 'A' : (Math.random() > 0.5 ? 'B' : 'C')
                });
            }
        });
    });
}

// View Toggles
function initializeViewToggles() {
    const toggles = document.querySelectorAll('.view-toggle-btn');
    toggles.forEach(btn => {
        btn.addEventListener('click', function() {
            const viewType = this.dataset.viewtype;
            toggles.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            document.getElementById('gridView').style.display = viewType === 'grid' ? 'block' : 'none';
            document.getElementById('timelineView').style.display = viewType === 'timeline' ? 'block' : 'none';
            document.getElementById('agendaView').style.display = viewType === 'agenda' ? 'block' : 'none';
            
            if (viewType === 'timeline') renderTimelineView();
            if (viewType === 'agenda') renderAgendaView();
        });
    });

    // Add event listener for year filter dropdown
    const filterYearSelect = document.getElementById('filterYear');
    if (filterYearSelect) {
        filterYearSelect.addEventListener('change', function() {
            renderTimetableGrid();
            renderTimelineView();
            renderAgendaView();
        });
    }

    // Publish button
    const publishBtn = document.getElementById('publishBtn');
    if (publishBtn) {
        publishBtn.addEventListener('click', publishTimetable);
    }
}

function renderTimetableGrid() {
    const container = document.getElementById('timetableGrid');
    const filterYear = document.getElementById('filterYear').value;
    
    if (!filterYear) {
        container.innerHTML = '<p class="text-muted">Please select a year to view the timetable.</p>';
        return;
    }
    
    const timetableKey = `year${filterYear}`;
    const timetable = appState.timetables[timetableKey] || [];
    
    if (timetable.length === 0) {
        container.innerHTML = '<p class="text-muted">No timetable generated for this year yet.</p>';
        return;
    }
    
    const dayMap = {'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday'};
    const days = appState.weekConfig.workingDays.map(d => d.substring(0, 3));
    const hours = generateHourSlots();
    const lunchHour = parseInt(appState.weekConfig.lunchStart.split(':')[0]);
    
    let html = '<table class="timetable-table"><thead><tr><th>Time</th>';
    days.forEach(day => {
        html += `<th>${dayMap[day] || day}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    const allHours = [...hours];
    if (!allHours.includes(lunchHour)) {
        allHours.push(lunchHour);
        allHours.sort((a, b) => a - b);
    }
    
    allHours.forEach(hour => {
        html += '<tr>';
        html += `<td class="time-cell">${hour}:00 - ${hour + 1}:00</td>`;
        
        days.forEach(day => {
            if (hour === lunchHour) {
                html += '<td class="lunch-cell">LUNCH BREAK</td>';
            } else {
                const timeSlot = `${String(hour).padStart(2, '0')}:00-${String(hour + 1).padStart(2, '0')}:00`;
                const classes = timetable.filter(c => {
                    if (c.day !== day) return false;
                    // Check if class starts at this hour (only show once, at start hour)
                    const classStartTime = c.slot.split('-')[0]; // e.g., "09:00" from "09:00-11:00"
                    const classStartHour = parseInt(classStartTime.split(':')[0]);
                    return classStartHour === hour;
                });
                html += '<td>';
                classes.forEach(cls => {
                    html += `
                        <div class="class-block ${cls.type}">
                            <div class="class-subject">${cls.subject || 'N/A'}</div>
                            <div class="class-room">${cls.room || 'N/A'}</div>
                            ${cls.teacher ? `<div class="class-teacher">${cls.teacher}</div>` : ''}
                        </div>
                    `;
                });
                html += '</td>';
            }
        });
        
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
    console.log('Timetable rendered:', timetable);
}

function renderTimelineView() {
    const container = document.getElementById('timelineContainer');
    const filterYear = document.getElementById('filterYear').value;
    
    if (!filterYear) {
        container.innerHTML = '<p class="text-muted">Please select a year to view the timeline.</p>';
        return;
    }
    
    const timetableKey = `year${filterYear}`;
    const timetable = appState.timetables[timetableKey] || [];
    
    if (timetable.length === 0) {
        container.innerHTML = '<p class="text-muted">No timetable data available.</p>';
        return;
    }
    
    const rooms = [...new Set(timetable.map(c => c.room.name))];
    
    let html = '';
    rooms.forEach(roomName => {
        const roomClasses = timetable.filter(c => c.room.name === roomName);
        html += `
            <div class="timeline-row">
                <div class="timeline-label">${roomName}</div>
                <div class="timeline-slots">
                    ${roomClasses.map(c => `
                        <div class="timeline-slot">
                            ${c.day} ${c.hour}:00 - ${c.subject.name}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html || '<p class="text-muted">No schedule data available</p>';
}

function renderAgendaView() {
    const container = document.getElementById('agendaContainer');
    const filterYear = document.getElementById('filterYear').value;
    
    if (!filterYear) {
        container.innerHTML = '<p class="text-muted">Please select a year to view the agenda.</p>';
        return;
    }
    
    const timetableKey = `year${filterYear}`;
    const timetable = appState.timetables[timetableKey] || [];
    
    if (timetable.length === 0) {
        container.innerHTML = '<p class="text-muted">No timetable data available.</p>';
        return;
    }
    
    const days = appState.weekConfig.workingDays;
    
    let html = '';
    days.forEach(day => {
        const dayClasses = timetable.filter(c => c.day === day).sort((a, b) => a.hour - b.hour);
        html += `
            <div class="agenda-day">
                <div class="agenda-day-header">${day}</div>
                <div class="agenda-events">
                    ${dayClasses.map(c => `
                        <div class="agenda-event">
                            <div class="agenda-time">${c.hour}:00 - ${c.hour + 1}:00</div>
                            <div class="agenda-details">
                                <strong>${c.subject.name}</strong> (${c.type})<br>
                                Room: ${c.room.name} | Batch: ${c.batch}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html || '<p class="text-muted">No schedule data available</p>';
}

function publishTimetable() {
    if (confirm('Publish this timetable? This will make it available to all students and staff.')) {
        alert('Timetable published successfully!');
    }
}

// Modal Management
function initializeModals() {
    // Department Modal
    document.getElementById('closeDepartmentModal').addEventListener('click', function() {
        document.getElementById('departmentModal').classList.remove('active');
    });
    
    document.getElementById('cancelDeptBtn').addEventListener('click', function() {
        document.getElementById('departmentModal').classList.remove('active');
    });
    
    document.getElementById('saveDeptBtn').addEventListener('click', async function() {
        const modal = document.getElementById('departmentModal');
        const name = document.getElementById('deptName').value;
        const code = document.getElementById('deptCode').value;
        const description = document.getElementById('deptDescription').value;
        
        if (!name || !code) {
            alert('Please enter department name and code');
            return;
        }
        
        const dept = { name, code, description };
        
        try {
            // Call backend API
            const response = await fetch('http://localhost:8000/api/departments/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    department_name: name,
                    subjects: []
                })
            });
            
            const result = await response.json();
            
            // Add to local state
            appState.departments.push(dept);
            
            modal.classList.remove('active');
            renderDepartmentsGrid();
            populateDepartmentSelects();
            
            // Clear form
            document.getElementById('deptName').value = '';
            document.getElementById('deptCode').value = '';
            document.getElementById('deptDescription').value = '';
            
            alert('Department saved successfully!');
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving department: ' + error.message);
        }
    });
    
    // Room Modal
    document.getElementById('closeRoomModal').addEventListener('click', function() {
        document.getElementById('roomModal').classList.remove('active');
    });
    
    document.getElementById('cancelRoomBtn').addEventListener('click', function() {
        document.getElementById('roomModal').classList.remove('active');
    });
    
    document.getElementById('saveRoomBtn').addEventListener('click', async function() {
        const modal = document.getElementById('roomModal');
        const name = document.getElementById('roomName').value;
        const type = document.getElementById('roomType').value;
        const capacity = parseInt(document.getElementById('roomCapacity').value);
        const location = document.getElementById('roomLocation').value;
        const tags = document.getElementById('roomTags').value.split(',').map(t => t.trim()).filter(t => t);
        const labSubject = type === 'lab' ? document.getElementById('labSubject').value : '';
        
        if (!name || !capacity) {
            alert('Please enter room name and capacity');
            return;
        }
        
        const room = { name, type, capacity, location, tags, labSubject };
        
        try {
            // Call backend API
            const response = await fetch('http://localhost:8000/api/rooms/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rooms: [{
                        name: name,
                        type: type,
                        capacity: capacity,
                        location: location
                    }]
                })
            });
            
            const result = await response.json();
            
            // Add to local state
            appState.rooms.push(room);
            
            modal.classList.remove('active');
            renderRoomsGrid();
            
            // Clear form
            document.getElementById('roomName').value = '';
            document.getElementById('roomType').value = 'classroom';
            document.getElementById('roomCapacity').value = '';
            document.getElementById('roomLocation').value = '';
            document.getElementById('roomTags').value = '';
            document.getElementById('labSubject').value = '';
            document.getElementById('labSubjectGroup').style.display = 'none';
            
            alert('Room saved successfully!');
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving room: ' + error.message);
        }
    });
    
    // Close modals on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });
}

// Load Sample Data
// Load Sample Data (Departments and Rooms only - subjects are predefined)
function loadSampleData() {
    appState.departments = [
        {
            name: 'Computer Science',
            code: 'CS',
            description: 'Department of Computer Science and Engineering'
        },
        {
            name: 'Electrical Engineering',
            code: 'EE',
            description: 'Department of Electrical and Electronics Engineering'
        }
    ];
    
    appState.rooms = [
        {
            name: 'Room 101',
            type: 'classroom',
            capacity: 60,
            location: 'Building A',
            tags: ['projector', 'whiteboard'],
            labSubject: ''
        },
        {
            name: 'Lab 7 - Basic Electrical',
            type: 'lab',
            capacity: 30,
            location: 'Building B',
            tags: ['computers', 'equipment'],
            labSubject: 'Basic Electrical Engineering'
        },
        {
            name: 'CS Lab 1',
            type: 'lab',
            capacity: 30,
            location: 'Building C',
            tags: ['computers', 'projector'],
            labSubject: 'Programming'
        }
    ];
    
    // Subjects are now managed through predefined subjects in subjects_data.js
    // Admin will select subjects from the dropdown
    
    populateDepartmentSelects();
}

// Week Configuration Update
document.getElementById('weekStartTime')?.addEventListener('change', function() {
    appState.weekConfig.startTime = this.value;
});

document.getElementById('weekEndTime')?.addEventListener('change', function() {
    appState.weekConfig.endTime = this.value;
});

document.getElementById('lunchStartTime')?.addEventListener('change', function() {
    appState.weekConfig.lunchStart = this.value;
});

document.getElementById('lunchEndTime')?.addEventListener('change', function() {
    appState.weekConfig.lunchEnd = this.value;
});

// Working days update
document.querySelectorAll('.days-selector input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const checkedDays = Array.from(document.querySelectorAll('.days-selector input[type="checkbox"]:checked'))
            .map(cb => cb.value);
        appState.weekConfig.workingDays = checkedDays;
    });
});

// Old duplicate function removed - using the correct one above

// Update deleteDepartment function
async function deleteDepartment(index) {
    if (confirm('Are you sure you want to delete this department?')) {
        try {
            const response = await fetch(`http://localhost:8000/api/departments/${appState.departments[index].name}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            if (result.success) {
                appState.departments.splice(index, 1);
                renderDepartmentsGrid();
                populateDepartmentSelects();
            }
        } catch (error) {
            alert('Error deleting department: ' + error.message);
        }
    }
}

// Update deleteRoom function
async function deleteRoom(index) {
    if (confirm('Are you sure you want to delete this room?')) {
        try {
            const response = await fetch(`http://localhost:8000/api/rooms/${appState.rooms[index].name}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            if (result.success) {
                appState.rooms.splice(index, 1);
                renderRoomsGrid();
            }
        } catch (error) {
            alert('Error deleting room: ' + error.message);
        }
    }
}

// All delete functions defined above

// Add this function to load data from backend on page load:
async function loadDataFromBackend() {
    try {
        // Load departments
        const deptResponse = await fetch('http://localhost:8000/api/departments/');
        const deptData = await deptResponse.json();
        if (deptData.departments && deptData.departments.length > 0) {
            appState.departments = deptData.departments;
        }
        
        // Load rooms
        const roomResponse = await fetch('http://localhost:8000/api/rooms/');
        const roomData = await roomResponse.json();
        if (roomData.rooms && roomData.rooms.length > 0) {
            appState.rooms = roomData.rooms;
        }
        
        populateDepartmentSelects();
    } catch (error) {
        console.log('Using sample data (backend not available):', error.message);
        // Fall back to sample data if backend is not running
    }
}

// Update the DOMContentLoaded event - find the existing one and add this line:
// Add this line after loadSampleData() in the DOMContentLoaded event:
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeYearTabs();
    initializeSubjectManagement();
    initializeDepartmentManagement();
    initializeRoomManagement();
    initializeSpecialSessions();
    initializeGenerateOptions();
    initializeViewToggles();
    initializeModals();
    loadSampleData();
    loadDataFromBackend(); // ADD THIS LINE
    populateDepartmentSelects();
});

// Make these functions globally accessible (add to the bottom with other window assignments):
window.deleteDepartment = deleteDepartment;
window.deleteRoom = deleteRoom;
// Batch configuration updates
for (let year = 1; year <= 4; year++) {
    document.getElementById(`year${year}Batches`)?.addEventListener('change', function() {
        appState.yearConfigs[year].batches = parseInt(this.value);
    });
    
    document.getElementById(`year${year}StudentsPerBatch`)?.addEventListener('change', function() {
        appState.yearConfigs[year].studentsPerBatch = parseInt(this.value);
    });
}

// Export Functions
document.getElementById('exportPdfBtn')?.addEventListener('click', exportToPDF);
document.getElementById('exportExcelBtn')?.addEventListener('click', exportToExcel);

function exportToPDF() {
    const filterYear = document.getElementById('filterYear').value;
    if (!filterYear) {
        alert('Please select a year to export');
        return;
    }
    
    const timetableKey = `year${filterYear}`;
    const timetable = appState.timetables[timetableKey] || [];
    
    if (timetable.length === 0) {
        alert('No timetable data to export');
        return;
    }
    
    try {
        // Create new PDF document
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('l', 'mm', 'a4'); // landscape, millimeters, A4
        
        // Add title
        doc.setFontSize(18);
        doc.text(`Timetable - Year ${filterYear}`, 14, 15);
        
        // Group by day
        const dayOrder = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const days = [...new Set(timetable.map(t => t.day))].sort((a, b) => 
            dayOrder.indexOf(a) - dayOrder.indexOf(b)
        );
        
        let yPosition = 25;
        
        days.forEach(day => {
            const daySlots = timetable.filter(t => t.day === day)
                .sort((a, b) => a.start_hour - b.start_hour);
            
            // Day header
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.text(day, 14, yPosition);
            yPosition += 7;
            
            // Create table data
            const tableData = daySlots.map(slot => [
                slot.slot || `${slot.start_time}-${slot.end_time}`,
                slot.subject || 'N/A',
                slot.room || 'N/A',
                slot.type || 'N/A',
                slot.teacher || ''
            ]);
            
            // Add table
            doc.autoTable({
                startY: yPosition,
                head: [['Time', 'Subject', 'Room', 'Type', 'Teacher']],
                body: tableData,
                theme: 'grid',
                styles: { fontSize: 10 },
                headStyles: { fillColor: [37, 99, 235], textColor: 255 },
                margin: { left: 14 },
                didDrawPage: function(data) {
                    yPosition = data.cursor.y + 10;
                }
            });
            
            yPosition = doc.lastAutoTable.finalY + 10;
            
            // Check if we need a new page
            if (yPosition > 180 && day !== days[days.length - 1]) {
                doc.addPage();
                yPosition = 20;
            }
        });
        
        // Save the PDF
        doc.save(`timetable_year${filterYear}.pdf`);
        alert('PDF exported successfully!');
        
    } catch (error) {
        console.error('PDF export error:', error);
        alert('Error exporting PDF. Please try again.');
    }
}

function exportToExcel() {
    const filterYear = document.getElementById('filterYear').value;
    if (!filterYear) {
        alert('Please select a year to export');
        return;
    }
    
    const timetableKey = `year${filterYear}`;
    const timetable = appState.timetables[timetableKey] || [];
    
    if (timetable.length === 0) {
        alert('No timetable data to export');
        return;
    }
    
    // Create CSV content
    let csv = 'Day,Time,Subject,Room,Type,Teacher\n';
    timetable.forEach(slot => {
        csv += `${slot.day},${slot.slot},${slot.subject},${slot.room},${slot.type},${slot.teacher || ''}\n`;
    });
    
    // Download CSV file
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `timetable_year${filterYear}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    alert('Timetable exported as CSV (can be opened in Excel)');
}

// Make functions globally accessible
window.updateSubject = updateSubject;
window.updateCoreSubject = updateCoreSubject;
window.updateElective = updateElective;
window.removeSubject = removeSubject;
window.removeCoreSubject = removeCoreSubject;
window.removeElective = removeElective;
window.editDepartment = editDepartment;
window.deleteDepartment = deleteDepartment;
window.editRoom = editRoom;
window.deleteRoom = deleteRoom;