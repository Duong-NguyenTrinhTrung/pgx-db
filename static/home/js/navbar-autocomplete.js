
//create new widgets from scratch, using just the $.Widget
//syntax: jQuery.widget( name [, base ], prototype )
$.widget( "custom.catcomplete", $.ui.autocomplete, 
  {
    _create: function() {
      this._super();
      //setting a option in the menu of the widget to only show options that are not of a class of 'ui-autocomplete-category'.
      this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
    },
    //The _renderMenu function is being overridden. This function is responsible for rendering the menu of options that appears when the user starts typing in the input field. The function takes two arguments, ul and items, which are the menu element and the list of options to be rendered, respectively.
    _renderMenu: function( ul, items ) {
      //create a variable that refers to the current context of the widget, so that it can be used inside the $.each function.
      //currentCategory is a variable that keeps track of the current category being rendered in the menu
      var that = this,
        currentCategory = "";
      //iterates over each item in the items array
      $.each( items, function( index, item ) {
        var li;
        //checks if the current item's category is different from the current category being rendered
        if ( item.category != currentCategory ) {
          //adds a new list item to the menu with the class 'ui-autocomplete-category' and the text of the current item's category
          ul.append( "<li class='ui-autocomplete-category'>" + item.category + "</li>" );
          //updates the current category being rendered to be the category of the current item
          currentCategory = item.category;
        }
        //calls the _renderItemData function of the parent widget and passing the ul and the current item as the argument, the _renderItemData function renders the current item in the menu.
        li = that._renderItemData( ul, item );
        //checks if the current item has a category
        if ( item.category ) {
          //adds an 'aria-label' attribute to the current item's list element, with the value being the item's category and label concatenated together with a colon
          li.attr( "aria-label", item.category + " : " + item.label );
        }
      });
    }
  }
  ); //end of widget

  $(function() { 
      redirect_on_select =''
      $("#nav-selection-autocomplete").catcomplete(
        {
          source: "/drug/autocomplete?type_of_selection=navbar",
          minLength: 3,
          autoFocus: true,
          delay: 500,
          create: function(event, ui) { this.focus();return false; },
          focus: function(event, ui) { return false; },
          select: function(event, ui) {
              $( '#selection-autocomplete' ).val('');
              redirect_url = ui.item['redirect']+ui.item['id'];
              setTimeout(function(){window.location = redirect_url;}, 1);
              return false;
          },
          open:function(){
            $(this).catcomplete("widget").css({
              "margin-top": "2px",
              "z-index": "99999",

            });
          },
          // response: function() {
          //   // Apply styles each time the suggestion list is updated
          //   $(this).catcomplete("widget").css({
          //     "margin-top": "30px"
          //   });
          // }
        }).data("custom-catcomplete")._renderItem = function (ul, item) {
          return $("<li></li>")
          .data("item.autocomplete", item)
          .append("<a>" + item.label + "</a>")
          .appendTo(ul);
      };
  });

