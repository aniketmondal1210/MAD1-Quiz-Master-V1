// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", () => {
  // Add confirmation for delete actions
  const deleteButtons = document.querySelectorAll("[data-confirm]")
  deleteButtons.forEach((button) => {
    button.addEventListener("click", function (event) {
      if (!confirm(this.getAttribute("data-confirm"))) {
        event.preventDefault()
      }
    })
  })

  // Form validation
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    form.addEventListener(
      "submit",
      (event) => {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }
        form.classList.add("was-validated")
      },
      false,
    )
  })

  // Add tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.map((tooltipTriggerEl) => {
    return new bootstrap.Tooltip(tooltipTriggerEl)
  })

  // Quiz timer
  const timerElement = document.getElementById("quiz-timer")
  const quizForm = document.getElementById("quiz-form")
  if (timerElement && quizForm) {
    // Get duration from the timer element text (HH:MM)
    const durationText = timerElement.textContent.trim()
    const durationParts = durationText.split(":")

    // Calculate total seconds (hours * 3600 + minutes * 60)
    let timeLeft = Number.parseInt(durationParts[0]) * 3600 + Number.parseInt(durationParts[1]) * 60

    const timer = setInterval(() => {
      timeLeft--

      if (timeLeft < 0) {
        clearInterval(timer)
        alert("Time's up! Your quiz will be submitted automatically.")
        quizForm.submit()
        return
      }

      const hours = Math.floor(timeLeft / 3600)
      const minutes = Math.floor((timeLeft % 3600) / 60)
      const seconds = timeLeft % 60

      timerElement.textContent = `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
    }, 1000)
  }

  // Role selection in registration
  const roleRadios = document.querySelectorAll('input[name="role"]')
  const adminCodeField = document.getElementById("admin_code")

  if (roleRadios.length && adminCodeField) {
    function toggleAdminCode() {
      const selectedRole = document.querySelector('input[name="role"]:checked').value
      adminCodeField.required = selectedRole === "admin"
      adminCodeField.disabled = selectedRole !== "admin"
    }

    roleRadios.forEach((radio) => {
      radio.addEventListener("change", toggleAdminCode)
    })

    toggleAdminCode() // Initial state
  }
})
