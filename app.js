/* =========================================================
   CONFIGURATION
========================================================= */

const API_URL = "http://127.0.0.1:8000/api/chat";


/* =========================================================
   DOM ELEMENTS
========================================================= */

const chatMessages =
    document.getElementById("chatMessages");

const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const typingIndicator =
    document.getElementById("typingIndicator");


/* =========================================================
   STATE
========================================================= */

let isSending = false;


/* =========================================================
   UTILITY
========================================================= */

function getCurrentTime() {

    return new Date().toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}


/* =========================================================
   FORMAT RESPONSE
========================================================= */

function formatResponse(text) {

    let formatted =
        escapeHtml(text);

    /*
     * Basic markdown-style formatting.
     */

    formatted = formatted.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    formatted = formatted.replace(
        /\n/g,
        "<br>"
    );

    return formatted;

}


/* =========================================================
   ADD USER MESSAGE
========================================================= */

function addUserMessage(message) {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "message user-message";


    wrapper.innerHTML = `

        <div class="avatar user-avatar">
            YOU
        </div>

        <div class="message-content">

            <div class="message-header">

                <strong>You</strong>

                <span>
                    ${getCurrentTime()}
                </span>

            </div>

            <div class="message-bubble">

                ${escapeHtml(message)}

            </div>

        </div>

    `;


    chatMessages.appendChild(wrapper);

    scrollToBottom();

}


/* =========================================================
   ADD ASSISTANT MESSAGE
========================================================= */

function addAssistantMessage(
    message,
    isError = false
) {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "message assistant-message";


    wrapper.innerHTML = `

        <div class="avatar assistant-avatar">
            AI
        </div>

        <div class="message-content">

            <div class="message-header">

                <strong>CRM Assistant</strong>

                <span>
                    ${getCurrentTime()}
                </span>

            </div>

            <div class="message-bubble ${isError ? "error-message" : ""}">

                ${formatResponse(message)}

            </div>

        </div>

    `;


    chatMessages.appendChild(wrapper);

    scrollToBottom();

}


/* =========================================================
   SCROLL
========================================================= */

function scrollToBottom() {

    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


/* =========================================================
   TYPING INDICATOR
========================================================= */

function showTyping() {

    typingIndicator.classList.remove(
        "hidden"
    );

    scrollToBottom();

}


function hideTyping() {

    typingIndicator.classList.add(
        "hidden"
    );

}


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage(
    providedMessage = null
) {

    if (isSending) {

        return;

    }


    const message =
        providedMessage !== null
            ? providedMessage.trim()
            : messageInput.value.trim();


    if (!message) {

        return;

    }


    isSending = true;

    sendButton.disabled = true;


    if (providedMessage === null) {

        messageInput.value = "";

        autoResize();

    }


    addUserMessage(message);

    showTyping();


    try {

        const response =
            await fetch(
                API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );

        }


        const data =
            await response.json();


        hideTyping();


        if (
            data.success &&
            data.response
        ) {

            addAssistantMessage(
                data.response
            );

        } else {

            addAssistantMessage(
                data.response ||
                "I couldn't process that request.",
                true
            );

        }


    } catch (error) {

        console.error(
            "CRM API Error:",
            error
        );


        hideTyping();


        addAssistantMessage(
            "I couldn't connect to the CRM backend. Please make sure the FastAPI server is running at http://127.0.0.1:8000.",
            true
        );

    } finally {

        isSending = false;

        sendButton.disabled = false;

        messageInput.focus();

    }

}


/* =========================================================
   SEND BUTTON
========================================================= */

sendButton.addEventListener(
    "click",
    () => {

        sendMessage();

    }
);


/* =========================================================
   ENTER KEY
========================================================= */

messageInput.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


/* =========================================================
   AUTO RESIZE TEXTAREA
========================================================= */

function autoResize() {

    messageInput.style.height =
        "auto";

    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            130
        ) + "px";

}


messageInput.addEventListener(
    "input",
    autoResize
);


/* =========================================================
   QUICK ACTIONS
========================================================= */

document
    .querySelectorAll(
        ".quick-action, .suggestion"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const message =
                        button.dataset.message;

                    if (message) {

                        sendMessage(
                            message
                        );

                    }

                }
            );

        }
    );


/* =========================================================
   SIDEBAR NAVIGATION
========================================================= */

document
    .querySelectorAll(".nav-item")
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    document
                        .querySelectorAll(
                            ".nav-item"
                        )
                        .forEach(
                            item =>
                                item.classList.remove(
                                    "active"
                                )
                        );


                    button.classList.add(
                        "active"
                    );


                    const id =
                        button.id;


                    if (
                        id !== "chatNav"
                    ) {

                        addAssistantMessage(
                            `${button.textContent.trim()} is available as part of the CRM interface. For this interview prototype, the main functionality is handled through the AI Assistant.`
                        );

                    }

                }
            );

        }
    );


/* =========================================================
   INITIALIZE
========================================================= */

messageInput.focus();

scrollToBottom();