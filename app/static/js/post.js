function likePost(postId){
    $.ajax({
        url: `/post/${postId}/like`,
        type: "POST",
        success: responce => {
            console.log(`Successfully liked post with id ${postId}`)
        },
        error: (request, status, error) => {
            console.log(error)
        }
    })
}

function deletePost(postId, redirectToBest) {
    $.ajax({
        url: `/post/${postId}`,
        type: "DELETE",
        success: responce => {
            console.log("success")
        },
        error: (request, status, error) => {
            console.log(error)
        }
    })
    if(redirectToBest) document.location.href = "/best"
    $(`#post${postId}`).remove()
}
