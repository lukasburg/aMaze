function pressToggleButton(button) {
    disableButton(button)
    let setState = toggleAndGetNewState(button)
    toggleClass(button, setState)
    setOnServer(button, button.dataset.serverUrl, setState)
}

function disableButton(button) {
    button.disabled = true
}

function enableButton(button) {
    button.disabled = false
}


function toggleAndGetNewState(button) {
    let currentState = button.dataset.currentState === "true"
    button.dataset.currentState = !currentState
    return !currentState
}

function toggleClass(button, state) {
    if (state) {
        button.classList.add(button.dataset.classTrue)
        button.classList.remove(button.dataset.classFalse)
    } else {
        button.classList.remove(button.dataset.classTrue)
        button.classList.add(button.dataset.classFalse)
    }
}

function setOnServer(button, url, setState) {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", url, true)
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
    xhr.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value)
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            enableButton(button)
        }
    }
    xhr.send(`set_state=${setState}`)
}
