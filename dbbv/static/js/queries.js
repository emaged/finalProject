{
  const csrfToken = window.CSRF_TOKEN;

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

        const emptyList = await response.text();

        if (!response.ok) {
          console.error("Server failed to remove query: ", response.statusText);
          alert("Failed to remove query on server.");
          return;
        }

        btn.closest(".col").remove(); // remove only after successful server update
        if (emptyList === "1")
          document.querySelector(".queryInput").innerHTML =
            "You deleted the last query";

        // recalculate indexes
        document.querySelectorAll(".btn-remove-query").forEach((btn, index) => {
          btn.value = index;
          console.log(index);
        });
      } catch (error) {
        console.error("Error while removing query: ", error);
        alert("something went wrong while removing query");
      }
    });
  });
}
