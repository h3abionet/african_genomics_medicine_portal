$(document).ready(function () {
  $("input[name='search_type_check']").change(function () {
    // define array to hold selected category types
    let cats = [];
    let placeholder;
    // on category (remember its a checkbox) change
    // push the selected category value into the category array
    $.each($("input[name='search_type_check']:checked"), function () {
      cats.push($(this).val());
    });
    // disable search button on empty categories selected
    if (cats.length < 1) {
      $(".search-btn").attr("disabled", true);
    } else {
      $(".search-btn").attr("disabled", false);
    }
    // updatePlaceholder(cats);
    if (cats.length == 0) {
      placeholder = '';
    } else {
      placeholder = 'Enter ' + cats.join(', ') + ' separated by double colon (::)';
    }
    $("input[type=text], #search").attr('placeholder', placeholder);
  });
  $("#search-form").submit(function (event) {
    event.preventDefault();
    // console.log('sddsd');
  });

  $("#pharmgkb-btn").click(function () {
    let item_id = 123;
    window.location.href = '/search_details/pharmgkb/' + item_id;
  });
  $("#gwascatalog-btn").click(function () {
    let item_id = 321;
    window.location.href = '/search_details/gwascatalog/' + item_id;
  });
});
