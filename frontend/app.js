const API_BASE_URL = "https://ai-powered-it-helpdesk-n0ua.onrender.com";

let currentTicket = null;

async function callAI(endpoint, title, description) {

    const token = localStorage.getItem("token");

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },

            body: JSON.stringify({
                title: title,
                description: description
            })
        }
    );

    const text = await response.text();

    console.log("AI Endpoint:", endpoint);
    console.log("HTTP Status:", response.status);
    console.log("Raw response:", text);

    if (!response.ok) {

        let errorMessage = "AI request failed";

        try {
            const errorData = JSON.parse(text);
            errorMessage = errorData.detail || errorMessage;
        } catch (error) {
            if (text) {
                errorMessage = text;
            }
        }

        throw new Error(
            `AI request failed (${response.status}): ${errorMessage}`
        );
    }

    if (!text.trim()) {
        throw new Error("AI server returned an empty response.");
    }

    try {
        return JSON.parse(text);
    } catch (error) {
        console.error("Invalid JSON:", text);
        throw new Error("AI server returned invalid JSON.");
    }
}

// ===============================
// LOGIN
// ===============================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const message = document.getElementById("message");

        message.textContent = "Logging in...";
        message.style.color = "blue";

        const formData = new URLSearchParams();

        formData.append("username", email);
        formData.append("password", password);

        try {

            const response = await fetch(
                `${API_BASE_URL}/login`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: formData
                }
            );

            console.log("STATUS:", response.status);
            console.log("OK:", response.ok);

            const responseText = await response.text();

            console.log("RAW RESPONSE:", responseText);

            if (!response.ok) {

                let errorMessage = "Invalid credentials";

                try {

                    const errorData = JSON.parse(responseText);

                    console.log("ERROR DATA:", errorData);

                    if (errorData.detail) {
                        errorMessage = errorData.detail;
                    }

                } catch (error) {

                    console.log("Response was not JSON.");

                }

                message.textContent = errorMessage;
                message.style.color = "red";

                return;
            }

            const data = JSON.parse(responseText);

            console.log("LOGIN DATA:", data);

            localStorage.setItem(
                "token",
                data.access_token
            );

            localStorage.setItem(
                "role",
                data.role
            );

            localStorage.setItem(
                "user_id",
                data.user_id
            );

            message.textContent = "Login successful!";
            message.style.color = "green";

            if (data.role === "admin") {

                window.location.href = "admin-dashboard.html";

            } else if (data.role === "agent") {

                window.location.href = "agent-dashboard.html";

            } else if (data.role === "employee") {

                window.location.href = "dashboard.html";

            } else {

                message.textContent = "Unknown user role.";
                message.style.color = "red";

            }

        } catch (error) {

            console.error("LOGIN ERROR:", error);

            message.textContent =
                "Cannot connect to the server.";

            message.style.color = "red";
        }

    });

}


// ===============================
// DASHBOARD
// ===============================

