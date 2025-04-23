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

// Service Management Functions
async function updateService(serviceId, serviceData) {
    try {
        const response = await fetch(`${API_BASE_URL}/update-service/${serviceId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(serviceData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error updating service');
        }
        
        const data = await response.json();
        showNotification('Success', 'Service updated successfully!');
        return data;
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error', error.message);
        throw error;
    }
}

async function deleteService(serviceId, paymentInfo) {
    try {
        const response = await fetch(`${API_BASE_URL}/delete-service/${serviceId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ service_id: serviceId, payment_info: paymentInfo })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error deleting service');
        }
        
        const data = await response.json();
        showNotification('Success', 'Service deleted successfully!');
        return data;
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error', error.message);
        throw error;
    }
}

// Authentication state
let authToken = localStorage.getItem('authToken');
let currentUser = null;

// Update UI based on authentication state
function updateAuthUI() {
    const loginBtn = document.querySelector('.login-btn');
    const userMenu = document.getElementById('userMenu');
    
    if (authToken) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (userMenu) userMenu.style.display = 'block';
    } else {
        if (loginBtn) loginBtn.style.display = 'block';
        if (userMenu) userMenu.style.display = 'none';
    }
}

// Store authentication token
function storeAuthToken(token) {
    authToken = token;
    localStorage.setItem('authToken', token);
    updateAuthUI();
}

// Remove authentication token
function removeAuthToken() {
    authToken = null;
    localStorage.removeItem('authToken');
    currentUser = null;
    updateAuthUI();
}

// Fetch current user data
async function fetchCurrentUser() {
    try {
        const response = await fetch('/api/users/me', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            updateUserMenu();
        } else {
            removeAuthToken();
        }
    } catch (error) {
        console.error('Error fetching user data:', error);
        removeAuthToken();
    }
}

