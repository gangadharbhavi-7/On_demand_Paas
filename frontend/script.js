// script.js

// API Configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api';

// VM Management Functions
async function createVM(vmConfig) {
    try {
        const response = await fetch(`${API_BASE_URL}/create-vm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(vmConfig)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error creating VM');
        }
        
        const data = await response.json();
        showNotification('Success', 'VM created successfully!');
        updateVMStatus(vmConfig.vmid);
        return data;
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error', error.message);
        throw error;
    }
}

async function getVMStatus(vmid) {
    try {
        const response = await fetch(`${API_BASE_URL}/vm-status/${vmid}`, {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error getting VM status');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

async function deleteVM(vmid, paymentInfo) {
    try {
        const response = await fetch(`${API_BASE_URL}/delete-vm/${vmid}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(paymentInfo)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error deleting VM');
        }
        
        const data = await response.json();
        showNotification('Success', 'VM deleted successfully!');
        document.getElementById('vmStatus').innerHTML = 'VM Deleted';
        return data;
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error', error.message);
        throw error;
    }
}

// Form Handling
document.addEventListener('DOMContentLoaded', function() {
    const vmForm = document.getElementById('vmCreationForm');
    if (vmForm) {
        vmForm.addEventListener('submit', handleVMCreation);
    }

    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactSubmission);
    }

    const deleteForm = document.getElementById('deleteVMForm');
    if (deleteForm) {
        deleteForm.addEventListener('submit', handleVMDeletion);
    }
});

async function handleVMCreation(event) {
    event.preventDefault();
    const form = event.target;
    
    const vmConfig = {
        name: form.vmName.value,
        vmid: parseInt(form.vmId.value),
        memory: parseInt(form.memory.value),
        cores: parseInt(form.cores.value),
        storage: form.storage.value,
        iso: form.iso.value,
        network: form.network.value,
        payment_info: {
            upi_id: form.upiId.value,
            amount: parseFloat(form.amount.value),
            currency: "INR",
            payment_method: "UPI"
        }
    };

    try {
        await createVM(vmConfig);
        form.reset();
        updateVMList();
    } catch (error) {
        console.error('Error creating VM:', error);
    }
}

async function handleVMDeletion(event) {
    event.preventDefault();
    const form = event.target;
    const vmid = parseInt(form.deleteVMId.value);
    const paymentInfo = {
        upi_id: form.deleteUpiId.value,
        amount: parseFloat(form.deleteAmount.value),
        currency: 'INR',
        payment_method: 'UPI'
    };

    try {
        await deleteVM(vmid, paymentInfo);
        form.reset();
        updateVMList();
    } catch (error) {
        console.error('Error deleting VM:', error);
    }
}

async function handleContactSubmission(event) {
    event.preventDefault();
    const form = event.target;
    
    // Basic form validation
    const name = form.name.value.trim();
    const email = form.email.value.trim();
    const message = form.message.value.trim();

    if (!name || !email || !message) {
        showNotification('Error', 'Please fill in all required fields');
        return;
    }

    // Email validation
    if (!isValidEmail(email)) {
        showNotification('Error', 'Please enter a valid email address');
        return;
    }

    showNotification('Success', 'Message sent successfully!');
    form.reset();
}

async function updateVMList() {
    try {
        const response = await fetch(`${API_BASE_URL}/vm-list`, {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch VM list');
        }
        
        const vms = await response.json();
        const vmGrid = document.getElementById('vmGrid');
        
        if (vmGrid) {
            vmGrid.innerHTML = vms.map(vm => `
                <div class="vm-card">
                    <h3>${vm.name}</h3>
                    <p>ID: ${vm.vmid}</p>
                    <p>Status: <span class="vm-status ${vm.status.toLowerCase()}">${vm.status}</span></p>
                    <button onclick="deleteVM(${vm.vmid})" class="delete-btn">Delete</button>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error updating VM list:', error);
        showNotification('Error', 'Failed to update VM list');
    }
}

// Function to update VM status display
async function updateVMStatus(vmid) {
    try {
        const status = await getVMStatus(vmid);
        const statusElement = document.getElementById('vmStatus');
        if (statusElement) {
            statusElement.innerHTML = `
                <h3>VM Status</h3>
                <p>Name: ${status.name || 'N/A'}</p>
                <p>Status: ${status.status || 'N/A'}</p>
                <p>Memory: ${status.mem || 'N/A'} MB</p>
                <p>CPU: ${status.cpu || 'N/A'}%</p>
            `;
        }
    } catch (error) {
        console.error('Error updating VM status:', error);
    }
}

// Utility Functions
function showNotification(type, message) {
    const notification = document.createElement('div');
    notification.className = `notification ${type.toLowerCase()}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Add this to handle VM status updates
setInterval(async function updateVMStatuses() {
    const vmStatusElements = document.querySelectorAll('[data-vm-id]');
    for (const element of vmStatusElements) {
        const vmid = element.dataset.vmId;
        try {
            const status = await getVMStatus(vmid);
            element.textContent = status.status;
            element.className = `vm-status ${status.status.toLowerCase()}`;
        } catch (error) {
            console.error(`Error updating VM ${vmid} status:`, error);
        }
    }
}, 30000); // Update every 30 seconds

// Initialize VM list on page load
document.addEventListener('DOMContentLoaded', updateVMList);