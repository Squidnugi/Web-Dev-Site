function toggleAdminCode() {
    var accountType = document.getElementById('account_type').value;
    var adminCodeDiv = document.getElementById('admin_code_div');
    if (accountType === 'admin') {
        adminCodeDiv.style.display = 'block';
    } else {
        adminCodeDiv.style.display = 'none';
    }
}
function updateEmail(type) {
    const selectElement = document.getElementById(`${type}_id`);
    const emailElement = document.getElementById(`${type}_email`);

    if (!selectElement || !emailElement) {
        console.log(`Elements for ${type} not found`);
        return;
    }

    // Check if the select is actually a select element and not a hidden input
    if (selectElement.tagName === 'SELECT') {
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        if (selectedOption && selectedOption.hasAttribute('data-email')) {
            const email = selectedOption.getAttribute('data-email');
            emailElement.value = email;
        } else {
            emailElement.value = '';
        }
    } else {
        // If it's a hidden input (for supervisors editing), the email is already set
        console.log(`${type} is using hidden inputs`);
    }
}

// Create named handler functions that can be properly removed
function handleSupervisorChange() {
    updateEmail('supervisor');
}

function handleClientChange() {
    updateEmail('client');
}

document.addEventListener('DOMContentLoaded', function() {
    // When the modal is fully shown, then update emails
    $('#sessionFormModal').on('shown.bs.modal', function() {
        console.log('Modal shown');

        // Initialize email fields when modal is shown
        updateEmail('supervisor');
        updateEmail('client');

        // Add change listeners
        const supervisorSelect = document.getElementById('supervisor_id');
        if (supervisorSelect) {
            // Remove and add event listeners using named functions
            supervisorSelect.removeEventListener('change', handleSupervisorChange);
            supervisorSelect.addEventListener('change', handleSupervisorChange);
        }

        const clientSelect = document.getElementById('client_id');
        if (clientSelect) {
            // Remove and add event listeners using named functions
            clientSelect.removeEventListener('change', handleClientChange);
            clientSelect.addEventListener('change', handleClientChange);
        }
    });
    // Keep your existing click handlers
    const addSessionBtn = document.getElementById('addSessionBtn');
    if (addSessionBtn) {
        addSessionBtn.addEventListener('click', function() {
            // Reset form for adding a new session
            const form = document.querySelector('#sessionFormModal form');
            form.reset();
            form.action = '/sessions/add';
            document.getElementById('sessionFormModalLabel').textContent = 'Add Session';
            document.getElementById('session_id').value = '';

            // Update button text
            document.getElementById('session-submit-btn').textContent = 'Add Session';

            // Force update of email fields after reset
            setTimeout(function() {
                updateEmail('supervisor');
                updateEmail('client');
            }, 100);
        });
    }

    // For edit buttons
    const editButtons = document.querySelectorAll('.edit-session-btn');
    editButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const sessionId = this.getAttribute('data-session-id');
            document.getElementById('sessionFormModalLabel').textContent = 'Edit Session';
            // You can add AJAX here to load session data if needed
        });
    });
});