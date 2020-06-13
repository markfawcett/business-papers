// Begin Create TOC

var ToC = "<ul class='ToC-list'>";

// Get text and ID of each h2 and h3

var el, title, link;

$("div.secWrap").each(function() {

  el = $(this);
  title = $(this).find(">:first-child").text()
  link = "#" + el.attr("id");
  level = $(this).find(">:first-child").attr("class");
});

// Create a new list item and append to string

var newLine, el, title, link;

$("div.secWrap").each(function() {

  el = $(this);
  title = $(this).find(">:first-child").text()
  link = "#" + el.attr("id");
  level = "ToC" + $(this).find(">:first-child").attr("class");

  newLine =
  "<li class='" + level + "'>" +
  "<a href='" + link + "'>" +
  title +
  "</a>" +
  "</li>";

  ToC += newLine;
});

ToC += "</ul>"

$("nav#toc").prepend(ToC);

// End Create TOC

$('#toc li a').on('click', function(event) {
  $(this).parent().find('a').removeClass('active');
  $(this).addClass('active');
});


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

// activate sub sections of toc
$(window).scroll( function() {
  $('div.secWrap:has(h2)').each(function() {
    if($(window).scrollTop() >= $(this).offset().top -10) {
      var id = $(this).attr('id');
      $('#toc li').removeClass('active');
      /*$('#toc li').addClass('active');*/

      $('#toc li:has(> a[href="#' + id + '"])').addClass('active');
      /*$('#toc li a[href="#' + id + '"]').removeClass('active');*/
    }
  });

  // look out for the bottom
  if($(window).scrollTop() + $(window).height() == $(document).height()) {
    //you are at bottom
    // $(".float-right").addClass("fade");
    $("nav#toc > ul.ToC-list > li").removeClass("active");
    $("nav#toc > ul.ToC-list > li:last-child").addClass("active");
 }
});

// create sub list in toc
$("li", "ul.ToC-list").each(function () {
    var subElements = $(this).nextUntil("li[class=" + $(this).attr("class") + "]");
    if (subElements.length > 0) {
        var wrapped = $("<ul class='sub-ToC-list noShow' />").append(subElements);
        $(this).append($(wrapped));
    }
});



// $(window).scroll(function() {
// // $(".float-right").removeClass("fade");

// });