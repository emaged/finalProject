document.addEventListener("DOMContentLoaded", () => {
    // check if csrf-token exists
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (!meta) return;
    const csrfToken = meta.getAttribute("content");

    const urlCheck = document.querySelector("#file-route-btn");
    const indexUrlCheck =
        document.querySelector("#index-route-btn").dataset.fileRoute;
    // Only run sidebar logic on pages that include #file-route-btn
    if (!urlCheck) return;
    const selectUrl = urlCheck.dataset.fileRoute;

    function select_db_listener() {
        document.querySelectorAll(".file-btn").forEach((btn) => {
            btn.addEventListener("click", async () => {
                try {
                    const selectedFile = btn.dataset.file;
                    const formData = new FormData();
                    formData.append("selected_file", selectedFile);

                    // Send selected file to Flask to update session
                    const response = await fetch(selectUrl, {
                        method: "POST",
                        headers: { "X-CSRFToken": csrfToken },
                        body: formData,
                    });

                    if (!response.ok) {
                        throw new Error(
                            `HTTP ${response.status} - ${response.statusText}`,
                        );
                    }

                    // remove active class from all buttons
                    document.querySelectorAll(".file-btn").forEach((b) => {
                        b.classList.remove("active");
                    });
                    // Add active class to clicked button
                    btn.classList.add("active");

                    const data = await response.json();

                    const container =
                        document.getElementById("dashboard-collapse");
                    container.innerHTML = "";

                    data.forEach((schema) => {
                        const button = document.createElement("button");
                        button.className = "btn p-0 border-0 btn-schema";
                        button.dataset.fileRoute = indexUrlCheck;
                        button.value = schema.name;
                        const table = document.createElement("table");
                        table.className =
                            "table table-striped border overflow-auto";

                        const tbody = document.createElement("tbody");

                        Object.entries(schema).forEach(([key, value]) => {
                            const row = document.createElement("tr");
                            row.innerHTML = `<td>${key}</td><td>${value}</td>`;
                            tbody.appendChild(row);
                        });
                        console.log("hello");
                        table.appendChild(tbody);
                        button.appendChild(table);
                        container.appendChild(button);
                    });
                    schema_button_listener();
                } catch (err) {
                    console.error("DB selection failed: ", err);
                    alert("Database selection failed, please try again!");
                }
            });
        });
    }

    function schema_button_listener() {
        document.querySelectorAll(".btn-schema").forEach((btn) => {
            btn.addEventListener("click", async () => {
                btn.disabled = true;

                const tableName = btn.value;
                if (!tableName) {
                    alert("Table has no name!");
                    btn.disabled = false;
                    return;
                }

                const query = "SELECT * FROM " + tableName;
                const selectUrl = indexUrlCheck;

                const formData = new FormData();
                formData.append("action", "run");
                formData.append("query", query);

                console.log(formData);
                console.log(query);
                console.log(selectUrl);

                const response = await fetch(selectUrl, {
                    method: "POST",
                    headers: { "X-CSRFToken": csrfToken },
                    body: formData,
                });
                window.location.reload(); // full refresh

                // do something
            });
        });
    }

    schema_button_listener();
    select_db_listener();

    let removeFileModal = document.getElementById("removeFileBtn");
    document.querySelectorAll(".file-btn-2").forEach((btn) => {
        btn.addEventListener("click", (event) => {
            removeFileModal.value = btn.dataset.file;
        });
    });
});
