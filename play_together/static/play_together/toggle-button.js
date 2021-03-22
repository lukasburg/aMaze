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

function forceRefresh(url) {
    window.location.href = url
}

function forceLogin(url) {

}

function setOnServer(button, url, setState) {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", url, true)
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
    xhr.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value)
    xhr.onreadystatechange = function () {
        if (this.status === 403) {
            // Client logged out
            forceLogin(button.dataset.loginUrl)
        } else if (this.status === 409) {
            // Conflict between client and server information
            forceRefresh(button.dataset.errorUrl)
        } else if (this.status === 200 && this.readyState !== XMLHttpRequest.DONE) {
        } else if (this.status === 200 && this.readyState === XMLHttpRequest.DONE) {
            enableButton(button)
        } else {
            console.log("Unexpected response:")
            console.log(this)
        }
    }
    xhr.send(`set_state=${setState}`)
}

function updateGameDisabledList(button) {
    let consoleName = button.dataset.name
    let newState = button.dataset.currentState === 'true'
    document.querySelectorAll(`[data-console-name="${consoleName}"]`).forEach(
        function (item) {
            item.disabled = !newState
        }
    )
}
