
{
    const csrfToken = window.CSRF_TOKEN
    const urlCheck = document.querySelector("#file-route-btn")
    // Only run sidebar logic on pages that include #file-route-btn
    if (urlCheck)
    { 
        const selectUrl = urlCheck.dataset.fileRoute;


        document.querySelectorAll(".file-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
            try { 
                    // remove active class from all buttons
                    document.querySelectorAll(".file-btn").forEach(b => {
                        b.classList.remove("active");
                    })
                    // Add active class to clicked button
                    btn.classList.add("active");
                    
                    const selectedFile = btn.dataset.file; 
                    const formData = new FormData();
                    formData.append("selected_file", selectedFile);
                
                    // Send selected file to Flask to update session
                    const response = await fetch(selectUrl, {
                        method: "POST", 
                        headers: { "X-CSRFToken": csrfToken },
                        body: formData
                    });
                    if (!response.ok){
                        console.log("db selection failed!");
                        alert("db selection failed");
                        throw new Error(`HTTP ${response.status} - ${response.statusText}`);
                    }
                        
                    const data = await response.json();
                    
                    const container = document.getElementById('dashboard-collapse');
                    container.innerHTML = "";

                    data.forEach(schema => {
                        const table = document.createElement("table");
                        table.className = "table table-striped border overflow-auto";
                        
                        const tbody = document.createElement("tbody")
                        
                        Object.entries(schema).forEach(([key, value]) => {
                            const row = document.createElement("tr");
                            row.innerHTML = `<td>${key}</td><td>${value}</td>`;
                            tbody.appendChild(row);
                        });

                        table.appendChild(tbody);
                        container.appendChild(table);
                    });
                } catch (err){
                    console.error("DB selection failed: ", err);
                    alert("Database selection failed, please try again!");
                }
            });
        });

        let removeFileModal = document.getElementById("removeFileBtn")
        document.querySelectorAll(".file-btn-2").forEach(btn => {
            btn.addEventListener("click", event => {
                removeFileModal.value=btn.dataset.file;
            });
        });
    }
}