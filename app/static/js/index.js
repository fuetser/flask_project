const navbar = document.querySelector(".navbar")
const body = document.querySelector("body")
const likeButtons = document.getElementsByClassName("like")
const likesWrappers = document.getElementsByClassName("likes-wrapper")

var lastScroll = window.scrollY * 2

document.addEventListener("scroll", (event) => {
    if (window.scrollY < lastScroll) {
        if (navbar.classList.contains("scrolled-down")) {
            navbar.classList.remove("scrolled-down")
        }
        navbar.classList.add("scrolled-up")
    } else {
        navbar.classList.remove("scrolled-up")
        navbar.classList.add("scrolled-down")
    }
    lastScroll = window.scrollY
})

document.addEventListener("optimizedResize", (event) => {
    body.style.cssText = `padding-top: ${navbar.clientHeight}px;`
})

// like icon filling/unfilling on click
Array.from(likeButtons)
    .filter(btn => btn !== null)
    .forEach((btn) =>
        btn.addEventListener("click", event => {
            const counter = $(btn).parent().parent().children("#likesCounter")
            const likesCount = parseInt((counter.text()))
            if(counter.hasClass("active")){
                counter.text(likesCount - 1)
                counter.removeClass("active")
            } else {
                counter.text(likesCount + 1)
                counter.addClass("active")
            }
            if (btn.classList.contains("bi-heart")){
                btn.classList.remove("bi-heart")
                btn.classList.add("bi-heart-fill")
            } else {
                btn.classList.remove("bi-heart-fill")
                btn.classList.add("bi-heart")
            }
        })
    )

function likePost(postId){
   $.ajax({
      url: `/like/${postId}`,
      type: "POST",
      success: responce => {
        console.log(`Successfully liked post with id ${postId}`)
      },
      error: (request, status, error) => {
        console.log(error)
      }
   })
}

function commentPost(postId){
    const text = $("#commentInput").val()
    if(text.length > 0){
        $.ajax({
            url: `/comment/${postId}`,
            type: "POST",
            dataType: "json",
            data: {text: text},
            success: responce => {
                console.log("success")
            },
            error: (request, status, error) => {
            console.log(error, request)
          }
        })
        $("#commentInput").val("")
    }
    location.reload()
}


function likeComment(commentId){
    $.ajax({
        url: `/like_comment/${commentId}`,
        type: "POST",
        success: responce => {
            console.log("success")
        },
        error: (request, status, error) => {
            console.log(error, request)
        }
    })
}


function deleteComment(commentId) {
    $(`#comment${commentId}`).remove()
    $.ajax({
        url: `/comment/${commentId}`,
        type: "DELETE",
        success: responce => {
            console.log("success")
            $("#commentsTitle").text(responce["comments"])
        },
        error: (request, status, error) => {
            console.log(error, request)
        }
    })
}

function deletePost(postId) {
    $(`#post${postId}`).remove()
    $.ajax({
        url: `/post/${postId}`,
        type: "DELETE",
        success: responce => {
            console.log("success")
        },
        error: (request, status, error) => {
            console.log(error, request)
        }
    })
}

