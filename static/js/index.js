const navbar = document.querySelector(".navbar")
const body = document.querySelector("body")

// body.style.cssText = `padding-top: ${navbar.clientHeight}px;`
var lastScroll = window.scrollY * 2

window.addEventListener("scroll", (event) => {
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
