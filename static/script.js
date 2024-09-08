// This function detects when text is selected in the job posting and updates the substring_quote of the active field
document.addEventListener("DOMContentLoaded", function () {
    const jobTextContainer = document.querySelector('.job-text-container');

    // Detect when the user finishes selecting text (mouseup event)
    jobTextContainer.addEventListener("mouseup", function () {
        const selectedText = window.getSelection().toString().trim();
        console.log(selectedText)

        if (selectedText) {
            // Find the active textarea for the active field
            const activeTextArea = document.querySelector('.active-field textarea');

            // If there is an active textarea, update its value with the selected text
            if (activeTextArea) {
                activeTextArea.value = selectedText;  // Replace the current value with the selected text
                updateHighlightedText(selectedText);  // Update the highlighted text in the job posting
            }
        }
    });

    // Function to update the highlighted text in the job posting
    function updateHighlightedText(highlight) {
        const jobPosting = document.querySelector('.job-posting');
        const originalText = jobPosting.textContent;
        const highlightedText = originalText.replace(/<mark>(.*?)<\/mark>/g, '$1'); // Remove existing highlights
        const newHighlightedText = highlightedText.replace(highlight, `<mark>${highlight}</mark>`);
        jobPosting.innerHTML = newHighlightedText;
    }

    // Detect changes in the textarea and update the highlighted text
    document.querySelector('.active-field textarea').addEventListener('input', function (event) {
        const newHighlight = event.target.value.trim();
        updateHighlightedText(newHighlight);
    });
});