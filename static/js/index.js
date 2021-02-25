const navbar = document.querySelector(".navbar")
const body = document.querySelector("body")
const likeButtons = document.getElementsByClassName("like")

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

for (const btn of likeButtons){
    if(btn != null){
        btn.addEventListener("click", event => {
            if (btn.classList.contains("bi-heart")){
                btn.classList.remove("bi-heart")
                btn.classList.add("bi-heart-fill")
            } else {
                btn.classList.remove("bi-heart-fill")
                btn.classList.add("bi-heart")
            }
        })
    }
}
