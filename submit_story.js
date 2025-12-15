// Load family tree to populate dropdowns
let familyTree = null;

async function loadFamilyTree() {
    try {
        const response = await fetch('family_tree.json');
        familyTree = await response.json();
        populateAuthorDropdown();
        populatePeopleCheckboxes();
    } catch (error) {
        console.error('Error loading family tree:', error);
    }
}

function populateAuthorDropdown() {
    const select = document.getElementById('author');
    const people = familyTree.family.people;

    // Get all living people, sorted by name
    const livingPeople = Object.values(people)
        .filter(person => person.dod === 'alive')
        .sort((a, b) => a.name.localeCompare(b.name));

    livingPeople.forEach(person => {
        const option = document.createElement('option');
        option.value = person.name;
        option.textContent = person.name;
        select.appendChild(option);
    });
}

function populatePeopleCheckboxes() {
    const container = document.getElementById('peopleCheckboxes');
    const people = familyTree.family.people;

    // Get all people, sorted by name
    const allPeople = Object.values(people)
        .sort((a, b) => a.name.localeCompare(b.name));

    allPeople.forEach(person => {
        const div = document.createElement('div');
        div.className = 'checkbox-item';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = 'person_' + person.id;
        checkbox.name = 'mentions';
        checkbox.value = person.name;

        const label = document.createElement('label');
        label.htmlFor = 'person_' + person.id;
        label.textContent = person.name;

        div.appendChild(checkbox);
        div.appendChild(label);
        container.appendChild(div);
    });
}

function toggleExtraOptions() {
    const extraOptions = document.getElementById('extraOptions');
    const button = document.querySelector('.toggle-options');

    extraOptions.classList.toggle('show');

    if (extraOptions.classList.contains('show')) {
        button.textContent = '➖ Hide Extra Options';
    } else {
        button.textContent = '➕ Extra Options (Title, Date, People Mentioned)';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorDiv.classList.add('show');
}

function hideError() {
    document.getElementById('error').classList.remove('show');
}

async function submitStory(event) {
    event.preventDefault();
    hideError();

    const submitBtn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');

    // Get form values
    const author = document.getElementById('author').value;
    const story = document.getElementById('story').value.trim();
    const title = document.getElementById('title').value.trim() || 'Untitled Story';
    const decade = document.getElementById('decade').value;
    const specificDate = document.getElementById('specificDate').value.trim();
    const otherPeople = document.getElementById('otherPeople').value.trim();

    // Get selected people
    const mentionsCheckboxes = document.querySelectorAll('input[name="mentions"]:checked');
    const mentions = Array.from(mentionsCheckboxes).map(cb => cb.value);

    if (!author) {
        showError('Please select who is sharing this story');
        return;
    }

    if (!story) {
        showError('Please enter your story');
        return;
    }

    // Redirect to GitHub issue creation with pre-filled data
    const githubUrl = buildGitHubIssueUrl({
        title,
        author,
        mentions,
        otherPeople,
        decade,
        specificDate,
        story
    });

    // Redirect to GitHub
    window.location.href = githubUrl;
}

function buildGitHubIssueUrl({ title, author, mentions, otherPeople, decade, specificDate, story }) {
    // Build the issue body that matches the template format
    let body = '### Story Title\n\n' + title + '\n\n';
    body += '### Your Name (Author)\n\n' + author + '\n\n';

    // Who is this story about
    body += '### Who Is This Story About?\n\n';
    if (mentions.length > 0) {
        mentions.forEach(person => {
            body += '- [x] ' + person + '\n';
        });
    } else {
        body += '_No response_\n';
    }
    body += '\n';

    if (otherPeople) {
        body += '### Other People This Story Is About\n\n' + otherPeople + '\n\n';
    } else {
        body += '### Other People This Story Is About\n\n_No response_\n\n';
    }

    body += '### When Did This Story Take Place?\n\n' + (decade || '_No response_') + '\n\n';
    body += '### Specific Date or Year (Optional)\n\n' + (specificDate || '_No response_') + '\n\n';
    body += '### Your Story\n\n' + story + '\n\n';
    body += '### Additional Context (Optional)\n\n_No response_';

    // Redirect to GitHub issue creation with pre-filled body and labels
    const baseUrl = 'https://github.com/patruff/rufftree/issues/new';
    const params = new URLSearchParams({
        title: '[Story] ' + title,
        body: body,
        labels: 'family-story,story:pending'
    });

    return baseUrl + '?' + params.toString();
}

// Initialize
document.getElementById('storyForm').addEventListener('submit', submitStory);
loadFamilyTree();
