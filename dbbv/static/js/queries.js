document.querySelectorAll('.btn-remove-query').forEach(btn => {
    btn.addEventListener('click', async () => {
        const removeIndex = btn.value;
        const formData = new FormData();    
        formData.append("remove", removeIndex)

        targetUrl = btn.dataset.fileRoute;
        const response = await fetch(targetUrl, {
            method: "POST",
            body: formData
        })
        if (response.ok) {
            btn.closest('.col').remove();  // remove only after successful server update
        } else {
            alert("Failed to remove query on server.");
        }
        const emptyList = await response.text()
        if (emptyList === "1")
           document.querySelector(".queryInput").innerHTML = "You deleted the last query"
    });
    

});