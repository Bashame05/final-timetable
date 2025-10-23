// Hardcoded Data - Departments, Rooms, Labs, and Batches

// Departments
const HARDCODED_DEPARTMENTS = [
    { name: 'Electrical', code: 'EE', description: 'Department of Electrical Engineering' },
    { name: 'Computer Science', code: 'CS', description: 'Department of Computer Science and Engineering' },
    { name: 'IOT', code: 'IOT', description: 'Department of Internet of Things' }
];

// Classrooms (C1-C15)
const HARDCODED_CLASSROOMS = Array.from({ length: 15 }, (_, i) => ({
    name: `C${i + 1}`,
    type: 'classroom',
    capacity: 60,
    location: `Building A`,
    tags: ['projector', 'whiteboard']
}));

// Labs (L1-L10)
const HARDCODED_LABS = Array.from({ length: 10 }, (_, i) => ({
    name: `L${i + 1}`,
    type: 'lab',
    capacity: 30,
    location: `Building B`,
    tags: ['computers', 'equipment']
}));

// All Rooms (Classrooms + Labs)
const HARDCODED_ROOMS = [...HARDCODED_CLASSROOMS, ...HARDCODED_LABS];

// Batches (A, B, C)
const HARDCODED_BATCHES = ['Batch A', 'Batch B', 'Batch C'];

// Function to initialize hardcoded data
function initializeHardcodedData() {
    appState.departments = JSON.parse(JSON.stringify(HARDCODED_DEPARTMENTS));
    appState.rooms = JSON.parse(JSON.stringify(HARDCODED_ROOMS));
    
    // Set batches for all years
    for (let year = 1; year <= 4; year++) {
        appState.yearConfigs[year].batches = 3;
        appState.yearConfigs[year].batchNames = JSON.parse(JSON.stringify(HARDCODED_BATCHES));
    }
    
    console.log('Hardcoded data initialized:');
    console.log('Departments:', appState.departments);
    console.log('Rooms:', appState.rooms);
    console.log('Classrooms:', HARDCODED_CLASSROOMS.length);
    console.log('Labs:', HARDCODED_LABS.length);
    console.log('Batches:', HARDCODED_BATCHES);
}
