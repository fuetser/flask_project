const navbar = document.querySelector(".navbar")
const body = document.querySelector("body")

body.style.cssText = `padding-top: ${navbar.clientHeight}px;`
var lastScroll = window.pageYOffset * 2

document.addEventListener("scroll", (event) => {
    if (window.pageYOffset <= lastScroll) {
        navbar.classList.remove("scrolled-down")
        navbar.classList.add("scrolled-up")
    } else {
        navbar.classList.remove("scrolled-up")
        navbar.classList.add("scrolled-down")
    }
    lastScroll = window.pageYOffset
})

document.addEventListener("optimizedResize", (event) => {
    body.style.cssText = `padding-top: ${navbar.clientHeight}px;`
})
