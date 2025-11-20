document.addEventListener("DOMContentLoaded", () => {
    // check if csrf-token exists
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (!meta) return;
    const csrfToken = meta.getAttribute("content");

    document.querySelectorAll(".btn-remove-query").forEach((btn) => {
        btn.addEventListener("click", async () => {
            try {
                const removeIndex = btn.value;
                const formData = new FormData();
                formData.append("remove", removeIndex);

                const targetUrl = btn.dataset.fileRoute;
                const response = await fetch(targetUrl, {
                    method: "POST",
                    headers: { "X-CSRFToken": csrfToken },
                    body: formData,
                });

                const emptyList = await response.json();

                if (!response.ok) {
                    const msg = emptyList.error;
                    console.error("Server failed to remove query: " + msg);
                    alert("Failed to remove query on server: " + msg);
                    return;
                }

                btn.closest(".col").remove(); // remove only after successful server update
                if (emptyList.empty)
                    document.querySelector(".queryInput").innerHTML =
                        "You deleted the last query";

                // recalculate indexes
                document
                    .querySelectorAll(".btn-remove-query")
                    .forEach((btn, index) => {
                        btn.value = index;
                    });
            } catch (error) {
                console.error("Error while removing query: ", error);
                alert("something went wrong while removing query");
            }
        });
    });
});
