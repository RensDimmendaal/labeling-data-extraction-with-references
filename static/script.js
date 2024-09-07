// This function grabs the currently selected text in the job posting and updates the substring_quote of the active field
document.getElementById('update-substring').onclick = function () {
    const selectedText = window.getSelection().toString();
    if (selectedText) {
        const textarea = document.querySelector('textarea');
        textarea.value += '\n' + selectedText;
    }
};
