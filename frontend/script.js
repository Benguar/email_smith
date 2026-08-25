let email = null
let picture = null
let promptText = null
let subject = null
let recipient = null
let body = null
const saveLogin = (userEmail, userPicture) => {
    email = userEmail
    picture = userPicture
    localStorage.setItem('userEmail', userEmail)
    localStorage.setItem('userPicture', userPicture)
}

const loadLogin = () => {
    const storedEmail = localStorage.getItem('userEmail')
    const storedPicture = localStorage.getItem('userPicture')
    if (storedEmail && storedPicture) {
        email = storedEmail
        picture = storedPicture
    }
}

const updateLoginUI = () => {
    const signInBtn = document.getElementById('sign-in-btn')
    if (email && picture && signInBtn) {
        signInBtn.innerHTML = `
            <img src="${picture}" alt="profile" class="user-avatar"><span>${email}</span>
        `
        signInBtn.classList.add('signed-in')
        signInBtn.onclick = logout;
    }
}

signin = () => {
    window.location.href = 'http://127.0.0.1:8000/auth/google-auth/signup'
}

window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search)
    const urlEmail = urlParams.get('email')
    const urlPicture = urlParams.get('picture')

    if (urlEmail && urlPicture) {
        saveLogin(urlEmail, urlPicture)
        window.history.replaceState({}, document.title, window.location.pathname)
    } else {
        loadLogin()
    }

    updateLoginUI()
    const promptInput = document.getElementById('prompt-input');
    if (promptInput) {
        promptInput.addEventListener('input', function() {
            // 1. Reset height temporarily to shrink if text is deleted
            this.style.height = 'auto'; 
            
            // 2. Set height to exactly fit the current text content
            this.style.height = this.scrollHeight + 'px'; 
            
            // 3. If it hits our 150px max-height, turn the scrollbar back on
            if (this.scrollHeight >= 75) {
                this.style.overflowY = 'auto';
            } else {
                this.style.overflowY = 'hidden';
            }
        });
    }
}

logout = () => {
   email = null;
   picture = null;
   localStorage.removeItem('userEmail');
   localStorage.removeItem('userPicture');
   const signInBtn = document.getElementById('sign-in-btn');
   if (signInBtn) {
       signInBtn.innerHTML = `
           <span class="g-icon">
               <i class="fa-brands fa-google"></i>
           </span>
           <span class="sign-in-text">Sign in</span>
       `;
       signInBtn.classList.remove('signed-in');
       signInBtn.onclick = signin;
   }
}
send_prompt = async () => {
    const promptInput = document.getElementById('prompt-input')
    promptText = promptInput?.value?.trim()
    const submitBtn = document.getElementById('prompt-submit')
    promptInput.value = ''
    promptInput.style.height = '24px'
    const FromDiv = document.getElementById("from-content")
    const ToDiv = document.getElementById("to-content")
    const SubjectDiv = document.getElementById("subject-content")
    const BodyDiv = document.getElementById("body-content")
    const WindowBody = document.querySelector('.window-body');
    if (!promptText) {
        console.warn('Prompt is empty.')
        return
    } 
    if (!email) {
        signin()
    }
    const originalBtnContent = submitBtn.innerHTML;
    submitBtn.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    submitBtn.disabled = true;
    try {
        const response = await fetch('http://127.0.0.1:8000/send_prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'prompt': promptText,'email': email }),
            credentials: 'include'
        })

        const data = await response.json()
        console.log(data)
        recipient = data["recipient"]
        subject = data["subject"]
        body = data["body"]
        if (body != 'this does not require email tool'){
            ToDiv.innerHTML = recipient
            SubjectDiv.innerHTML = subject
            BodyDiv.innerHTML = body
            WindowBody.style.visibility = "visible"
            
        }else{
            alert("this does not require email call you fraud")
            return
        }

    } catch (error) {
        console.error('Failed to send prompt', error)
    } finally {
        submitBtn.innerHTML = originalBtnContent; 
        submitBtn.disabled = false; 
    }
}

send = async () => {
    const FromDiv = document.getElementById("from-content")
    const ToDiv = document.getElementById("to-content")
    const SubjectDiv = document.getElementById("subject-content")
    const BodyDiv = document.getElementById("body-content")
    const WindowBody = document.querySelector('.window-body')
    const submitBtn = document.getElementById('prompt-submit')
    ToDiv.innerHTML = ''
    FromDiv.innerHTML = ''
    SubjectDiv.innerHTML = ''
    BodyDiv.innerHTML = ''
    WindowBody.style.visibility = 'hidden'
    payload ={
     "decision": "yes",
     "thread_id": "1",
     "subject": SubjectDiv.innerHTML,
      "recipient_email": ToDiv.innerHTML,
      "body": BodyDiv.innerHTML,
      "email": email
    }
    console.log(payload)
    const request = await fetch(
       'http://127.0.0.1:8000/resume',
       {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(
            payload
        ),
        credentials: "include" 
        }
    )
    const response = await request.json()
    console.log(response)
    if (response === "successful"){
        submitBtn.onclick = send_prompt
    }
}
discard = async () => {
    const FromDiv = document.getElementById("from-content")
    const ToDiv = document.getElementById("to-content")
    const SubjectDiv = document.getElementById("subject-content")
    const BodyDiv = document.getElementById("body-content")
    const WindowBody = document.querySelector('.window-body')
    const submitBtn = document.getElementById('prompt-submit')
    ToDiv.innerHTML = ''
    FromDiv.innerHTML = ''
    SubjectDiv.innerHTML = ''
    BodyDiv.innerHTML = ''
    WindowBody.style.visibility = 'hidden'
    submitBtn.onclick = send_prompt
    payload ={
     "decision": "no",
     "subject": SubjectDiv.innerHTML,
      "recipient_email": ToDiv.innerHTML,
      "body": BodyDiv.innerHTML,
      "email": email
    }
    console.log(payload)
    const request = await fetch(
       'http://127.0.0.1:8000/resume',
       {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(
            payload
        ),
        credentials: "include" 
        }
    )
    const response = await request.json()
    console.log(response)
}

edit =  () => {
    let promptInput = document.getElementById('prompt-input')
    promptInput.value = promptText
    console.log(promptText)
    const submitBtn = document.getElementById('prompt-submit')
    submitBtn.onclick = send_prompt
}