async function loadDashboard() {

    const token = localStorage.getItem("token");

    if (!token) {

        window.location.href = "login.html";

        return;
    }

    try {

        // Get dashboard statistics

        const statsResponse = await fetch(
            `${API_BASE_URL}/dashboard/stats`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const stats = await statsResponse.json();

        document.getElementById("totalTickets").textContent =
    stats.total_tickets;

    document.getElementById("openTickets").textContent =
        stats.open_tickets;

    document.getElementById("progressTickets").textContent =
        stats.in_progress_tickets;

    document.getElementById("resolvedTickets").textContent =
        stats.resolved_tickets;


        // Get tickets

        const ticketsResponse = await fetch(
            `${API_BASE_URL}/tickets`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const tickets = await ticketsResponse.json();

        // Display tickets

        const ticketTable =
            document.getElementById("ticketTable");

        if (ticketTable && Array.isArray(tickets)) {

            ticketTable.innerHTML = "";

            tickets.forEach(ticket => {

                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${ticket.id}</td>
                    <td>
                        <a href="ticket.html?id=${ticket.id}">
                            ${ticket.title}
                        </a>
                    </td>
                    <td>${ticket.priority}</td>
                    <td>${ticket.status}</td>
                `;

                ticketTable.appendChild(row);

            });

        }

    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

    }

}


// ===============================
// LOGOUT
// ===============================

function logout() {

    localStorage.removeItem("token");

    localStorage.removeItem("role");

    localStorage.removeItem("user_id");

    window.location.href = "login.html";

}


// ===============================
// START DASHBOARD
// ===============================

const currentPage = window.location.pathname
    .split("/")
    .pop();

if (currentPage === "dashboard.html") {
    loadDashboard();
}


// ===============================
// TICKET DETAILS
// ===============================

async function loadTicket() {

    const ticketDetails =
    document.getElementById("ticketDetails");

    if (!ticketDetails) {
        return;
    }

    const token = localStorage.getItem("token");

    if (!token) {

        window.location.href = "login.html";

        return;
    }

    const params = new URLSearchParams(
        window.location.search
    );

    const ticketId = params.get("id");

    if (!ticketId) {

        ticketDetails.innerHTML =
            "<p>Ticket ID not found.</p>";

        return;
    }

    try {

        const response = await fetch(
            `${API_BASE_URL}/tickets/${ticketId}`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const ticket = await response.json();
        currentTicket = ticket;

        if (!response.ok) {

            ticketDetails.innerHTML =
                `<p>${ticket.detail || "Ticket not found."}</p>`;

            return;
        }

        ticketDetails.innerHTML = `

            <div class="ticket-card">

                <h3>${ticket.title}</h3>

                <p>
                    <strong>Ticket ID:</strong>
                    ${ticket.id}
                </p>

                <p>
                    <strong>Description:</strong>
                    ${ticket.description}
                </p>

                <p>
                    <strong>Category:</strong>
                    ${ticket.category}
                </p>

                <p>
                    <strong>Priority:</strong>
                    ${ticket.priority}
                </p>

                <p>
                    <strong>Status:</strong>
                    ${ticket.status}
                </p>

                <p>
                    <strong>Created:</strong>
                    ${ticket.created_at}
                </p>

            </div>

        `;

        // Display recommended solution
        const solutionElement =
            document.getElementById("recommendedSolution");

        if (solutionElement) {

            if (ticket.recommended_solution) {

                solutionElement.innerHTML = `

                    <div class="solution-card">

                        <p>
                            ${ticket.recommended_solution}
                        </p>

                    </div>

                `;

            } else {

                solutionElement.innerHTML =
                    "<p>No recommended solution available.</p>";

            }
        }

        showAgentActions(ticket.status);        

    } catch (error) {

        console.error(
            "Ticket error:",
            error
        );

        document.getElementById("ticketDetails").innerHTML =
            "<p>Unable to load ticket.</p>";

    }

}


// Load ticket page

if (
    window.location.pathname.includes("ticket.html")
) {

    loadTicket();

}



// ===============================
// COMMENTS
// ===============================

async function loadComments(ticketId) {

    const token = localStorage.getItem("token");

    const commentsList =
        document.getElementById("commentsList");

    try {

        const response = await fetch(
            `${API_BASE_URL}/tickets/${ticketId}/comments`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const comments = await response.json();

        if (!response.ok) {

            commentsList.innerHTML =
                `<p>${comments.detail || "Unable to load comments."}</p>`;

            return;
        }

        commentsList.innerHTML = "";

        if (comments.length === 0) {

            commentsList.innerHTML =
                "<p>No comments yet.</p>";

            return;
        }

        comments.forEach(comment => {

            const div = document.createElement("div");

            div.className = "comment-card";

            div.innerHTML = `
                <p>
                    <strong>User:</strong>
                    ${comment.name}
                </p>

                <p>
                    ${comment.comment}
                </p>

                <p class="comment-date">
                    ${comment.created_at}
                </p>
            `;

            commentsList.appendChild(div);

        });

    } catch (error) {

        console.error(
            "Comments error:",
            error
        );

        commentsList.innerHTML =
            "<p>Unable to load comments.</p>";
    }
}


// ===============================
// ADD COMMENT
// ===============================

const commentForm =
    document.getElementById("commentForm");

if (commentForm) {

    commentForm.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();

            const token =
                localStorage.getItem("token");

            const params =
                new URLSearchParams(
                    window.location.search
                );

            const ticketId =
                params.get("id");

            const comment =
                document.getElementById("comment").value;

            const message =
                document.getElementById("commentMessage");

            try {

                const response = await fetch(
                    `${API_BASE_URL}/tickets/${ticketId}/comments`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json",

                            "Authorization":
                                `Bearer ${token}`
                        },

                        body: JSON.stringify({
                            comment: comment
                        })
                    }
                );

                const data =
                    await response.json();

                if (response.ok) {

                    message.textContent =
                        "Comment added successfully.";

                    document.getElementById(
                        "comment"
                    ).value = "";

                    loadComments(ticketId);

                } else {

                    message.textContent =
                        data.detail ||
                        "Unable to add comment.";

                }

            } catch (error) {

                console.error(
                    "Add comment error:",
                    error
                );

                message.textContent =
                    "Unable to connect to server.";

            }

        }
    );

}


// ===============================
// TICKET HISTORY
// ===============================

async function loadHistory(ticketId) {

    const token =
        localStorage.getItem("token");

    const historyList =
        document.getElementById("historyList");

    try {

        const response = await fetch(
            `${API_BASE_URL}/tickets/${ticketId}/history`,
            {
                headers: {
                    "Authorization":
                        `Bearer ${token}`
                }
            }
        );

        const history =
            await response.json();

        if (!response.ok) {

            historyList.innerHTML =
                `<p>${history.detail || "Unable to load history."}</p>`;

            return;
        }

        historyList.innerHTML = "";

        if (history.length === 0) {

            historyList.innerHTML =
                "<p>No history available.</p>";

            return;
        }

        history.forEach(item => {

            const div =
                document.createElement("div");

            div.className =
                "history-item";

            div.innerHTML = `
                <p>
                    <strong>Action:</strong>
                    ${item.action}
                </p>

                <p>
                    <strong>Old Value:</strong>
                    ${item.old_value || "-"}
                </p>

                <p>
                    <strong>New Value:</strong>
                    ${item.new_value || "-"}
                </p>

                <p>
                    <strong>User:</strong>
                    ${item.name}
                </p>

                <p class="comment-date">
                    ${item.created_at}
                </p>
            `;

            historyList.appendChild(div);

        });

    } catch (error) {

        console.error(
            "History error:",
            error
        );

        historyList.innerHTML =
            "<p>Unable to load history.</p>";
    }

}


// ===============================
// LOAD COMMENTS + HISTORY
// ===============================

if (
    window.location.pathname.includes("ticket.html")
) {

    const params =
        new URLSearchParams(
            window.location.search
        );

    const ticketId =
        params.get("id");

    if (ticketId) {

        loadComments(ticketId);

        loadHistory(ticketId);

    }

}



const ticketForm =
    document.getElementById("ticketForm");

if (ticketForm) {

    ticketForm.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();

            const token =
                localStorage.getItem("token");

            const userId =
                localStorage.getItem("user_id");

            const title =
                document.getElementById("title").value;

            const description =
                document.getElementById("description").value;

            const message =
                document.getElementById("ticketMessage");

            if (!token || !userId) {

                window.location.href =
                    "login.html";

                return;
            }

            try {

                const response = await fetch(
                    `${API_BASE_URL}/tickets`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json",
                            "Authorization":
                                `Bearer ${token}`
                        },

                        body: JSON.stringify({
                            title: title,
                            description: description,
                            user_id: Number(userId)
                        })
                    }
                );

                const data =
                    await response.json();

                if (response.ok) {

                    message.textContent =
                        "Ticket created successfully!";

                    document.getElementById(
                        "ticketForm"
                    ).reset();

                    setTimeout(
                        function() {
                            window.location.href =
                                "dashboard.html";
                        },
                        1000
                    );

                } else {

                    message.textContent =
                        data.detail ||
                        "Unable to create ticket.";

                }

            } catch (error) {

                console.error(
                    "Create ticket error:",
                    error
                );

                message.textContent =
                    "Unable to connect to server.";
            }
        }
    );

}


const registerForm =
    document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();

            const name =
                document.getElementById("name").value;

            const email =
                document.getElementById("email").value;

            const password =
                document.getElementById("password").value;

            const message =
                document.getElementById("registerMessage");

            try {

                const response = await fetch(
                    `${API_BASE_URL}/register`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            name: name,
                            email: email,
                            password: password
                        })
                    }
                );

                const data =
                    await response.json();

                if (response.ok) {

                    message.textContent =
                        "Registration successful!";

                    document.getElementById(
                        "registerForm"
                    ).reset();

                    setTimeout(
                        function() {
                            window.location.href =
                                "login.html";
                        },
                        1000
                    );

                } else {

                    message.textContent =
                        data.detail ||
                        "Registration failed.";

                }

            } catch (error) {

                console.error(
                    "Registration error:",
                    error
                );

                message.textContent =
                    "Unable to connect to server.";
            }

        }
    );

}


async function loadAgentDashboard() {

    const token =
        localStorage.getItem("token");

    const role =
        localStorage.getItem("role");

    if (!token) {

        window.location.href =
            "login.html";

        return;
    }

    // Only agents can access this page

    if (role !== "agent") {
        window.location.href = "login.html";
        return;
    }


    try {

        const response = await fetch(
            `${API_BASE_URL}/tickets`,
            {
                headers: {
                    "Authorization":
                        `Bearer ${token}`
                }
            }
        );


        const tickets =
            await response.json();

        if (!response.ok) {

            console.error(
                "Unable to load tickets:",
                tickets
            );

            return;
        }


        const ticketTable =
            document.getElementById(
                "agentTicketTable"
            );


        ticketTable.innerHTML = "";


        if (!Array.isArray(tickets) ||
            tickets.length === 0) {

            ticketTable.innerHTML = `
                <tr>
                    <td colspan="5">
                        No assigned tickets found.
                    </td>
                </tr>
            `;

            updateAgentStats([]);

            return;
        }


        tickets.forEach(ticket => {

            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>
                    ${ticket.id}
                </td>

                <td>
                    <a href="ticket.html?id=${ticket.id}">
                        ${ticket.title}
                    </a>
                </td>

                <td>
                    ${ticket.category}
                </td>

                <td>
                    ${ticket.priority}
                </td>

                <td>
                    ${ticket.status}
                </td>

            `;


            ticketTable.appendChild(row);

        });


        updateAgentStats(tickets);


    } catch (error) {

        console.error(
            "Agent dashboard error:",
            error
        );

    }

}


function updateAgentStats(tickets) {

    const total =
        tickets.length;


    const open =
        tickets.filter(
            ticket =>
                ticket.status === "Open"
        ).length;


    const inProgress =
        tickets.filter(
            ticket =>
                ticket.status === "In Progress"
        ).length;


    const resolved =
        tickets.filter(
            ticket =>
                ticket.status === "Resolved"
        ).length;


    document.getElementById(
        "assignedTickets"
    ).textContent = total;


    document.getElementById(
        "openTickets"
    ).textContent = open;


    document.getElementById(
        "progressTickets"
    ).textContent = inProgress;


    document.getElementById(
        "resolvedTickets"
    ).textContent = resolved;

}

if (
    window.location.pathname.includes(
        "agent-dashboard.html"
    )
) {

    loadAgentDashboard();

}


function showAgentActions(ticketStatus) {

    const role =
        localStorage.getItem("role");

    if (role !== "agent") {
        return;
    }

    const agentActions =
        document.getElementById("agentActions");

    if (!agentActions) {
        return;
    }

    agentActions.style.display = "block";

    document.getElementById(
        "ticketStatus"
    ).value = ticketStatus;
}


const updateStatusButton =
    document.getElementById(
        "updateStatusButton"
    );

if (updateStatusButton) {

    updateStatusButton.addEventListener(
        "click",
        async function() {

            const token =
                localStorage.getItem("token");

            const params =
                new URLSearchParams(
                    window.location.search
                );

            const ticketId =
                params.get("id");

            const status =
                document.getElementById(
                    "ticketStatus"
                ).value;

            const resolution =
                document.getElementById(
                    "ticketResolution"
                ).value;

            const message =
                document.getElementById(
                    "statusMessage"
                );

            try {

                const response = await fetch(
                    `${API_BASE_URL}/tickets/${ticketId}/status`,
                    {
                        method: "PUT",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Authorization":
                                `Bearer ${token}`
                        },

                        body: JSON.stringify({
                            status: status,
                            resolution: resolution
                        })
                    }
                );

                const data =
                    await response.json();

                if (response.ok) {

                    message.textContent =
                        "Status and resolution updated successfully.";

                    loadTicket();
                    loadHistory(ticketId);

                } else {

                    message.textContent =
                        data.detail ||
                        "Unable to update ticket.";

                }

            } catch (error) {

                console.error(
                    "Status update error:",
                    error
                );

                message.textContent =
                    "Unable to connect to server.";

            }

        }
    );

}

async function loadAdminDashboard() {

    const token =
        localStorage.getItem("token");

    const role =
        localStorage.getItem("role");

    if (!token) {

        window.location.href =
            "login.html";

        return;
    }

    if (role !== "admin") {

        window.location.href =
            "dashboard.html";

        return;
    }


    try {

        // =========================
        // LOAD TICKETS
        // =========================

        const ticketResponse =
            await fetch(
                `${API_BASE_URL}/tickets`,
                {
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );

        adminTickets =
            await ticketResponse.json();

        const tickets =
            adminTickets;

        if (!ticketResponse.ok) {

            console.error(
                "Unable to load tickets:",
                tickets
            );

            return;
        }


        // =========================
        // UPDATE STATISTICS
        // =========================

        document.getElementById(
            "adminTotalTickets"
        ).textContent = tickets.length;


        const openTickets =
            tickets.filter(
                ticket =>
                    ticket.status === "Open"
            ).length;


        const progressTickets =
            tickets.filter(
                ticket =>
                    ticket.status === "In Progress"
            ).length;


        const resolvedTickets =
            tickets.filter(
                ticket =>
                    ticket.status === "Resolved"
            ).length;


        document.getElementById(
            "adminOpenTickets"
        ).textContent =
            openTickets;


        document.getElementById(
            "adminProgressTickets"
        ).textContent =
            progressTickets;


        document.getElementById(
            "adminResolvedTickets"
        ).textContent =
            resolvedTickets;


        // =========================
        // DISPLAY TICKETS
        // =========================

        displayAdminTickets(
            adminTickets
        );


        // =========================
        // LOAD USERS
        // =========================

        const userResponse =
            await fetch(
                `${API_BASE_URL}/admin/users`,
                {
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        const users =
            await userResponse.json();

        if (!userResponse.ok) {

            console.error(
                "Unable to load users:",
                users
            );

            return;
        }


        // =========================
        // DISPLAY USERS
        // =========================

        const userTable =
            document.getElementById(
                "adminUserTable"
            );


        userTable.innerHTML = "";


        users.forEach(user => {

            const row =
                document.createElement("tr");


            row.innerHTML = `
                <td>${user.id}</td>

                <td>${user.name}</td>

                <td>${user.email}</td>

                <td>${user.role}</td>

                <td>${user.created_at}</td>
            `;


            userTable.appendChild(row);

        });

    } catch (error) {

        console.error(
            "Admin dashboard error:",
            error
        );

    }
}


// =========================
// ADMIN DASHBOARD START
// =========================
let adminTickets = [];

if (
    window.location.pathname.includes(
        "admin-dashboard.html"
    )
) {

    loadAdminDashboard();

}

function displayAdminTickets(tickets) {

    const ticketTable =
        document.getElementById(
            "adminTicketTable"
        );

    if (!ticketTable) {
        return;
    }

    ticketTable.innerHTML = "";

    if (tickets.length === 0) {

        ticketTable.innerHTML = `
            <tr>
                <td colspan="8">
                    No tickets match the filters.
                </td>
            </tr>
        `;

        return;
    }

    tickets.forEach(ticket => {

        const row =
            document.createElement("tr");

        row.innerHTML = `
            <td>${ticket.id}</td>

            <td>
                <a href="ticket.html?id=${ticket.id}">
                    ${ticket.title}
                </a>
            </td>

            <td>${ticket.category}</td>

            <td>${ticket.priority}</td>

            <td>${ticket.status}</td>

            <td>${ticket.user_id}</td>

            <td>
                ${ticket.assigned_to || "Unassigned"}
            </td>

            <td>
                <button
                    onclick="selectTicketForAssignment(${ticket.id})"
                >
                    Assign
                </button>
            </td>
        `;

        ticketTable.appendChild(row);

    });
}

function filterAdminTickets() {

    const search =
        document.getElementById(
            "ticketSearch"
        ).value.toLowerCase();

    const status =
        document.getElementById(
            "statusFilter"
        ).value;

    const priority =
        document.getElementById(
            "priorityFilter"
        ).value;
    
    const agent =
        document.getElementById(
            "agentFilter"
    ).value;


    const filteredTickets =
        adminTickets.filter(ticket => {

            const matchesSearch =
                ticket.title
                    .toLowerCase()
                    .includes(search);

            const matchesStatus =
                !status ||
                ticket.status === status;

            const matchesPriority =
                !priority ||
                ticket.priority === priority;

            const matchesAgent =
                !agent ||
                String(ticket.assigned_to) === String(agent);

            return (
                matchesSearch &&
                matchesStatus &&
                matchesPriority &&
                matchesAgent
            );

        });


    displayAdminTickets(
        filteredTickets
    );
}

const ticketSearch =
    document.getElementById(
        "ticketSearch"
    );

const statusFilter =
    document.getElementById(
        "statusFilter"
    );

const priorityFilter =
    document.getElementById(
        "priorityFilter"
    );

const agentFilter =
    document.getElementById(
        "agentFilter"
    );

const clearFilters =
    document.getElementById(
        "clearFilters"
    );


if (ticketSearch) {

    ticketSearch.addEventListener(
        "input",
        filterAdminTickets
    );

}


if (statusFilter) {

    statusFilter.addEventListener(
        "change",
        filterAdminTickets
    );

}


if (priorityFilter) {

    priorityFilter.addEventListener(
        "change",
        filterAdminTickets
    );

}

if (agentFilter) {

    agentFilter.addEventListener(
        "change",
        filterAdminTickets
    );

}


if (clearFilters) {

    clearFilters.addEventListener(
        "click",
        function() {

            ticketSearch.value = "";
            statusFilter.value = "";
            priorityFilter.value = "";
            agentFilter.value = "";

            displayAdminTickets(
                adminTickets
            );

        }
    );

}


async function loadAssignmentData() {

    const token =
        localStorage.getItem("token");

    const ticketSelect =
        document.getElementById(
            "assignmentTicket"
        );

    const agentSelect =
        document.getElementById(
            "assignmentAgent"
        );

    if (!token || !ticketSelect || !agentSelect) {
        return;
    }


    try {

        // =========================
        // LOAD ALL TICKETS
        // =========================

        const ticketResponse =
            await fetch(
                `${API_BASE_URL}/tickets`,
                {
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        adminTickets =
            await ticketResponse.json();

        const tickets =
            adminTickets; 


        if (!ticketResponse.ok) {
            console.error(
                "Unable to load tickets:",
                tickets
            );
            return;
        }


        ticketSelect.innerHTML = `
            <option value="">
                Select Ticket
            </option>
        `;


        tickets.forEach(ticket => {

            const option =
                document.createElement("option");

            option.value = ticket.id;

            option.textContent =
                `#${ticket.id} - ${ticket.title}`;

            ticketSelect.appendChild(option);

        });


        // =========================
        // LOAD USERS
        // =========================

        const userResponse =
            await fetch(
                `${API_BASE_URL}/admin/users`,
                {
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        const users =
            await userResponse.json();


        if (!userResponse.ok) {
            console.error(
                "Unable to load users:",
                users
            );
            return;
        }


        agentSelect.innerHTML = `
            <option value="">
                Select Agent
            </option>
        `;


        users
            .filter(user => user.role === "agent")
            .forEach(agent => {

                const option =
                    document.createElement("option");

                option.value = agent.id;

                option.textContent =
                    `${agent.name} (${agent.email})`;

                agentSelect.appendChild(option);

            });


    } catch (error) {

        console.error(
            "Assignment data error:",
            error
        );

    }
}

const assignTicketButton =
    document.getElementById(
        "assignTicketButton"
    );

if (assignTicketButton) {

    assignTicketButton.addEventListener(
        "click",
        async function() {

            const token =
                localStorage.getItem("token");

            const ticketId =
                document.getElementById(
                    "assignmentTicket"
                ).value;

            const agentId =
                document.getElementById(
                    "assignmentAgent"
                ).value;

            const message =
                document.getElementById(
                    "assignmentMessage"
                );


            if (!ticketId) {

                message.textContent =
                    "Please select a ticket.";

                return;
            }


            if (!agentId) {

                message.textContent =
                    "Please select an agent.";

                return;
            }


            try {

                const response =
                    await fetch(
                        `${API_BASE_URL}/tickets/${ticketId}/assign`,
                        {
                            method: "PUT",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Authorization":
                                    `Bearer ${token}`
                            },

                            body: JSON.stringify({
                                assigned_to:
                                    Number(agentId)
                            })
                        }
                    );


                const data =
                    await response.json();

                if (response.ok) {

                    message.textContent =
                        "Ticket assigned successfully.";

                    // Refresh ticket table
                    loadAdminDashboard();

                    // Clear selections
                    document.getElementById(
                        "assignmentTicket"
                    ).value = "";

                    document.getElementById(
                        "assignmentAgent"
                    ).value = "";

                } else {

                    message.textContent =
                        data.detail ||
                        "Unable to assign ticket.";
                }


            } catch (error) {

                console.error(
                    "Assignment error:",
                    error
                );

                message.textContent =
                    "Unable to connect to server.";

            }

        }
    );
}

if (
    window.location.pathname.includes(
        "admin-dashboard.html"
    )
) {

    loadAssignmentData();
    loadAgentFilter();

}


function selectTicketForAssignment(ticketId) {

    const ticketSelect =
        document.getElementById(
            "assignmentTicket"
        );

    if (!ticketSelect) {
        return;
    }

    ticketSelect.value = ticketId;

    // Scroll to the assignment section
    ticketSelect.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

}

async function loadAgentFilter() {

    const token =
        localStorage.getItem("token");

    if (!token || !agentFilter) {
        return;
    }

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/admin/users`,
                {
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );

        const users =
            await response.json();

        if (!response.ok) {
            console.error(
                "Unable to load agents:",
                users
            );
            return;
        }

        agentFilter.innerHTML = `
            <option value="">
                All Agents
            </option>
        `;

        users
            .filter(user => user.role === "agent")
            .forEach(agent => {

                const option =
                    document.createElement("option");

                option.value = agent.id;

                option.textContent =
                    agent.name;

                agentFilter.appendChild(option);

            });

    } catch (error) {

        console.error(
            "Agent filter error:",
            error
        );

    }
}


document
    .getElementById("aiClassifyButton")
    ?.addEventListener("click", async () => {

        try {

            document.getElementById("aiStatus").textContent =
                "AI is classifying the ticket...";

            const data = await callAI(
                "/ai/classify",
                currentTicket.title,
                currentTicket.description
            );

            document.getElementById("aiClassifyResult").innerHTML = `
                <h3>Classification</h3>
                <p><strong>Category:</strong> ${data.category}</p>
                <p><strong>Priority:</strong> ${data.priority}</p>
            `;

            document.getElementById("aiStatus").textContent =
                "Classification completed.";

        } catch (error) {

            document.getElementById("aiStatus").textContent =
                error.message;

        }

    });


    document
    .getElementById("aiSummarizeButton")
    ?.addEventListener("click", async () => {

        try {

            document.getElementById("aiStatus").textContent =
                "Generating summary...";

            const data = await callAI(
                "/ai/summarize",
                currentTicket.title,
                currentTicket.description
            );

            document.getElementById("aiSummarizeResult").innerHTML = `
                <h3>AI Summary</h3>
                <p>${data.summary}</p>
            `;

            document.getElementById("aiStatus").textContent =
                "Summary generated.";

        } catch (error) {

            document.getElementById("aiStatus").textContent =
                error.message;

        }

    });


  document
    .getElementById("aiRecommendButton")
    ?.addEventListener("click", async () => {

        try {

            document.getElementById("aiStatus").textContent =
                "Finding recommended solution...";

            const data = await callAI(
                "/ai/recommend",
                currentTicket.title,
                currentTicket.description
            );

            document.getElementById("aiRecommendResult").innerHTML = `
                <h3>Recommended Solution</h3>
                <p>${data.solution}</p>
            `;

            document.getElementById("aiStatus").textContent =
                "Solution generated.";

        } catch (error) {

            document.getElementById("aiStatus").textContent =
                error.message;

        }

    });
    
    
    document
    .getElementById("aiSimilarButton")
    ?.addEventListener("click", async () => {

        try {

            document.getElementById("aiStatus").textContent =
                "Searching similar tickets...";

            const data = await callAI(
                "/ai/similar",
                currentTicket.title,
                currentTicket.description
            );

            let html = "<h3>Similar Tickets</h3>";

            if (data.similar_tickets.length === 0) {

                html += "<p>No similar tickets found.</p>";

            } else {

                data.similar_tickets.forEach(ticket => {

                    html += `
                        <div class="ai-ticket-card">

                            <strong>
                                Ticket #${ticket.ticket_id}
                            </strong>

                            <p>${ticket.title}</p>

                            <p>
                                Similarity:
                                ${ticket.similarity}
                            </p>

                            <p>
                                Resolution:
                                ${ticket.resolution || "N/A"}
                            </p>

                        </div>
                    `;

                });

            }

            document.getElementById("aiSimilarResult").innerHTML = html;

            document.getElementById("aiStatus").textContent =
                "Similar ticket search completed.";

        } catch (error) {

            document.getElementById("aiStatus").textContent =
                error.message;

        }

    });


    document
    .getElementById("aiSemanticButton")
    ?.addEventListener("click", async () => {

        console.log("SEMANTIC SEARCH STARTED");

        try {

            document.getElementById("aiStatus").textContent =
                "Searching semantically...";

            if (!currentTicket) {
                throw new Error("No ticket is currently loaded.");
            }

            const data = await callAI(
                "/ai/semantic-search",
                currentTicket.title,
                currentTicket.description
            );

            console.log("Semantic Search Data:", data);

            let html = "<h3>Semantic Search Results</h3>";

            if (
                !data.semantic_results ||
                data.semantic_results.length === 0
            ) {

                html += `
                    <div class="ai-ticket-card">
                        <p>No semantically similar tickets found.</p>
                    </div>
                `;

            } else {

                data.semantic_results.forEach(ticket => {

                    html += `
                        <div class="ai-ticket-card">

                            <strong>
                                Ticket #${ticket.ticket_id}
                            </strong>

                            <p>
                                <strong>${ticket.title}</strong>
                            </p>

                            <p>
                                ${ticket.description}
                            </p>

                            <p>
                                <strong>Similarity:</strong>
                                ${(ticket.similarity * 100).toFixed(1)}%
                            </p>

                            <p>
                                <strong>Resolution:</strong>
                                ${ticket.resolution || "N/A"}
                            </p>

                        </div>
                    `;

                });

            }

            document.getElementById("aiSemanticResult").innerHTML =
                html;

            document.getElementById("aiStatus").textContent =
                "Semantic search completed.";

        } catch (error) {

            console.error("Semantic Search Error:", error);

            document.getElementById("aiStatus").textContent =
                error.message;

        }

    });


    document
    .getElementById("aiRagButton")
    ?.addEventListener("click", async () => {

        try {

            document.getElementById("aiStatus").textContent =
                "Generating RAG solution...";

            const data = await callAI(
                "/ai/rag",
                currentTicket.title,
                currentTicket.description
            );

            const aiSolution = data.ai_solution || {};

            let html = `
                <h3>AI RAG Solution</h3>

                <div class="ai-ticket-card">

                    <p>
                        <strong>Status:</strong>
                        ${aiSolution.status || "Unknown"}
                    </p>

                    <p>
                        <strong>Solution:</strong>
                    </p>

                    <p>
                        ${aiSolution.solution || "No solution available."}
                    </p>

                </div>

                <h4>Supporting Tickets</h4>
            `;

            if (
                data.similar_tickets &&
                data.similar_tickets.length > 0
            ) {

                data.similar_tickets.forEach(ticket => {

                    html += `
                        <div class="ai-ticket-card">

                            <strong>
                                Ticket #${ticket.ticket_id}
                            </strong>

                            <p>
                                <strong>${ticket.title}</strong>
                            </p>

                            <p>
                                ${ticket.description}
                            </p>

                            <p>
                                <strong>Similarity:</strong>
                                ${(ticket.similarity * 100).toFixed(1)}%
                            </p>

                            ${
                                ticket.resolution
                                    ? `
                                        <p>
                                            <strong>Previous Resolution:</strong>
                                            ${ticket.resolution}
                                        </p>
                                      `
                                    : ""
                            }

                        </div>
                    `;

                });

            } else {

                html += `
                    <div class="ai-ticket-card">
                        <p>
                            No sufficiently similar resolved tickets
                            were found.
                        </p>
                    </div>
                `;

            }

            document.getElementById("aiRagResult").innerHTML =
                html;

            document.getElementById("aiStatus").textContent =
                "RAG solution generated.";

        } catch (error) {

            console.error("RAG Error:", error);

            document.getElementById("aiStatus").textContent =
                error.message;

        }

    });