document.addEventListener('DOMContentLoaded', function () {
    const followInfo = JSON.parse(document.getElementById('follow-data').textContent);
    document.querySelector('#profile-view-name').innerHTML = `@${followInfo.user}`;
    document.querySelector('#profile-view-body').innerHTML = `
                                <p class="numfollowers">Followers: ${followInfo.numfollowers}</p>
                                <p class="numfollowing">Following: ${followInfo.numfollowing}</p>`;

    document.querySelector(".followButton").addEventListener('click', () => {
        let follow = true
        if (document.querySelector(".followButton").value == "Unfollow") {
            follow = false
        }
        let fetchPromise = fetch(`/profiles/${followInfo.user}`, {
            method: 'PUT',
            body: JSON.stringify({
                follow: follow
            })
        })
        .then(() => {
            window.location.href = `/profiles/${followInfo.user}`;
        })
    })

})