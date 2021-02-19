const navbar = document.querySelector(".navbar")
const body = document.querySelector("body")

body.style.cssText = `padding-top: ${navbar.clientHeight}px;`
var lastScroll = 0

window.addEventListener("scroll", (event) => {
    if (window.pageYOffset < lastScroll) {
        if (navbar.classList.contains("scrolled-down")) {
            navbar.classList.remove("scrolled-down")
        }
        navbar.classList.add("scrolled-up")
    } else {
        if (navbar.classList.contains("scrolled-up")) {
            navbar.classList.remove("scrolled-up")
        }
        navbar.classList.add("scrolled-down")
    }
    lastScroll = window.pageYOffset
})
