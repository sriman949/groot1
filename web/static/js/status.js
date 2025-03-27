document.addEventListener('DOMContentLoaded', function() {
    const podCountElement = document.getElementById('pod-count');
    const deploymentCountElement = document.getElementById('deployment-count');
    const serviceCountElement = document.getElementById('service-count');
    const namespacesTableBody = document.querySelector('#namespaces-table tbody');
    const refreshButton = document.getElementById('refresh-button');

    let podStatusChart = null;
    let socket = null;

    // Initialize WebSocket connection
    function initWebSocket() {
        // Close existing socket if any
        if (socket) {
            socket.close();
        }

        // Create new WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

        // WebSocket event handlers
        socket.onopen = function(e) {
            console.log('WebSocket connection established');
            requestStatusUpdate();
        };

        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);

            if (data.type === 'status_update') {
                updateStatusDisplay(data.status);
            } else if (data.type === 'error') {
                console.error('Error:', data.error);
            }
        };

        socket.onclose = function(event) {
            console.log('WebSocket connection closed');
            // Try to reconnect after a delay
            setTimeout(initWebSocket, 3000);
        };

        socket.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    }

    // Request status update from server
    function requestStatusUpdate() {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'status_update'
            }));
        } else {
            console.error('WebSocket connection is not open');
        }
    }

    // Update status display with data from server
    function updateStatusDisplay(status) {
        // Update counts
        podCountElement.textContent = status.pod_count || 0;
        deploymentCountElement.textContent = status.deployment_count || 0;
        serviceCountElement.textContent = status.service_count || 0;

        // Update pod status chart
        updatePodStatusChart(status.pod_statuses || {});

        // Load namespaces
        loadNamespaces();
    }

    // Update pod status chart
    function updatePodStatusChart(podStatuses) {
        const ctx = document.getElementById('pod-status-chart').getContext('2d');

        // Prepare data for chart
        const labels = Object.keys(podStatuses);
        const data = Object.values(podStatuses);

        // Define colors for different statuses
        const colors = {
            'Running': '#4CAF50',
            'Pending': '#FFC107',
            'Failed': '#F44336',
            'Succeeded': '#2196F3',
            'Unknown': '#9E9E9E'
        };

        const backgroundColor = labels.map(label => colors[label] || '#9E9E9E');

        // Create or update chart
        if (podStatusChart) {
            podStatusChart.data.labels = labels;
            podStatusChart.data.datasets[0].data = data;
            podStatusChart.data.datasets[0].backgroundColor = backgroundColor;
            podStatusChart.update();
        } else {
            podStatusChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: backgroundColor,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    // Load namespaces
    function loadNamespaces() {
        fetch('/api/namespaces')
            .then(response => response.json())
            .then(data => {
                if (data.namespaces) {
                    namespacesTableBody.innerHTML = '';
                    data.namespaces.forEach(namespace => {
                        const row = document.createElement('tr');

                        const nameCell = document.createElement('td');
                        nameCell.textContent = namespace;

                        const statusCell = document.createElement('td');
                        statusCell.innerHTML = '<span class="status-badge active">Active</span>';

                        const ageCell = document.createElement('td');
                        ageCell.textContent = 'Unknown';

                        row.appendChild(nameCell);
                        row.appendChild(statusCell);
                        row.appendChild(ageCell);

                        namespacesTableBody.appendChild(row);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading namespaces:', error);
            });
    }

    // Event listeners
    refreshButton.addEventListener('click', requestStatusUpdate);

    // Initialize
    initWebSocket();
});