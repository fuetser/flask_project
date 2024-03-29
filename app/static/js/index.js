const navbar = document.querySelector(".navbar")
const body = document.querySelector("body")
const clearSearchButton = document.querySelector("#clearSearchButton")
const likeButtons = document.getElementsByClassName("like")
const likesWrappers = document.getElementsByClassName("likes-wrapper")
const shareButtons = document.getElementsByClassName("bi-share")
const daysButtons = document.getElementsByClassName("days-button")

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

function copyStringToClipboard(str) {
    var el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
}

// like icon filling/unfilling on click
function animateLikeButtons() {
    Array.from(likeButtons)
    .filter(btn => btn !== null)
    .forEach((btn) =>
        btn.addEventListener("click", event => {
            if (btn.classList.contains("bi-heart")){
                btn.classList.remove("bi-heart")
                btn.classList.add("bi-heart-fill")
            } else {
                btn.classList.remove("bi-heart-fill")
                btn.classList.add("bi-heart")
            }
            const counter = $(btn).parent().parent().children("#likesCounter")
            const likesCount = parseInt(counter.text())
            if(counter.hasClass("active")){
                counter.text(likesCount - 1)
                counter.removeClass("active")
            } else {
                counter.text(likesCount + 1)
                counter.addClass("active")
            }
        })
    )
}

function connectShareButtons() {
    Array.from(shareButtons)
    .filter(btn => btn !== null)
    .forEach(btn => {
        btn.addEventListener("click", e => {
            $("#toastMessage").addClass("show")
            timeout = setTimeout(() => $("#toastMessage").removeClass("show"), 5000)
            copyStringToClipboard(window.location.protocol + "//" + window.location.host + $(btn).data("link"))
        })
    })
    $("#hideToastButton").click(e => {
        $("#toastMessage").removeClass("show")
        window.clearTimeout(timeout)
    })
}

function connectDaysButtons() {
    Array.from(daysButtons)
    .filter(btn => btn !== null)
    .forEach(btn => {
        btn.addEventListener("click", e => {
            for(const button of daysButtons) {
                $(button).parent().removeClass("active")
            }
            $(btn).parent().addClass("active")
            if(history.pushState){
                let searchParams = new URLSearchParams(window.location.search)
                const days = $(btn).data("days")
                addSearchParamToUrl("days", days)
                removeSearchParamFromUrl("page")
                showPostsByAge(days, 1)
            }
        })
    })
}

function prepareMainPage() {
    if(history.pushState){
        let searchParams = new URLSearchParams(window.location.search)
        switch(searchParams.get("days")) {
            case "7":
                $("#weekButton").addClass("active")
                break
            case "30":
                $("#monthButton").addClass("active")
                break
            case "365":
                $("#yearButton").addClass("active")
                break
            default:
                $("#dayButton").addClass("active")
                break
        }
    }
}

function sortComments(sortBy, reverse) {
    addSearchParamToUrl("sort", sortBy)
    if (reverse) {
        addSearchParamToUrl("reverse", reverse)
    } else {
        removeSearchParamFromUrl("reverse")
    }
    $.ajax({
        url: "",
        type: "POST",
        success: responce => {
            $(".comments-list").html(responce.html_data)
            animateLikeButtons()
        },
        error: (request, status, error) => {
            console.log(error)
      }
    })
}

function performSearch() {
    let searchBy = $("#searchGroupsCheckbox").prop("checked") ? "groups" :
        $("#searchUsersCheckbox").prop("checked") ? "users" :
        $("#searchPostsCheckbox").prop("checked") ? "posts" :
        "groups";
    const requestText = $("#searchInput").val()
    const searchResults = $("#searchResults")
    if(requestText) {
        addSearchParamToUrl("q", requestText)
        addSearchParamToUrl("sort", searchBy)
        $.ajax({
            url: "",
            type: "POST",
            dataType: "json",
            data: {
                request_text: requestText,
                searchBy: searchBy
            },
            success: responce => {
                searchResults.html(responce.html_data)
                animateLikeButtons()
                connectShareButtons()
            },
            error: (request, status, error) => {
                console.log(error)
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
        connectShareButtons()
    }
}

function swapPage(requestText, searchTarget, pageIndex) {
    addSearchParamToUrl("q", requestText)
    addSearchParamToUrl("sort", searchTarget)
    addSearchParamToUrl("page", pageIndex)
    performSearch()
    animateLikeButtons()
    connectShareButtons()
}

function search() {
    removeSearchParamFromUrl("page")
    performSearch()
}

function showPostsByPage(postsSortType, event) {
    addSearchParamToUrl("page", $(event.target).data("page"))
    if (history.pushState) {
        let searchParams = new URLSearchParams(window.location.search)
        showPostsByAge(
            searchParams.get("days") || 1, 
            $(event.target).data("page"),
            postsSortType
        )
        window.scrollTo(0, 0)
    }
}

function showPostsByAge(days, pageIndex, postsSortType) {
    $.ajax({
        url: `/get_posts/${days}?page=${pageIndex}`,
        type: "POST",
        dataType: "json",
        data: {type: postsSortType},
        success: responce => {
            $("#postsHolder").html(responce.html_data)
            animateLikeButtons()
            connectShareButtons()
        },
        error: (request, status, error) => {
            console.log(error)
        }
    })
}

function showPostsByGroup(groupId, event) {
    const pageIndex = $(event.target).data("page")
    addSearchParamToUrl("page", pageIndex)
    $.ajax({
        url: "",
        type: "POST",
        success: responce => {
            $("#postsHolder").html(responce.html_data)
            animateLikeButtons()
            connectShareButtons()
            window.scrollTo(0, 0)
            if((footer = $("#paginationFooter")).length > 0) {
                footer.remove()
            }
        },
        error: (request, status, error) => {
            console.log(error)
        }
    })
}

function showOrderedPostsByGroup(sortBy, reverse, event) {
    addSearchParamToUrl("sort", sortBy)
    if(reverse) addSearchParamToUrl("reverse", reverse)
    else removeSearchParamFromUrl("reverse")
    showPostsByGroup($(event.target).data("group-id"), event)
}

function showPostsByUser(username, sortBy, reverse, event) {
    const pageIndex = $(event.target).data("page")
    addSearchParamToUrl("page", pageIndex)
    let url = `/user/${username}/posts?page=${pageIndex || 1}&sort=${sortBy}`
    if(reverse) url += `&reverse=true`
    $.ajax({
        url: url,
        type: "POST",
        success: responce => {
            $("#postsHolder").html(responce.html_data)
            animateLikeButtons()
            connectShareButtons()
            window.scrollTo(0, 0)
        },
        error: (request, status, error) => {
            console.log(error)
        }
    })
}

function showOrderedPostsByUser(sortBy, reverse, event) {
    addSearchParamToUrl("sort", sortBy)
    if(reverse) addSearchParamToUrl("reverse", reverse)
    else removeSearchParamFromUrl("reverse")
    showPostsByUser($(event.target).data("username"), sortBy, reverse, event)
}

function showUserSubscriptions(username, event) {
    const pageIndex = $(event.target).data("page")
    addSearchParamToUrl("page", pageIndex)
    $.ajax({
        url: `/user/${username}/subscriptions?page=${pageIndex}`,
        type: "POST",
        success: responce => {
            $("#v-pills-subscriptions").html(`<div class="content-container">${responce.html_data}</div>`)
            window.scrollTo(0, 0)
        },
        error: (request, status, error) => {
            console.log(error)
        }
    })
}

$(window).ready(e => {
    animateLikeButtons()
    connectShareButtons()
    connectDaysButtons()
})
