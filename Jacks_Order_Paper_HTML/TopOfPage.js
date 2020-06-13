
$(function () {
    $(window).scroll(function () {
        var top_offset = $(window).scrollTop(); 
        console.log(top_offset)
        if (top_offset == 0) {
            $('nav#toc > ul.ToC-list li:first-child').addClass('active');
            $('nav#toc > ul.ToC-list li:not(first-child)').removeClass('active');
        } 
    })
});