document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.spots_left !== undefined ? details.spots_left : (details.max_participants - details.participants_count);

        // Show full badge if no spots left
        const availabilityText = spotsLeft > 0 ? `${spotsLeft} spots left` : `Full`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${availabilityText}</p>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown (disable if full)
        const option = document.createElement("option");
        option.value = name;
        option.textContent = spotsLeft > 0 ? name : `${name} (Full)`;
        if (spotsLeft <= 0) {
          option.disabled = true;
        }
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const activity = document.getElementById("activity").value;

    // Basic client-side validation
    if (!email || !activity) {
      showMessage("Please provide an email and select an activity.", "error");
      return;
    }

    // Re-check that the selected option is not disabled (in case the list changed)
    const selectedOption = document.querySelector(`#activity option[value="${CSS.escape(activity)}"]`);
    if (selectedOption && selectedOption.disabled) {
      showMessage("Selected activity is full. Please choose another activity.", "error");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message || "Signed up successfully", "success");
        signupForm.reset();
        // Refresh the activities list to show updated availability
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove("hidden");

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Initialize app
  fetchActivities();
});
