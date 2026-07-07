$(function() {
  function isMobileNav() {
    return window.matchMedia('(max-width: 767px)').matches;
  }

  function closeMobileNav() {
    if (!isMobileNav()) return;

    var $toggle = $('.navigation-toggle[data-target="#navbar-1"]');
    var $target = $('#navbar-1');

    if ($target.length) {
      $target.hide();
    }

    if ($toggle.length) {
      $toggle.removeClass('navigation-toggle-show');
    }
  }

  $('a[href*=#]:not([href=#])').click(function() {
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
      if (target.length) {
        $('html,body').animate({
          scrollTop: target.offset().top
        }, 1000);

        closeMobileNav();
        return false;
      }
    }
  });

  $('.item-nav a').on('click', function() {
    closeMobileNav();
  });

  $(document).on('click', function(e) {
    if (!isMobileNav()) return;
    if ($(e.target).closest('.main-nav').length) return;
    closeMobileNav();
  });

  $(document).on('keydown', function(e) {
    if (e.key === 'Escape') {
      closeMobileNav();
    }
  });
});