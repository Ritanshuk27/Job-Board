// job-board/static/js/script.js

// Function to filter job listings based on search term and job type
function filterJobs() {
    // Get the search term from the input field, convert to lowercase for case-insensitive matching
    const searchTerm = document.getElementById('searchTerm').value.toLowerCase();
    // Get the selected job type from the dropdown, convert to lowercase
    const filterType = document.getElementById('filterType').value.toLowerCase();
    // Select all elements that represent a job card
    const jobCards = document.querySelectorAll('.job-card');
    let visibleJobCount = 0; // Counter for jobs that match the criteria

    // Loop through each job card
    jobCards.forEach(card => {
        // Retrieve job data from data attributes (e.g., data-title, data-company)
        const title = card.dataset.title;
        const company = card.dataset.company;
        const location = card.dataset.location;
        const description = card.dataset.description;
        const type = card.dataset.type;

        // Check if the job matches the search term in any of the relevant fields
        const matchesSearch = title.includes(searchTerm) ||
                              company.includes(searchTerm) ||
                              location.includes(searchTerm) ||
                              description.includes(searchTerm);

        // Check if the job type matches the selected filter (or if filter is 'all')
        const matchesType = filterType === 'all' || type === filterType;

        // If both search and type criteria are met, display the card
        if (matchesSearch && matchesType) {
            card.style.display = 'flex'; // Use flex to maintain card layout (e.g., for spacing between elements)
            visibleJobCount++; // Increment counter
        } else {
            card.style.display = 'none'; // Hide the card if it doesn't match
        }
    });

    // Update the displayed job count in the header
    document.getElementById('jobCount').textContent = `(${visibleJobCount})`;

    // Get the message elements for no jobs found
    const noFilteredJobsMessage = document.getElementById('noFilteredJobsMessage');
    const noJobsMessage = document.getElementById('noJobsMessage');

    // Show/hide messages based on whether any jobs are visible after filtering
    if (visibleJobCount === 0) {
        noFilteredJobsMessage.classList.remove('hidden'); // Show "No jobs found matching your criteria"
    } else {
        noFilteredJobsMessage.classList.add('hidden'); // Hide it
    }

    // Handle the initial "No jobs found at the moment" message.
    // If there were initially any jobs (even if all are filtered out now), hide this message.
    // This prevents showing two "no jobs" messages simultaneously.
    if (noJobsMessage) {
        if (jobCards.length > 0) {
            noJobsMessage.classList.add('hidden');
        } else {
            noJobsMessage.classList.remove('hidden'); // Show if initial list was empty
        }
    }
}

// Ensure filterJobs runs when the DOM is fully loaded.
// This is important for applying filters if the user navigates back or if initial values are set.
document.addEventListener('DOMContentLoaded', filterJobs);

// You can add more global JavaScript functions here if needed.
// For example, validation functions for forms, dynamic content loading, etc.