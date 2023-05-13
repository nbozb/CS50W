document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email.bind(this));

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';


  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  document.querySelector('#compose-form').onsubmit = () => {
    let status = true;
    document.querySelector('#error').innerHTML = '';
      let fetchPromise = fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
          recipients: document.querySelector('#compose-recipients').value,
          subject: document.querySelector('#compose-subject').value,
          body: document.querySelector('#compose-body').value
        })
      })
      .then(response => {
        return response.json();
      })
      .then(result => {
        if (result.error) {
          localStorage.setItem('message', 'Archived!');
          document.querySelector('#error').innerHTML = result.error;
        } else {
          load_mailbox('sent');
        }
      });
    
    return false;
  }
}

function reply_email(id) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
      document.querySelector('#compose-recipients').value = email.sender;
      if (email.subject.slice(0, 3) === "RE:") {
        document.querySelector('#compose-subject').value = `${email.subject}`;
      } else {
        document.querySelector('#compose-subject').value = `RE: ${email.subject}`;
      }
      
      
      document.querySelector('#compose-body').value = `\n\n On ${email.timestamp}, ${email.sender} wrote: \n${email.body}`;

      document.querySelector('#compose-form').onsubmit = () => {
        let status = true;
        document.querySelector('#error').innerHTML = '';
          let fetchPromise = fetch('/emails', {
            method: 'POST',
            body: JSON.stringify({
              recipients: document.querySelector('#compose-recipients').value,
              subject: document.querySelector('#compose-subject').value,
              body: document.querySelector('#compose-body').value
            })
          })
          .then(response => {
            return response.json();
          })
          .then(result => {
            if (result.error) {
              document.querySelector('#error').innerHTML = result.error;
            } else {
              load_mailbox('sent');
            }
          });
        
        return false;
      }
    })


  // Prefill composition fields
  
}


function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#mailbox-name').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  document.querySelector('#emails').innerHTML = '';
  document.querySelector('#buttons').innerHTML = '';

  //get mailbox JSON data
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      emails.forEach(email => {
        //create div
        const newEmail = document.createElement('div');

        newEmail.classList.add("email-info", "list-group-item");
        if (!email.read) newEmail.classList.add("unread-email");
        console.log(`${email.subject}: ${email.archive}`);

        newEmail.innerHTML = `<p>${email.sender}</p><p class="subject">${email.subject}</p><p class="timestamp">${email.timestamp}</p>`
        
        
        newEmail.addEventListener('click', () => {

          document.querySelector('#emails-view').style.display = 'none';

          
          if (mailbox == 'inbox') {
            const button = document.createElement('button');
            button.classList.add("btn", "btn-sm", "btn-outline-secondary");
            button.innerHTML = "Archive";
            button.classList.add("archive-btn")
            document.querySelector('#buttons').append(button);
          } else if (email.archived == true) {
            const button = document.createElement('button');
            button.classList.add("btn", "btn-sm", "btn-outline-secondary");
            button.innerHTML = "Unarchive";
            button.classList.add("unarchive-btn")
            document.querySelector('#buttons').append(button);
          }
          
          get_email(email.id);

        });
        document.querySelector('#emails').append(newEmail);

      })
    });
}

function get_email(id) {
  document.querySelector('#email-metadata').innerHTML = ''
  document.querySelector('#email-body').innerHTML = '';
  document.querySelector('#view-email').style.display = 'block';

  fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {

      document.querySelector('#email-metadata').innerHTML = 
      `
        <p><b>From:</b> ${email.sender}</p>
        <p><b>To:</b> ${email.recipients}</p>
        <p><b>Subject:</b> ${email.subject}</p>
        <p><b>Timestamp:</b> ${email.timestamp}</p>
      `;

      let bodytext = email.body
      bodytext = bodytext.replaceAll("\r\n", "<br/>").replaceAll("\n", "<br/>")
      document.querySelector('#email-body').innerHTML = 
      `${bodytext}`
      console.log(bodytext);
    })

    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        read: true
      })
    })

    if (document.querySelector(".archive-btn")) {
      document.querySelector(".archive-btn").addEventListener('click', () => {
        fetch(`/emails/${id}`, {
          method: 'PUT',
          body: JSON.stringify({
              archived: true
          })
        })
        .then(() => {
          localStorage.setItem('message', 'Archived!');
          load_mailbox('inbox');
        }) 
      })
    }

    if (document.querySelector(".unarchive-btn")) {
      document.querySelector(".unarchive-btn").addEventListener('click', () => {
        fetch(`/emails/${id}`, {
          method: 'PUT',
          body: JSON.stringify({
              archived: false
          })
        })
        .then(() => {
          localStorage.setItem('message', 'Unarchived!');
          load_mailbox('inbox');
        }) 
        
      })
    }

    const button = document.createElement('button');
    button.classList.add("btn", "btn-sm", "btn-outline-secondary", "archive-btn");
    button.innerHTML = "Reply"
    button.addEventListener('click', () => {
      reply_email(id);
    })

    document.querySelector('#buttons').append(button);
}