// Update user menu with current user data
function updateUserMenu() {
    const userMenu = document.getElementById('userMenu');
    if (userMenu && currentUser) {
        userMenu.innerHTML = `
            <div class="user-info">
                <span>${currentUser.name}</span>
                <button onclick="logout()">Logout</button>
            </div>
        `;
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

    const updateServiceForm = document.getElementById('updateServiceForm');
    if (updateServiceForm) {
        updateServiceForm.addEventListener('submit', handleServiceUpdate);
    }

    const deleteServiceForm = document.getElementById('deleteServiceForm');
    if (deleteServiceForm) {
        deleteServiceForm.addEventListener('submit', handleServiceDeletion);
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    updateAuthUI();
    if (authToken) {
        fetchCurrentUser();
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
    const name = form.querySelector('#name').value.trim();
    const email = form.querySelector('#email').value.trim();
    const subject = form.querySelector('#subject').value.trim();
    const message = form.querySelector('#message').value.trim();

    // Validate required fields
    if (!name || !email || !subject || !message) {
        showNotification('Please fill in all required fields.', 'error');
        return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showNotification('Please enter a valid email address.', 'error');
        return;
    }

    try {
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                email,
                subject,
                message
            })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(data.message, 'success');
            form.reset(); // Clear the form on success
        } else {
            showNotification(data.detail || 'Failed to send message. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error submitting contact form:', error);
        showNotification('An error occurred while sending your message. Please try again.', 'error');
    }
}

async function handleServiceUpdate(event) {
    event.preventDefault();
    const form = event.target;
    
    const serviceData = {
        name: form.serviceName.value,
        description: form.serviceDescription.value,
        price: parseFloat(form.servicePrice.value),
        features: form.serviceFeatures.value.split(',').map(feature => feature.trim())
    };

    try {
        const serviceId = parseInt(form.serviceId.value);
        await updateService(serviceId, serviceData);
        form.reset();
        updateServiceList();
    } catch (error) {
        console.error('Error updating service:', error);
    }
}

async function handleServiceDeletion(event) {
    event.preventDefault();
    const form = event.target;
    const serviceId = parseInt(form.deleteServiceId.value);
    const paymentInfo = {
        upi_id: form.deleteUpiId.value,
        amount: parseFloat(form.deleteAmount.value),
        currency: 'INR',
        payment_method: 'UPI'
    };

    try {
        await deleteService(serviceId, paymentInfo);
        form.reset();
        updateServiceList();
    } catch (error) {
        console.error('Error deleting service:', error);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch('/api/login', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            storeAuthToken(data.access_token);
            showNotification('Login successful!', 'success');
            closeLoginModal();
            await fetchCurrentUser();
        } else {
            showNotification(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('An error occurred during login', 'error');
        console.error('Login error:', error);
    }
}

async function handleLogout() {
    removeAuthToken();
    showNotification('Logged out successfully', 'success');
    // Redirect to home page or refresh current page
    window.location.href = '/';
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

async function updateServiceList() {
    try {
        const response = await fetch(`${API_BASE_URL}/service-list`, {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch service list');
        }
        
        const services = await response.json();
        const serviceGrid = document.getElementById('serviceGrid');
        
        if (serviceGrid) {
            serviceGrid.innerHTML = services.map(service => `
                <div class="service-card">
                    <h2>${service.name}</h2>
                    <p>${service.description}</p>
                    <p>Price: ₹${service.price}</p>
                    <ul>
                        ${service.features.map(feature => `<li>${feature}</li>`).join('')}
                    </ul>
                    <div class="service-actions">
                        <button onclick="openUpdateModal(${service.id})" class="update-btn">Update</button>
                        <button onclick="openDeleteModal(${service.id})" class="delete-btn">Delete</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error updating service list:', error);
        showNotification('Error', 'Failed to update service list');
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

// Modal Functions for Service Management
function openUpdateModal(serviceId) {
    const modal = document.getElementById('updateServiceModal');
    if (modal) {
        modal.style.display = 'block';
        // Pre-fill the form with service data
        const service = getServiceById(serviceId);
        if (service) {
            document.getElementById('updateServiceId').value = service.id;
            document.getElementById('updateServiceName').value = service.name;
            document.getElementById('updateServiceDescription').value = service.description;
            document.getElementById('updateServicePrice').value = service.price;
            document.getElementById('updateServiceFeatures').value = service.features.join(', ');
        }
    }
}

function openDeleteModal(serviceId) {
    const modal = document.getElementById('deleteServiceModal');
    if (modal) {
        modal.style.display = 'block';
        document.getElementById('deleteServiceId').value = serviceId;
    }
}

function closeUpdateModal() {
    const modal = document.getElementById('updateServiceModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteServiceModal');
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

// Initialize service list on page load
document.addEventListener('DOMContentLoaded', updateServiceList);

// Service Tier Selection
document.querySelectorAll('.select-tier').forEach(button => {
    button.addEventListener('click', function() {
        const tier = this.dataset.tier;
        const tiers = {
            basic: { cores: 2, memory: 4096, storage: 50 },
            professional: { cores: 4, memory: 8192, storage: 100 },
            enterprise: { cores: 8, memory: 16384, storage: 200 }
        };

        const config = tiers[tier];
        document.getElementById('cores').value = config.cores;
        document.getElementById('memory').value = config.memory;
        document.getElementById('amount').value = tier === 'basic' ? 999 : tier === 'professional' ? 1999 : 3999;

        updateResourceMeters();
        showNotification('Success', `Selected ${tier} tier configuration`);
    });
});

// Resource Meter Updates
function updateResourceMeters() {
    const memory = document.getElementById('memory').value;
    const cores = document.getElementById('cores').value;
    
    // Update memory meter (assuming max 32GB)
    const memoryPercent = (memory / 32768) * 100;
    document.getElementById('memoryMeter').style.width = `${memoryPercent}%`;
    
    // Update cores meter (assuming max 8 cores)
    const coresPercent = (cores / 8) * 100;
    document.getElementById('coresMeter').style.width = `${coresPercent}%`;
}

// Add event listeners for resource inputs
document.getElementById('memory').addEventListener('input', updateResourceMeters);
document.getElementById('cores').addEventListener('input', updateResourceMeters);

// VM Search and Filter
document.getElementById('vmSearch').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    filterVMs();
});

document.getElementById('vmStatusFilter').addEventListener('change', filterVMs);

function filterVMs() {
    const searchTerm = document.getElementById('vmSearch').value.toLowerCase();
    const statusFilter = document.getElementById('vmStatusFilter').value;
    const vmCards = document.querySelectorAll('.vm-card');

    vmCards.forEach(card => {
        const name = card.querySelector('h3').textContent.toLowerCase();
        const status = card.querySelector('.vm-status').textContent.toLowerCase();
        
        const matchesSearch = name.includes(searchTerm);
        const matchesStatus = statusFilter === 'all' || status === statusFilter;
        
        card.style.display = matchesSearch && matchesStatus ? 'block' : 'none';
    });
}

// Enhanced VM Card Creation
function createVMCard(vm) {
    const card = document.createElement('div');
    card.className = 'vm-card';
    card.innerHTML = `
        <div class="vm-header">
            <h3>${vm.name}</h3>
            <span class="vm-status ${vm.status.toLowerCase()}">${vm.status}</span>
        </div>
        <div class="vm-details">
            <p><i class="fas fa-microchip"></i> ${vm.cores} Cores</p>
            <p><i class="fas fa-memory"></i> ${vm.memory}MB RAM</p>
            <p><i class="fas fa-hdd"></i> ${vm.storage}GB Storage</p>
        </div>
        <div class="vm-actions">
            <button class="action-btn start" onclick="startVM(${vm.vmid})">
                <i class="fas fa-play"></i> Start
            </button>
            <button class="action-btn stop" onclick="stopVM(${vm.vmid})">
                <i class="fas fa-stop"></i> Stop
            </button>
            <button class="action-btn delete" onclick="openDeleteModal(${vm.vmid})">
                <i class="fas fa-trash"></i> Delete
            </button>
        </div>
        <div class="vm-resources">
            <div class="resource-bar">
                <label>CPU Usage</label>
                <div class="bar-container">
                    <div class="bar-fill" style="width: ${vm.cpuUsage}%"></div>
                </div>
            </div>
            <div class="resource-bar">
                <label>Memory Usage</label>
                <div class="bar-container">
                    <div class="bar-fill" style="width: ${vm.memoryUsage}%"></div>
                </div>
            </div>
        </div>
    `;
    return card;
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    updateResourceMeters();
    updateVMList();
    
    // Set up auto-refresh for VM status
    setInterval(updateVMList, 30000); // Update every 30 seconds
});