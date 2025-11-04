const selectUrl = document.querySelector("#file-route-btn").dataset.fileRoute;

document.querySelectorAll(".file-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
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
        await fetch(selectUrl, {
            method: "POST", 
            body: formData
        });
    });
});

let removeFileModal = document.getElementById("removeFileBtn")
document.querySelectorAll(".file-btn-2").forEach(btn => {
    btn.addEventListener("click", event => {
        removeFileModal.value=btn.dataset.file;
    });
});