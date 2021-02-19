$('body').css('padding-top', $('.navbar').outerHeight() + 'px')

var last_scroll_top = 0;
$(window).scroll(function(e) {
    scroll_top = $(window).scrollTop();
    if(scroll_top < last_scroll_top) {
        $('.smart-scroll').removeClass('scrolled-down').addClass('scrolled-up');
    }
    else {
        $('.smart-scroll').removeClass('scrolled-up').addClass('scrolled-down');
    }
    last_scroll_top = scroll_top;
});
