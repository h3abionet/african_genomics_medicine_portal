$(document).ready(function () {
  let cats;
  $("input[type=text], #search-input").val('');
  $("input[type=text], #search-input").focus();

  $( "#search-input" ).autocomplete({
    source: function( request, response ) {
      $.ajax({
        url: "/agnocomplete/Search",
        dataType: "json",
        data: {
          q: request.term
        },
        success: function( data ) {
          // console.log(data);
          response( data.data );
          // response( data.response.docs );
        }
      });
    },
    minLength: 3
  });
  
  // disable form input when text is empty
  let search_input = $("input[type=text], #search-input");
  $("#search-form,.search-btn").attr("disabled", true);
  search_input.on('input', function(){
    // disable search button on empty categories selected
    if (search_input.val() === "") {
      $("#search-form,.search-btn").attr("disabled", true);
    } else {
      $("#search-form,.search-btn").attr("disabled", false);
    }
  });

  //  check for selected categories and do a bunch of stuff
  $("input[name='search_type_check']").change(function () {
    // define array to hold selected category types
    cats = [];
    eg = {
      drug: ' eg. Warfarin',
      disease: ' eg. Malaria',
      "SNP ID": ' eg. rs28371685',
      gene: ' eg. CFH'
    };
    let placeholder;
    // on category (remember its a checkbox) change
    // push the selected category value into the category array
    $.each($("input[name='search_type_check']:checked"), function () {
      cats.push($(this).val());
    });
    // updatePlaceholder(cats);
    // if no categories are selected, show nothing
    if (cats.length == 0) {
      placeholder = '';
    } else {
      // if you have only one category, 
      // don't add the separation instructions
      let splitText;
      if (cats.length === 1) {splitText = '' + eg[cats[0]];} else {splitText= ' separated by double colon (::)';}
      placeholder = 'Enter ' + cats.join(', ') + splitText;
    }
    $("input[type=text], #search-input").attr('placeholder', placeholder);
  });

  $("#search-form").submit(function (event) {
    event.preventDefault();
    // get search input and query db
    let query_string = $("input[type=text], #search-input").val();
    // empty results
    // $('#results').empty();
    let query_array = [];
    cats = (cats == undefined) ? [] : cats;
    for (let idx = 0; idx < cats.length; idx++) {
      const cat = cats[idx];
      if(cat === 'disease'){
        query_array.push(cat + '=1');
      }else if(cat === 'drug'){
        query_array.push(cat + '=1');
      }else if(cat === 'SNP ID'){
        query_array.push('variant=1');
      }else if(cat === 'gene'){
        query_array.push(cat + '=1');
      }
    }
    query_params = (cats != undefined && cats.length>0) ? '?'+ query_array.join('&') : '?disease=1&drug=1&variant=1&gene=1';
    let URL = '/search/' + query_string + query_params;
    
    $.ajax({
      url: URL,
      dataType: "json",
      success: function (data) {
        console.log(data);
        $('#results').empty();
        for (let i = 0; i < data.length; i++) {
          let name = '', head = '';
          const rec = data[i];
          name = rec.name ? "<h1 class='title'>"+rec.name+"</h1></a>" : '';
          rec.detail.forEach(el => {
            head += "<h2 class='snippet'>"+el+"</h2>";
          });
          // gedg = (rec.key == 'dg')||(rec.key == 'ge') ? "<a href='/search_details/gene-drug/"+rec.id+"'><h2 class='snippet'>For gene associations click here</h2></a>" : '';
          gedg = (rec.key == 'ds')||(rec.key == 'ge') ? "<a href='/search_details/gene-drug/"+rec.id+"'><h2 class='snippet'>For gene associations click here</h2></a>" : '';
          vtdg = (rec.key == 'dg')||(rec.key == 'vt') ? "<a href='/search_details/variant-drug/"+rec.id+"'><h4 class='snippet'>For variant-drug associations click here</h4></a>" : '';          
          // geds = (rec.key == 'ge')||(rec.key == 'ds') ? "<a href='/search_details/gene-disease/"+rec.id+"'><h4 class='snippet'>For gene-disease associations click here</h4></a>" : '';
          // vtds = (rec.key == 'vt')||(rec.key == 'ds') ? "<a href='/search_details/variant-disease/"+rec.id+"'><h4 class='snippet'>For variant-disease associations click here</h4></a>" : '';

          // results = '' + name;
          $('<div class="list-data"></div>')
            .append(name)
            .append(head)
            .append(gedg)
            .append(vtdg)
            // .append(geds)
            // .append(vtds)
          .appendTo('#results').fadeIn(8000);
        }
        // check for empty results
        if (data.length<1) {
          results = "<h1 class='title'>No results to show</h1>";
          $('<div class="list-data"></div>').append(
            results
          ).appendTo('#results').fadeIn(8000);
        }
      }
    });
  });
});
