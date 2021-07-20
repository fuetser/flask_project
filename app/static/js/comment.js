function commentPost(postId) {
    const text = $("#commentInput").val()
    if(text.length > 0){
        $.ajax({
            url: `/comment/${postId}`,
            type: "POST",
            dataType: "json",
            data: {text: text},
            success: responce => {
                $(".comments-list").html(responce.html_data)
                $("#commentsTitle").text(responce.title)
            },
            error: (request, status, error) => {
                console.log(error)
          }
        })
        clearCommentInput()
    }
}

function clearCommentInput() {
    $("#commentInput").val("")
}

function likeComment(commentId){
	$.ajax({
		url: `/comment/${commentId}/like`,
		type: "POST",
		success: responce => {
			console.log("success")
		},
		error: (request, status, error) => {
			console.log(error)
		}
	})
}

function deleteComment(commentId) {
	$.ajax({
		url: `/comment/${commentId}`,
		type: "DELETE",
		success: responce => {
			console.log("success")
			$(`#comment${commentId}`).remove()
			$("#commentsTitle").text(responce.title)
		},
		error: (request, status, error) => {
			console.log(error)
		}
	})
}
