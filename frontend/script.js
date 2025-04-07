const API_BASE_URL = 'http://localhost:8000';

// Function to create a new VM
async function createVM() {
    const vmConfig = {
        name: document.getElementById('vmName').value,
        vmid: parseInt(document.getElementById('vmId').value),
        memory: parseInt(document.getElementById('vmMemory').value),
        cores: parseInt(document.getElementById('vmCores').value),
        storage: document.getElementById('vmStorage').value,
        iso: document.getElementById('vmIso').value,
        network: document.getElementById('vmNetwork').value,
        payment_info: {
            upi_id: document.getElementById('upiId').value,
            amount: parseFloat(document.getElementById('amount').value),
            currency: 'INR',
            payment_method: 'UPI'
        }
    };

    try {
        const response = await fetch(`${API_BASE_URL}/create-vm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(vmConfig)
        });

        const data = await response.json();
        if (response.ok) {
            alert('VM created successfully!');
            updateVMStatus(vmConfig.vmid);
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (error) {
        alert(`Error creating VM: ${error.message}`);
    }
}

// Function to get VM status
async function getVMStatus(vmid) {
    try {
        const response = await fetch(`${API_BASE_URL}/vm-status/${vmid}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error getting VM status:', error);
        return null;
    }
}

// Function to delete a VM
async function deleteVM(vmid) {
    const paymentInfo = {
        upi_id: document.getElementById('deleteUpiId').value,
        amount: parseFloat(document.getElementById('deleteAmount').value),
        currency: 'INR',
        payment_method: 'UPI'
    };

    try {
        const response = await fetch(`${API_BASE_URL}/delete-vm/${vmid}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(paymentInfo)
        });

        const data = await response.json();
        if (response.ok) {
            alert('VM deleted successfully!');
            document.getElementById('vmStatus').innerHTML = 'VM Deleted';
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (error) {
        alert(`Error deleting VM: ${error.message}`);
    }
}

// Function to update VM status display
async function updateVMStatus(vmid) {
    const status = await getVMStatus(vmid);
    if (status) {
        document.getElementById('vmStatus').innerHTML = `
            <h3>VM Status</h3>
            <p>Name: ${status.name}</p>
            <p>Status: ${status.status}</p>
            <p>Memory: ${status.mem} MB</p>
            <p>CPU: ${status.cpu}%</p>
        `;
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('createVMForm').addEventListener('submit', (e) => {
        e.preventDefault();
        createVM();
    });

    document.getElementById('deleteVMForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const vmid = parseInt(document.getElementById('deleteVMId').value);
        deleteVM(vmid);
    });
}); 