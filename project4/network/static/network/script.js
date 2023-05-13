document.addEventListener('DOMContentLoaded', function () {
    let type = document.querySelector('#posts-view-name').innerHTML.trim();
    if (type == 'none' || type == 'all') {
        load_posts('all');
    } else {
        load_posts('following');
    }
    
})


function load_posts(type) {
    //show posts
    document.querySelector('#posts-view-posts').innerHTML = '';
    document.querySelector('.posts-view').style.display = 'block';

    // Show the mailbox name
    document.querySelector('#posts-view-name').innerHTML = `${type.charAt(0).toUpperCase() + type.slice(1)} Posts`;

    //get posts JSON data
    fetch(`/posts/${type}`)
    .then(response => response.json())
    .then(posts => {
        posts.forEach(post => {
            const newPost = document.createElement('div');

            console.log(`${post.content} by ${post.poster} - ${post.meliked}`);

            if (!post.meliked) {
                newPost.innerHTML = `<br>
                                <p>${post.content}</p>
                                <p class="poster">${post.poster}</p>
                                <p class="timestamp">${post.timestamp}</p>
                                <p class="numLikes">${post.numlikes}</p>
                                <button class="likebutton">Like</button>
                                <br>`;
            } else {
                newPost.innerHTML = `<br>
                                <p>${post.content}</p>
                                <p class="poster">${post.poster}</p>
                                <p class="timestamp">${post.timestamp}</p>
                                <p class="numLikes">${post.numlikes}</p>
                                <button class="likebutton">Unlike</button>
                                <br>`;
            }
            

            //redirect to profile
            newPost.querySelector('.poster').addEventListener('click', () => {
                window.location.href = `/profiles/${post.poster}`;
            })

            //like post
            newPost.querySelector('.likebutton').addEventListener('click', () => {
                let fetchPromise = fetch(`/post/${post.id}`, {method: 'PUT'})
                .then(response =>
                    console.log(response)
                )
            })

            document.querySelector('#posts-view-posts').append(newPost);

        })                  
    })
}