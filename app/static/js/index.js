const navbar = document.querySelector(".navbar")
const body = document.querySelector("body")
const clearSearchButton = document.querySelector("#clearSearchButton")
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
function animateLikeButtons(){
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
}

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
                console.log(responce)
                $(".comments-list").html(responce.html_data)
                $("#commentsTitle").text(responce.title)
            },
            error: (request, status, error) => {
                console.log(error, request)
          }
        })
        $("#commentInput").val("")
    }
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
            $("#commentsTitle").text(responce.title)
        },
        error: (request, status, error) => {
            console.log(error, request)
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
            console.log(error, request)
        }
    })
    if(redirectToBest) document.location.href = "/best"
    $(`#post${postId}`).remove()
}

function deleteGroup(groupId) {
    $.ajax({
        url: `/group/${groupId}`,
        type: "DELETE",
        success: responce => {
            console.log("success")
            document.location.href = "/best"
        },
        error: (request, status, error) => {
            console.log(error, request)
        }
    })
}

function performSearch() {
    const requestText = $("#searchInput").val()
    const searchGroups = $("#searchGroupsCheckbox").prop("checked")
    const searchUsers = $("#searchUsersCheckbox").prop("checked")
    const searchPosts = $("#searchPostsCheckbox").prop("checked")
    const searchResults = $("#searchResults")
    if(requestText) {
        addSearchParamToUrl("q", requestText)
        addSearchTargetToUrl(searchGroups, searchUsers, searchPosts)
        $.ajax({
            url: "",
            type: "POST",
            dataType: "json",
            data: {
                request_text: requestText,
                search_groups: searchGroups,
                search_users: searchUsers,
                search_posts: searchPosts
            },
            success: responce => {
                searchResults.html(responce.html_data)
                animateLikeButtons()
            },
            error: (request, status, error) => {
                console.log(error, request)
            }
        })
    }
}

function addSearchParamToUrl(key, value) {
    if (history.pushState) {
        let searchParams = new URLSearchParams(window.location.search)
        searchParams.set(key, value)
        let newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + searchParams.toString()
        window.history.pushState({path: newurl}, '', newurl)
    }
}

function removeSearchParamFromUrl(key) {
    if (history.pushState) {
        let searchParams = new URLSearchParams(window.location.search)
        searchParams.delete(key)
        let newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + searchParams.toString()
        window.history.pushState({path: newurl}, '', newurl)
    }
}

function addSearchTargetToUrl(searchGroups, searchUsers, searchPosts) {
    let searchTarget = "groups"
    if(searchUsers){
        searchTarget = "users"
    } else if(searchPosts){
        searchTarget = "posts"
    }
    addSearchParamToUrl("sort", searchTarget)
}

function prepareSearchPage(){
    clearSearchButton.addEventListener("click", e => $("#searchInput").val("").focus())
    let searchParams = new URLSearchParams(window.location.search)
    if ((request = searchParams.get("q")) !== null) {
        $("#searchInput").val(request)
        if((searchTarget = searchParams.get("sort")) !== null) {
            switch(searchTarget){
                case "users":
                    const searchUsers = $("#searchUsersCheckbox").prop("checked", true)
                    break
                case "posts":
                    const searchPosts = $("#searchPostsCheckbox").prop("checked", true)
                    break
                default:
                    const searchGroups = $("#searchGroupsCheckbox").prop("checked", true)
                    break
            }
        }
        performSearch()
        animateLikeButtons()
    }
}

function swapPage(requestText, searchTarget, pageIndex) {
    addSearchParamToUrl("q", requestText)
    addSearchParamToUrl("sort", searchTarget)
    addSearchParamToUrl("page", pageIndex)
    performSearch()
    animateLikeButtons()
}

function search() {
    removeSearchParamFromUrl("page")
    performSearch()
}

$(window).ready(e => animateLikeButtons())
