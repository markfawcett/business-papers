$(window).scroll(function() {
   // $(".float-right").removeClass("fade");
   if($(window).scrollTop() + $(window).height() == $(document).height()) {
       //you are at bottom
       // $(".float-right").addClass("fade");
       $("nav#toc > ul.ToC-list > li").removeClass("active");
       $("nav#toc > ul.ToC-list > li:last-child").addClass("active");
   }
});