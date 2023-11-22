
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

    //selects the input element with the id "nav-selection-autocomplete" and calls the "catcomplete" widget on it. The options for the widget are specified inside the curly braces.
    $("#nav-selection-autocomplete").catcomplete(
      {
        //This line sets the source option of the widget to the given url. The widget will send a GET request to this url with the current input of the user.
        source: "/drug/autocomplete?type_of_selection=navbar",
        minLength: 3,
        autoFocus: true,
        delay: 500,
        //sets the create option of the widget to a function. This function will be called when the widget is created and it will focus on the input element and return false to prevent default behavior.
        create: function(event, ui) { this.focus();return false; },
        //sets the focus option of the widget to a function. This function will be called when an item is focused and it will return false to prevent default behavior.
        focus: function(event, ui) { return false; },
        //sets the select option of the widget to a function. This function will be called when an item is selected.
        select: function(event, ui) {
            $( '#selection-autocomplete' ).val('');
            console.log(ui.item['id'],ui.item['type'],ui.item['label']);
            //This line sets the value of the redirect_url variable to the url '/drug/' concatenated with the drug_bankID property of the selected item.
            redirect_url = ui.item['redirect']+ui.item['id'];
            console.log("drug_bankID: ", ui.item['id']);
            // sets a timeout of 1ms that redirects the user to the redirect_url.
            setTimeout(function(){window.location = redirect_url;}, 1);
            return false;
        }
      }).data("custom-catcomplete")._renderItem = function (ul, item) {
        return $("<li></li>")
        .data("item.autocomplete", item)
        // .data( "ui-autocomplete-item", item )
        .append("<a>" + item.label + "</a>")
        .appendTo(ul);
    };
});

