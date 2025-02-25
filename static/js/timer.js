quizDuration = questions.length * 60;

// Update Timer
function updateTimer() {
  var minutes = Math.floor(quizDuration / 60);
  var seconds = quizDuration % 60;

  timerSpan.innerText = minutes + "m" + seconds + "s";

  // Check if the time ended
  if (quizDuration <= 0) {
    // Automatically Submit the quiz
    clearTimeout(quizTimerId);
    submitQuiz();
  } else if (document.getElementById("message-div")) {
    clearTimeout(quizTimerId);
    highlightCorrectAnswers();
  } else {
    // decrement the timer value by 1s
    quizDuration--;
  }
}

// Function to submit the quiz
function submitQuiz() {
  // Submit the quiz
  quizForm.submit();
}

submitButton.addEventListener("click", submitQuiz);

// Timer Interval
quizTimerId = setInterval(updateTimer, 1000);
